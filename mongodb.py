from dotenv import load_dotenv
import pymongo
import os


_db = None


def get_db():
    global _db
    if _db is None:
        load_dotenv()
        client = pymongo.MongoClient(os.getenv('MONGOCON'))
        _db = client.get_database("stocksdb")
    return _db


def check_res(res):
    print(res, f"was acknowledged: {res.acknowledged}")


def get_last_jpy_rate():
    db = get_db()
    return db["eur2jpy"].find_one(sort=[("date", -1)])


def insert_many_jpy_rate(dateratelist):
    db = get_db()
    db.create_collection("eur2jpy", timeseries={
                "timeField": "date",
                "granularity": "hours"
            })
    check_res(db["eur2jpy"].insert_many(dateratelist))


def upsert_stock_transactions(key, stocks_list):
    db = get_db()
    ops = [ pymongo.UpdateOne({key: x[key]}, {'$set': x}, upsert=True) for x in stocks_list ]
    res = db["transactions"].bulk_write(ops)
    print(res)


def get_all_transactions():
    db = get_db()
    return list(db["transactions"].find().sort("TA-Nr", 1))


def replace_collection(name, new_objs):
    db = get_db()
    db.drop_collection(name)
    db[name].insert_many(new_objs)


if __name__ == "__main__":
    date = get_last_jpy_rate()["date"]
    print(date)