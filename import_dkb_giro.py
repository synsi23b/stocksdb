from mongodb import upsert_giro_transactions, insert_transactions_infile
from util import convert_to_utf8
import dkb_giro_util

#nfile = "dkb_giro_export_1018533461_01.01.2022_30.01.2023.csv"
utf8f = "dkb_giro_export_1018533461_01.01.2022_30.01.2023_utf8.csv"

#convert_to_utf8(infile, utf8f)
#insert_transactions_infile(utf8f)

transactions = dkb_giro_util.load_transactions(utf8f)
transactions = [dkb_giro_util.convert(x, "dkb_giro_1018533461", utf8f, i) for i, x in enumerate(transactions)]
print(f"Entry count: {len(transactions)}")
upsert_giro_transactions(transactions)

