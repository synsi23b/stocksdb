from mongodb import get_transactions_cc, get_transactions_cc_range, get_eur2jpy_by_date
import freee_util
from decimal import Decimal
from copy import deepcopy
from datetime import datetime, timedelta
from mydataclasses import CCTransaction

year = 2022

################################
# Transfer Settlement DKB CC 9825
################################
starting_date = datetime(year, 1, 1)
starting_balance = Decimal(-132995)
CARD = "dkb_kredit_4930_9825"
CREDITACCOUNT = "DKB Credit Card 9825ドイツのクレジットカード"
balancing = get_transactions_cc(CARD, year, ["balancing"])


def normalize(trans:CCTransaction) -> CCTransaction:
    if trans.foreign_currency == "JPY":
        return trans
    rate = get_eur2jpy_by_date(trans.execution_date)
    trans.foreign_currency = "JPY"
    trans.foreign_value = (trans.value * rate).to_integral_value()
    return trans


def get_actions_range(frm, to, actionlist):
    return [ normalize(t) for t in get_transactions_cc_range(CARD, frm, to, actionlist) ]


balances = []
spending = []
deposits = []
loop_start_date = starting_date
for bal in balancing:
    bal = normalize(bal)
    accrual = bal.execution_date
    if balances:
        balance = Decimal()
    else:
        balance = starting_balance

    for trs in get_actions_range(loop_start_date, accrual, ["pay", "pay_intl"]):
        value = trs.foreign_value
        balance += value
        spending.append(
            freee_util.Expenditure(
            trs.execution_date, trs.description, freee_util.EXP_OWNER_LOAN,
            CREDITACCOUNT, -value, freee_util.TAX_NA, f" {-trs.value} EUR"
            )
        )
    for trs in get_actions_range(loop_start_date, accrual, ["deposit"]):
        value = trs.foreign_value
        balance += value
        deposits.append(freee_util.income_private(
            trs.execution_date, "", CREDITACCOUNT, value, 
            f"{trs.description}  {trs.value} EUR @ {get_eur2jpy_by_date(trs.execution_date)}")
            )

    balances.append(freee_util.Income(
        accrual, "VOELKER JOHANNES STEFAN", freee_util.INC_ONWER_LOAN,
        CREDITACCOUNT, bal.foreign_value, freee_util.TAX_NA,
        bal.description + f" {bal.value} EUR @ {get_eur2jpy_by_date(accrual)}"
    ))
    # balance is guaranteed to be negative, else there would be no balancing event
    # just as the bal-event foreign value is guaranteed to be positive
    diff = bal.foreign_value + balance
    # now the difference is either positive or negative. if it is positive, we incurred an FX-Loss
    # need to record it so that the balance sheet will be zero at this point
    # vice versa for an FX-win
    if diff > Decimal():
        balances.append(freee_util.Expenditure(
            accrual, "", freee_util.EXP_MISC,
            CREDITACCOUNT, diff, freee_util.TAX_NA,
            freee_util.EXP_FX_LOSS
        ))
    if diff < Decimal():
        balances.append(freee_util.Income(
            accrual, "", freee_util.INC_MISC,
            CREDITACCOUNT, -diff, freee_util.TAX_NA,
            freee_util.INC_FX_GAIN
        ))

    loop_start_date = accrual + timedelta(days=1)

fname = f"_dkb_cc_{starting_date.date()}-{accrual.date()}.xlsx"
freee_util.make_xlsx("mongoexport/expend" + fname, spending)
freee_util.make_xlsx("mongoexport/deposit" + fname, deposits)
freee_util.make_xlsx(f"mongoexport/cc_balancing_{year}.xlsx", balances)