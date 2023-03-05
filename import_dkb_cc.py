from mongodb import upsert_cc_transactions, insert_transactions_infile
import dkb_util


utf8f = "export_dkb_kredit_4930_9825_21_12_23-23_01_21_v2.csv"
insert_transactions_infile(utf8f)
transactions = dkb_util.load_transactions(utf8f)
transactions = [dkb_util.convert(x, "dkb_kredit_4930_9825", utf8f, i) for i, x in enumerate(transactions)]
print(f"Entry count: {len(transactions)}")
upsert_cc_transactions(transactions)

