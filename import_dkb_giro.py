from mongodb import upsert_cc_transactions, insert_transactions_infile
from util import convert_to_utf8
import dkb_util

infile = "dkb_giro_export_1018533461_01.08.2020_30.01.2023.csv"
utf8f = "dkb_giro_export_1018533461_01.08.2020_30.01.2023_utf8.csv"

convert_to_utf8("Depotumsaetze.csv", utf8f)
insert_transactions_infile(utf8f)

#transactions = dkb_util.load_transactions(utf8f)
#transactions = [dkb_util.convert(x, "dkb_kredit_4930_9825", utf8f, i) for i, x in enumerate(transactions)]
#print(f"Entry count: {len(transactions)}")
#upsert_cc_transactions(transactions)

