from mongodb import get_transactions_giro, get_transactions_giro_range, get_eur2jpy_by_date
import freee_util
from decimal import Decimal
from datetime import datetime, timedelta
from mydataclasses import GiroTransaction, GiroAction
import dkb_giro_util
from random import choice
import string

year = 2024
closings_start = datetime(2023, 12, 20)
closings_end = datetime(2024, 7, 2)

################################
# Transfer dkb_giro_1018533461
################################
FREEE_ACCOUNT = "Deutsche Kreditbank AG ドイツの銀行 EUR"
ACCOUNT = "dkb_giro_1018533461"

# cost
COMMUNICATION = ["NTTCOMMUNICATIONS", "NTT COMMUNICATIONS"]
PURCHASE = ["PAYPAL .ZOHOGERMANY ZO", ]
TRAVEL = ["EMIRATES 62347876046"]
# income
EXPORT_SALE = ["TECHNISCHE UNIVERSITÄT DARMSTADT", "LEAP IN TIME GMBH", ]



def normalize(trans:GiroTransaction) -> GiroTransaction:
    if trans.foreign_currency == "JPY":
        return trans
    rate = get_eur2jpy_by_date(trans.execution_date)
    trans.foreign_currency = "JPY"
    trans.foreign_value = (trans.value * rate).to_integral_value()
    return trans


def get_freee_type(trs:GiroTransaction, balance):
    accrual = trs.execution_date
    client = trs.transaction_counterpart
    if trs.action != GiroAction.DEBIT_CARD_PAY_INTL.value:
        remarks = trs.description + f" {trs.value.copy_abs()} EUR @ {get_eur2jpy_by_date(accrual)}"
    else:
        remarks = trs.description
    amount = trs.foreign_value
    if amount > 0:
        func = freee_util.income_private
        if client.upper() in EXPORT_SALE:
            func = freee_util.income_sale_export
    else:
        func = freee_util.expend_private
        if client.upper() in COMMUNICATION:
            func = freee_util.expend_communication
        if client.upper() in TRAVEL:
            func = freee_util.expend_travel
        if client.upper() in PURCHASE:
            func = freee_util.expend_purchase
    return func(accrual, client, FREEE_ACCOUNT, amount.copy_abs(), remarks, balance)


def get_actions_range(frm, to, actionlist):
    return [ normalize(t) for t in get_transactions_giro_range(ACCOUNT, frm, to, actionlist) ]


closings = get_transactions_giro_range(ACCOUNT, closings_start, closings_end, ["closing"])
closings = [ normalize(c) for c in closings ]

running_balance = closings[0].foreign_value
freee_trans = []

loop_start_date = closings[0].execution_date + timedelta(days=1)
for closing in closings[1:]:
    accrual = closing.execution_date

    actiontypes = set(dkb_giro_util.ACTIONS.values())
    actiontypes.remove(GiroAction.CLOSING)
    actiontypes = [ x.value for x in actiontypes ]

    transac = get_actions_range(loop_start_date, accrual, actiontypes)
    for trs in transac:
        value = trs.foreign_value
        print("Balance: ", running_balance, "Transfer: ", value)
        running_balance += value
        freee_trans.append(get_freee_type(trs, running_balance))

    if closing.foreign_value > running_balance:
        # the foreign balance is smaller than the closing balance
        # FX gain to match the closing balance
        diff = closing.foreign_value - running_balance
        running_balance = closing.foreign_value
        freee_trans.append(
            freee_util.income_fx(accrual, "", 
                                 FREEE_ACCOUNT, diff, 
                                 f"Closing quarter with Balance {closing.foreign_value} JPY {closing.value} EUR @ {get_eur2jpy_by_date(accrual)} vs running balance of {running_balance} JPY",
                                 running_balance))
    elif closing.foreign_value < running_balance:
        # the closing balance is smaller the the foreign closing balance
        # incurred an FX loss
        diff = running_balance - closing.foreign_value
        running_balance = closing.foreign_value
        freee_trans.append(
            freee_util.expend_fx(accrual, "", 
                                 FREEE_ACCOUNT, diff, 
                                 f"Closing quarter with Balance {closing.foreign_value} JPY {closing.value} EUR @ {get_eur2jpy_by_date(accrual)} vs running balance of {running_balance} JPY",
                                 running_balance))
        

    loop_start_date = accrual + timedelta(days=1)

print(f"Starting balance: {closings[0].foreign_value} {closings[0].foreign_currency}")
now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
freee_util.make_new_csv(f"mongoexport/giro_transactions_dkb_{year}_{now}.csv", freee_trans)