from mongodb import upsert_stock_transactions, insert_transactions_infile
from util import convert_to_utf8
import flatex_util


def import_flatex():
    utf8f = "depotumsaetze_utf8.csv"
    convert_to_utf8("Depotumsaetze.csv", utf8f)
    insert_transactions_infile(utf8f)
    transactions = flatex_util.load_transactions(utf8f)
    transactions = [flatex_util.convert(x) for x in transactions]
    upsert_stock_transactions(transactions)


if __name__ == "__main__":
    import_flatex()
