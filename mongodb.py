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


if __name__ == "__main__":
    date = get_last_jpy_rate()["date"]
    print(date)