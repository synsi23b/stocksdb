from util import to_dt, to_decimal, to_int, rename_key
from csv import DictReader
from stocks import StockAction, StockTransaction
from mongodb import create_bson_decimal
from bson import ObjectId


def load_transactions(infile):
    with open(infile, "r") as inf:
        dr = DictReader(inf, delimiter=";")
        # read fieldnames and breaking the file pointer
        next(dr)
        # update missing fieldnames
        print("original CSV header: ", dr.fieldnames)
        first, second = None, None
        for i, v in enumerate(dr.fieldnames):
            if v == "":
                if not first:
                    first = (i, "Unit")
                elif not second:
                    second = (i, "Waehrung")
        fnames = dr.fieldnames
        fnames[first[0]] = first[1]
        fnames[second[0]] = second[1]
        dr.fieldnames = fnames
        print("fixed CSV header: ", fnames)
    with open(infile, "r") as inf:
        # open the file again and assigne the new header
        dr = DictReader(inf, delimiter=";")
        dr.fieldnames = fnames
        # ignore the first row because now that is the old header
        next(dr)
        # return the contents as list of dicts
        return [x for x in dr]


def fix_values(trs):
    to_dt(trs, "Buchtag", "%d.%m.%Y")
    to_dt(trs, "Valuta", "%d.%m.%Y")
    to_decimal(trs, "Nominal", True)
    to_decimal(trs, "Kurs", True)
    #to_int(trs, "Nummer")
    #to_int(trs, "TA-Nr.")
    # mongodb cant deal with keys that have a dot
    rename_key(trs, "TA-Nr.", "TA-Nr")
    return trs


ACTIONS = {
    "WP-Eingang" : StockAction.TRANSFER,
    "Ausführung ORDER Kauf" : StockAction.BUY,
    "Ausführung ORDER Verkauf" : StockAction.SELL,
    "Split im Verhältnis" : StockAction.SPLIT,
    "Storno WP-Eingang" : StockAction.CANCEL_TRANSFER,
}


def decode_action(trs):
    txt = trs["Buchungsinformationen"]
    for k, v in ACTIONS.items():
        if txt.startswith(k):
            return v
    raise RuntimeError(f"Unknown Action: {txt}")


def convert(trs):
    trs = fix_values(trs)
    action = decode_action(trs)
    count = trs["Nominal"]
    if action == StockAction.SELL or action == StockAction.CANCEL_TRANSFER:
        count = create_bson_decimal(-count.to_decimal())

    return StockTransaction(
        "flatex_" + trs["Nummer"],
        trs['TA-Nr'],
        trs["ISIN"],
        trs["Bezeichnung"],
        action.value,
        trs["Buchtag"],
        trs["Valuta"],
        count,
        trs["Kurs"],
        trs["Waehrung"],
        trs)
