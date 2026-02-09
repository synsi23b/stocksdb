from dotenv import load_dotenv
import pymongo
import os
from mydataclasses import StockTransaction, CCTransaction, GiroTransaction, WiseTransaction
from datetime import datetime, timedelta
from bson import Decimal128, decimal128
import decimal


_db = None
_decimal128_ctx = decimal128.create_decimal128_context()


def get_db():
    global _db
    if _db is None:
        load_dotenv()
        client = pymongo.MongoClient(os.getenv('MONGOCON'))
        _db = client.get_database("finance")
    return _db


def get_decimal_ctx():
    return decimal.localcontext(_decimal128_ctx)


def create_decimal(val) -> decimal:
    with get_decimal_ctx() as c:
        return c.create_decimal(val)
    

def create_bson_decimal(val) -> Decimal128:
    if type(val) == Decimal128:
        return Decimal128(val)
    else:
        return Decimal128(create_decimal(val))


def check_res(res):
    print(res, f"was acknowledged: {res.acknowledged}")


def check_res_uspert(res):
    print(res, f"\nwas acknowledged: {res.acknowledged}\nnMatched: {res.matched_count}\nnUpserted: {res.upserted_count}\nnModified: {res.modified_count}")


def get_last_jpy_rate():
    db = get_db()
    return db["fx_eur2jpy"].find_one(sort=[("date", -1)])


def get_eur2jpy_by_date(date:datetime):
    db = get_db()
    found = db["fx_eur2jpy"].find_one({"date":date})
    if found:
        return found["rate"].to_decimal()
    # maybe weekend, go back one day
    return get_eur2jpy_by_date(date - timedelta(days=1))


def upsert_many_jpy_rate(dateratelist):
    db = get_db()
    ops = [ pymongo.UpdateOne({"date": x["date"]}, {'$set': x}, upsert=True) for x in dateratelist ]
    res = db["fx_eur2jpy"].bulk_write(ops)
    check_res_uspert(res)


def upsert_stock_transactions(stocks_list:list[StockTransaction]):
    db = get_db()
    ops = [ pymongo.UpdateOne({"transaction_id": x.transaction_id}, {'$set': x.to_dict()}, upsert=True) for x in stocks_list ]
    res = db["stock_transactions"].bulk_write(ops)
    check_res_uspert(res)


def upsert_wise_transactions(wise_list:list[WiseTransaction]):
    db = get_db()
    ops = [ pymongo.UpdateOne({"transaction_id": x.transaction_id, "currency": x.currency}, {'$set': x.to_dict()}, upsert=True) for x in wise_list ]
    res = db["wise_transactions"].bulk_write(ops)
    check_res_uspert(res)


def insert_transactions_infile(filename):
    with open(filename, "r") as inf:
        data = inf.read()
    db = get_db()
    db["inputfiles"].insert_one({"_id": filename, "content": data})


def upsert_cc_transactions(cc_list:list[CCTransaction]):
    db = get_db()
    ops = [ pymongo.UpdateOne({"inputfile": x.inputfile, "index": x.index}, {'$set': x.to_dict()}, upsert=True) for x in cc_list ]
    res = db["cc_transactions"].bulk_write(ops)
    check_res_uspert(res)


def upsert_giro_transactions(cc_list:list[GiroTransaction]):
    db = get_db()
    ops = [ pymongo.UpdateOne({"inputfile": x.inputfile, "index": x.index}, {'$set': x.to_dict()}, upsert=True) for x in cc_list ]
    res = db["giro_transactions"].bulk_write(ops)
    check_res_uspert(res)


def get_all_depots():
    db = get_db()
    res = db['stock_transactions'].aggregate([
        {
            '$group': {
                '_id': {
                    'depot': '$depot'
                }
            }
        }])
    return [x["_id"]["depot"] for x in res]


def get_all_stock_transactions(depot:str):
    db = get_db()
    return [StockTransaction(**x) for x in (db["stock_transactions"].find({"depot": depot},{"_id": 0}).sort("transaction_id", 1))]


def get_transactions_wise(currency:str, year:int, action:str):
    db = get_db()
    match = {
        'currency': currency, 
        'action': action,
        '$and': [
            {
                'date': {
                    '$gte': datetime(year, 1, 1)
                }
            }, {
                'date': {
                    '$lte': datetime(year, 12, 31)
                }
            }
        ]
    }
    return [WiseTransaction(**x) for x in (db["wise_transactions"].find(match,{"_id": 0}).sort("date", 1))]


def get_transactions_cc(cardnum:str, year:int, actionlist:list[str]):
    return get_transactions_cc_range(cardnum, datetime(year, 1, 1), datetime(year, 12, 31), actionlist)
    

def get_transactions_cc_range(cardnum:str, frm:datetime, to:datetime, actionlist:list[str]):
    db = get_db()
    match = {
        'cardnum': cardnum, 
        '$and': [
            {
                'execution_date': {
                    '$gte': frm
                }
            }, {
                'execution_date': {
                    '$lte': to
                }
            }
        ]
    }
    if actionlist:
        match["action"] = { "$in" : actionlist }
    res = [CCTransaction(**x) for x in (db["cc_transactions"].find(match,{"_id": 0}).sort("execution_date", 1))]
    for trans in res:
        trans.value = trans.value.to_decimal()
        trans.foreign_value = trans.foreign_value.to_decimal()
    return res


def get_transactions_giro(account:str, year:int, actionlist:list[str]):
    return get_transactions_giro_range(account, datetime(year, 1, 1), datetime(year, 12, 31), actionlist)


def get_transactions_giro_range(account:str, frm:datetime, to:datetime, actionlist:list[str]):
    db = get_db()
    match = {
        'account': account, 
        '$and': [
            {
                'execution_date': {
                    '$gte': frm
                }
            }, {
                'execution_date': {
                    '$lte': to
                }
            }
        ]
    }
    if actionlist:
        match["action"] = { "$in" : actionlist }
    res = [GiroTransaction(**x) for x in (db["giro_transactions"].find(match,{"_id": 0}).sort([("execution_date", 1), ("index", -1)]))]
    for trans in res:
        trans.value = trans.value.to_decimal()
        trans.foreign_value = trans.foreign_value.to_decimal()
    return res


def replace_collection(name, new_objs):
    db = get_db()
    db.drop_collection(name)
    db[name].insert_many(new_objs)


if __name__ == "__main__":
    #date = get_last_jpy_rate()["date"]
    db = get_db()
    #print(db.command({'buildInfo':1})['version'])
    #print(get_all_depots())
    print(get_transactions_wise("EUR", 2022))
