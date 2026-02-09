from mongodb import upsert_giro_transactions, insert_transactions_infile
from util import convert_to_utf8
import dkb_giro_util
from pathlib import Path

infile = "dkb_giro_export_1018533461_01.01.2022_30.01.2023.csv"
infile = "dkb_giro_export_1018533461_01.02.2023_02.03.2023.csv"
infile = "dkb_giro_export_1018533461_01.01.2023_03.04.2023.csv"
infile = "dkb_giro_1018533461_2023_4_2023_12.csv"
infile = "dkb_giro_2024_1_6.csv"
infile = "dkb_giro_export_2024-7_2025-1_Umsatzliste_Girokonto_DE13120300001018533461.csv"
infile = "05-02-2026_Umsatzliste_Girokonto_DE13120300001018533461 (1).csv"
utf8f = str(Path(infile).stem + "_utf8.csv")

convert_to_utf8(infile, utf8f, 'utf-8-sig')


transactions = dkb_giro_util.load_transactions(utf8f)
transactions = [dkb_giro_util.convert(x, "dkb_giro_1018533461", utf8f, i) for i, x in enumerate(transactions)]
print(f"Entry count: {len(transactions)}")
insert_transactions_infile(utf8f)
upsert_giro_transactions(transactions)

