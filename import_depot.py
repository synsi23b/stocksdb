import codecs
from csv import DictReader
from mongodb import upsert_stock_transactions
from datetime import datetime


BLOCKSIZE = 1048576 # or some other, desired size in bytes
with codecs.open("Depotumsaetze.csv", "r", "cp1252") as sourceFile:
    with codecs.open("Depotumsaetzeutf8.csv", "w", "utf-8") as targetFile:
        while True:
            contents = sourceFile.read(BLOCKSIZE)
            if not contents:
                break
            targetFile.write(contents)


with open("Depotumsaetzeutf8.csv", "r") as inf:
    dr = DictReader(inf, delimiter=";")
    # read fieldnames
    next(dr)
    # update missing fieldnames
    print(dr.fieldnames)
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
    print(dr.fieldnames)
    transi = [x for x in dr]
#print(transi)
# update values to be usable easily
def to_dt(trs, key):
    trs[key] = datetime.strptime(trs[key], "%d.%m.%Y")

def to_flt(trs, key):
    trs[key] = float(trs[key].replace(",", "."))

def to_int(trs, key):
    trs[key] = int(trs[key])

def rename_key(trs, src, dst):
    trs[dst] = trs[src]
    del trs[src]

def fix_values(trs):
    to_dt(trs, "Buchtag")
    to_dt(trs, "Valuta")
    to_flt(trs, "Nominal")
    to_flt(trs, "Kurs")
    to_int(trs, "Nummer")
    to_int(trs, "TA-Nr.")
    rename_key(trs, "TA-Nr.", "TA-Nr")
    return trs

transi = [ fix_values(x) for x in transi ]
upsert_stock_transactions("TA-Nr", transi)