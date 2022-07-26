import xmltodict
from datetime import datetime
import requests
from mongodb import insert_many_jpy_rate, get_last_jpy_rate


# first import japan yen exchange rate from european cental bank
# download https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/jpy.xml
# https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-jpy.en.html

jpyecb = requests.get("https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/jpy.xml")
open("jpy_exchange_rate_historical.xml", "wb").write(jpyecb.content)

jpy = None
with open("jpy_exchange_rate_historical.xml") as jpyxml:
    jpy = xmltodict.parse(jpyxml.read())


MINYEAR = datetime(year=2019, month=12, day=31)
try:
    mininsert = get_last_jpy_rate()["date"]
    print(f"Last known jpy rate value {mininsert}")
except:
    print("no mininsert value! Using default")
    mininsert = MINYEAR

dateratelist = []
for dailyrate in jpy["CompactData"]["DataSet"]["Series"]["Obs"]:
    #print(dailyrate)
    date = datetime.strptime(dailyrate["@TIME_PERIOD"], "%Y-%m-%d")
    # ignore very old or existing data
    if date <= mininsert:
        continue
    # build ratelist objects
    dateratelist.append({"date": date, "rate": float(dailyrate["@OBS_VALUE"])})
if dateratelist:
    insert_many_jpy_rate(dateratelist)
else:
    print("no update to euro jpy rate")
    