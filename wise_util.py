from util import to_dt, to_decimal
from csv import DictReader
from mydataclasses import WiseAction, WiseTransaction
from bson import ObjectId


def load_transactions(infile) -> list[dict]:
    with open(infile, "r") as inf:
        # open the file again and assigne the new header
        dr = DictReader(inf, delimiter=",")
        return [x for x in dr]


def fix_values(trs):
    to_dt(trs, "Date", "%d-%m-%Y")
    to_decimal(trs, "Amount", False)
    to_decimal(trs, "Running Balance", False)
    to_decimal(trs, "Exchange Rate", False)
    to_decimal(trs, "Total fees", False)
    return trs


ACTIONS = {
    "Converted" : WiseAction.CONVERSION,
    "Topped up" : WiseAction.TOP_UP,
    "Sent": WiseAction.SEND
}


def decode_action(trs):
    txt = trs["Description"]
    for k, v in ACTIONS.items():
        if txt.startswith(k):
            return v
    raise ValueError(f"Unknown Action Type! {txt}")


def convert(trs, filename:str):
    trs = fix_values(trs)
    action = decode_action(trs)

    examount = to_decimal({"x": "0.0"}, "x", False)
    if action == WiseAction.CONVERSION:
        val = trs["Description"].split()[-2]
        examount = to_decimal({"x": val}, "x", False)


    return WiseTransaction(
        filename,
        trs["Currency"],
        trs["TransferWise ID"],
        action.value,
        trs["Date"],
        trs["Amount"],
        trs["Description"],
        trs["Running Balance"],

        trs["Exchange From"],
        trs["Exchange To"],
        examount,
        trs["Exchange Rate"],

        trs["Payee Name"],
        trs["Payee Account Number"],
        trs["Total fees"],
        trs)
