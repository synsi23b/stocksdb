from mongodb import upsert_cc_transactions, insert_transactions_infile
import dkb_util
from pathlib import Path
from util import convert_to_utf8

infile = "dkb_credit_4930_9825--2023.csv"

utf8f = str(Path(infile).stem + "_utf8.csv")
convert_to_utf8(infile, utf8f)
#insert_transactions_infile(utf8f)

transactions = dkb_util.load_transactions_cc(utf8f)
transactions = [dkb_util.convert(x, "dkb_kredit_4930_9825", utf8f, i) for i, x in enumerate(transactions)]
print(f"Entry count: {len(transactions)}")
upsert_cc_transactions(transactions)

