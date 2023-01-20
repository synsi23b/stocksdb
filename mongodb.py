from dotenv import load_dotenv
import pymongo
import os
import stocks


_db = None


def get_db():
    global _db
    if _db is None:
        load_dotenv()
        client = pymongo.MongoClient(os.getenv('MONGOCON'))
        _db = client.get_database("finance")
    return _db


def check_res(res):
    print(res, f"was acknowledged: {res.acknowledged}")


def get_last_jpy_rate():
    db = get_db()
    return db["fx_eur2jpy"].find_one(sort=[("date", -1)])


def insert_many_jpy_rate(dateratelist):
    db = get_db()
    check_res(db["fx_eur2jpy"].insert_many(dateratelist))


def upsert_stock_transactions(stocks_list:list[stocks.StockTransaction]):
    db = get_db()
    ops = [ pymongo.UpdateOne({"transaction_id": x.transaction_id}, {'$set': x.to_dict()}, upsert=True) for x in stocks_list ]
    res = db["stock_transactions"].bulk_write(ops)
    check_res(res)


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
    return [stocks.StockTransaction(**x) for x in (db["stock_transactions"].find({"depot": depot},{"_id": 0}).sort("transaction_id", 1))]


def replace_collection(name, new_objs):
    db = get_db()
    db.drop_collection(name)
    db[name].insert_many(new_objs)


if __name__ == "__main__":
    #date = get_last_jpy_rate()["date"]
    db = get_db()
    #print(db.command({'buildInfo':1})['version'])
    print(get_all_depots())
