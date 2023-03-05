from mongodb import get_transactions_wise, get_eur2jpy_by_date
import freee_util
from decimal import Decimal
from copy import deepcopy

year = 2022

################################
# Transfer DKB to WISE
################################
trans = get_transactions_wise("EUR", year, "top_up")

# debit = RECEIVER
debit = freee_util.TransferDetail(
    "Wise Europe SA 両替 EUR",
    "",
    Decimal(),
    freee_util.TAX_NA,
    Decimal())

# credit = SENDER
credit = freee_util.TransferDetail(
    "Deutsche Kreditbank AG ドイツの銀行 EUR",
    "",
    Decimal(),
    freee_util.TAX_NA,
    Decimal())

freetrans = []
for t in trans:
    debit.item = t.transaction_id
    rate = get_eur2jpy_by_date(t.date)
    debit.amount = (t.amount.to_decimal() * rate).to_integral_value()
    credit.amount = debit.amount

    tr = freee_util.Transfer(t.date, debit, credit, t.description + f" {t.amount}EUR @ {rate}")
    freetrans.append(deepcopy(tr))

freee_util.make_xlsx(f"mongoexport/transfer_dkb_wise_{year}.xlsx", freetrans)



################################
# Transfer Wise EUR to Wise YEN
################################
trans = get_transactions_wise("EUR", year, "conversion")

# debit = RECEIVER
debit = freee_util.TransferDetail(
    "Wise Europe SA 両替 JPY",
    "",
    Decimal(),
    freee_util.TAX_NA,
    Decimal())

# credit = SENDER
credit = freee_util.TransferDetail(
    "Wise Europe SA 両替 EUR",
    "",
    Decimal(),
    freee_util.TAX_NA,
    Decimal())

freetrans = []
transfees = []
for t in trans:
    credit.item = t.transaction_id
    debit.item = t.transaction_id
    
    credit.amount = t.examount.to_decimal()
    debit.amount = t.examount.to_decimal()
    fee = (t.fees.to_decimal() * t.rate.to_decimal()).to_integral_value()

    tr = freee_util.Transfer(t.date, debit, credit, t.description + f" @ Rate {t.rate.to_decimal()} Fee {fee} YEN")
    freetrans.append(deepcopy(tr))
    transfees.append(freee_util.Expenditure(
        t.date,
        "Wise Europe SA",
        freee_util.EXP_COMMISSION_PAID,
        credit.account,
        fee,
        freee_util.TAX_NA,
        f"{t.transaction_id} fee"))

freee_util.make_xlsx(f"mongoexport/transfer_wise_eur_to_yen_{year}.xlsx", freetrans)
freee_util.make_xlsx(f"mongoexport/expense_wise_eur_to_yen_fees_{year}.xlsx", transfees)
