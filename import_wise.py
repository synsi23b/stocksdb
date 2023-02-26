from mongodb import upsert_wise_transactions, insert_transactions_infile
import wise_util


#utf8f = "statement_30717571_JPY_2022-01-01_2022-12-31 (1).csv"
utf8f = "statement_22172923_EUR_2022-01-01_2022-12-31 (2).csv"
insert_transactions_infile(utf8f)
transactions = wise_util.load_transactions(utf8f)
transactions = [wise_util.convert(x, utf8f) for x in transactions]
print(f"Entry count: {len(transactions)}")
upsert_wise_transactions(transactions)