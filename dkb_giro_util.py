from util import to_dt, to_decimal
from csv import DictReader
from mydataclasses import GiroAction, GiroTransaction
import re


def load_transactions(infile) -> list[dict]:
    with open(infile, "r") as inf:
        # ignore header
        for x in range(6):
            inf.readline()
        # open the file again and assigne the new header
        dr = DictReader(inf, delimiter=";")
        return [x for x in dr]


def fix_values(trs):
    to_dt(trs, "Buchungstag", "%d.%m.%Y")
    to_dt(trs, "Wertstellung", "%d.%m.%Y")
    to_decimal(trs, "Betrag (EUR)", True)
    #to_int(trs, "Nummer")
    #to_int(trs, "TA-Nr.")
    # mongodb cant deal with keys that have a dot
    #rename_key(trs, "TA-Nr.", "TA-Nr")
    return trs


ACTIONS = {
    "": GiroAction.CC_BALANCING,
    "Gutschrift": GiroAction.TRANSFER_IN,
    "Dauerauftrag": GiroAction.TRANSFER_OUT,
    "Überweisung": GiroAction.TRANSFER_OUT,
    "autom.Kartenentgelt": GiroAction.TRANSFER_OUT,
    "Lastschrift": GiroAction.TRANSFER_OUT,
    "Abschluss": GiroAction.CLOSING,
    "Online-Zahlung": GiroAction.DEBIT_CARD_PAY,
    "Kartenzahlung": GiroAction.DEBIT_CARD_PAY,
    "FAKE_ENTRY_TO_GET_THIS_IN_LIST": GiroAction.DEBIT_CARD_PAY_INTL
}


INTL_PATTERN = re.compile("Original\s[\d,]+?\s[A-Z]{3}\s1\sEuro=[\d,]+?\s[A-Z]{3}")

def decode_action(trs):
    txt = trs["Buchungstext"]
    act = None
    for k, v in ACTIONS.items():
        if txt == k:
            act = v
            break
    if act == GiroAction.DEBIT_CARD_PAY:
        if INTL_PATTERN.findall(trs["Verwendungszweck"]):
            return GiroAction.DEBIT_CARD_PAY_INTL
    if act is None:
        pass
    return act


INTL_VAL_CUR_PATTERN = re.compile(".+?Original\s([\d,]+?)\s([A-Z]{3})\s1\sEuro=\w+")
CLOSING_VAL_PATTERN = re.compile(".+?([\d.,]+)\s([+-])Rechnungsnummer")

def convert(trs, acc_name:str, filename:str, index:int):
    trs = fix_values(trs)
    action = decode_action(trs)

    foreign_currency = ""
    dic = {"x": "0.0"}
    to_decimal(dic, "x", False)
    if action == GiroAction.DEBIT_CARD_PAY_INTL:
        mc = INTL_VAL_CUR_PATTERN.match(trs["Verwendungszweck"])
        if trs["Betrag (EUR)"].to_decimal() < 0:
            dic["x"] = "-" + mc.group(1)
        else:
            dic["x"] = mc.group(1)
        foreign_currency = mc.group(2)
        to_decimal(dic, "x", True)
    foreign_value = dic["x"]
    if action == GiroAction.CLOSING:
        mc = CLOSING_VAL_PATTERN.match(trs["Verwendungszweck"])
        dic["x"] = mc.group(2) + mc.group(1)
        trs["Betrag (EUR)"] = to_decimal(dic, "x", True)
    
    return GiroTransaction(
        filename,
        index,
        acc_name,
        action.value,
        trs["Auftraggeber / Begünstigter"],
        trs["Kontonummer"],
        trs["BLZ"],
        trs["Verwendungszweck"],
        trs["Buchungstag"],
        trs["Wertstellung"],
        trs["Betrag (EUR)"],
        "EUR",
        foreign_value,
        foreign_currency,
        trs)
