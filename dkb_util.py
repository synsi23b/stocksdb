from util import to_dt, to_decimal
from csv import DictReader
from mydataclasses import CCAction, CCTransaction
from bson import ObjectId


def load_transactions(infile) -> list[dict]:
    # with open(infile, "r") as inf:
    #     dr = DictReader(inf, delimiter=",")
    #     # read fieldnames and breaking the file pointer
    #     next(dr)
    #     # update missing fieldnames
    #     print("original CSV header: ", dr.fieldnames)
    #     first, second = None, None
    #     for i, v in enumerate(dr.fieldnames):
    #         if v == "":
    #             if not first:
    #                 first = (i, "Unit")
    #             elif not second:
    #                 second = (i, "Waehrung")
    #     fnames = dr.fieldnames
    #     fnames[first[0]] = first[1]
    #     fnames[second[0]] = second[1]
    #     dr.fieldnames = fnames
    #     print("fixed CSV header: ", fnames)
    with open(infile, "r") as inf:
        # open the file again and assigne the new header
        dr = DictReader(inf, delimiter=",")
        # dr.fieldnames = fnames
        # ignore the first row because now that is the old header
        # next(dr)
        # return the contents as list of dicts
        return [x for x in dr]


def fix_values(trs):
    to_dt(trs, "Wertstellung", "%d.%m.%Y")
    to_dt(trs, "Belegdatum", "%d.%m.%Y")
    to_decimal(trs, "Betrag (EUR)", True)
    #to_int(trs, "Nummer")
    #to_int(trs, "TA-Nr.")
    # mongodb cant deal with keys that have a dot
    #rename_key(trs, "TA-Nr.", "TA-Nr")
    return trs


ACTIONS = {
    "Ausgleich Kreditkarte gem. Abrechnung" : CCAction.BALANCING,
    "Einzahlung" : CCAction.DEPOSIT,
}


def decode_action(trs):
    txt = trs["Beschreibung"]
    for k, v in ACTIONS.items():
        if txt.startswith(k):
            return v
    if trs["Ursprünglicher Betrag"]:
        return CCAction.PAY_INTL
    return CCAction.PAY


def convert(trs, card_name:str, filename:str, index:int):
    trs = fix_values(trs)
    action = decode_action(trs)

    urs = trs["Ursprünglicher Betrag"]
    foreign_currency = ""
    dic = {"x": "0.0"}
    to_decimal(dic, "x", False)
    if urs:
        dic["x"], foreign_currency = urs.split(" ")
        to_decimal(dic, "x", True)
    foreign_value = dic["x"]
    
    return CCTransaction(
        filename,
        index,
        card_name,
        action.value,
        trs["Beschreibung"],
        trs["Belegdatum"],
        trs["Wertstellung"],
        trs["Betrag (EUR)"],
        "EUR",
        foreign_value,
        foreign_currency,
        trs)
