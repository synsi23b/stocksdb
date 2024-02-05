from mongodb import replace_collection
import pymongo

old_con = "mongodb://blablabla:blablasecret@192.168.178.250:27018/"
client = pymongo.MongoClient(old_con)
olddb = client.get_database("finance")

collections = [
    "cc_transactions",
    "fx_eur2jpy",
    "giro_transactions",
    "inputfiles",
    "stock_transactions",
    "wise_transactions"
]

for col in collections:
    objs = olddb[col].find({})
    objs = list(objs)
    replace_collection(col, objs)