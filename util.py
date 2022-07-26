
ACTIONS = [
    ("WP-Eingang", "TRANSFER"),
    ("Ausführung ORDER Kauf", "BUY"),
    ("Ausführung ORDER Verkauf", "SELL"),
    ("Split im Verhältnis", "SPLIT"),
    ("Storno WP-Eingang", "CLR_TRANSFER"),
]
ACTION_TRANSFER=ACTIONS[0]
ACTION_BUY=ACTIONS[1]
ACTION_SELL=ACTIONS[2]
ACTION_SPLIT=ACTIONS[3]
ACTION_CLR_TRANSFER=ACTIONS[4]


def decode_action_flatex(trs):
    txt = str(trs["Buchungsinformationen"])
    for sv in ACTIONS:
        if txt.startswith(sv[0]):
            return sv
    raise RuntimeError(f"Unknown Action: {txt}")


def make_new_stock_flatex(trs):
    act = decode_action_flatex(trs)
    if act is ACTION_BUY or act is ACTION_TRANSFER:
        print("Create new: ", trs["Bezeichnung"])
        cost = trs["Nominal"] * trs["Kurs"]
        return {
            "isin" : trs["ISIN"],
            "name" : trs["Bezeichnung"],
            "count": trs["Nominal"],
            "last_price": trs["Kurs"],
            "cost": cost,
            "earnings": [],
            "last_change": trs["Valuta"],
            "history": [trs],
            "fifo": [(trs["Nominal"], trs["Kurs"], cost)]
        }
    raise RuntimeError(f"Attempt to create stock from Action: {act}")


def increase_flatex(stock, trs):
    number, price = trs["Nominal"], trs["Kurs"]
    cost = number * price
    stock["fifo"].append((number, price, cost))
    stock["cost"] += cost
    stock["count"] += number


def decrease_flatex(stock, trs):
    number, price = -trs["Nominal"], trs["Kurs"]
    cost = number * price
    stock["count"] -= number
    fifo = stock["fifo"]
    aqic = 0.0
    while number > 0.0:
        num, pr, cs = fifo.pop(0)
        remain = num - number
        if remain == 0.0:
            # complete sale
            aqic += cs
            number = 0.0
        elif remain > 0.0:
            # first position bigger than sale
            aqic += number * pr
            number = 0.0
            fifo.insert(0, (remain, pr, remain * pr))
        elif remain < 0.0:
            # first position smaller than sale
            aqic += cs
            number = -remain
    print(f"SALE  {aqic} ->  {cost}")


def clr_trans_flatex(stock, trs):
    number, price = -trs["Nominal"], trs["Kurs"]
    cost = number * price
    fifo = stock["fifo"]
    if fifo[-1] == (number, price, cost):
        fifo.pop()
    else:
        raise RuntimeError("Last in FIFO not fitting CLR IMPORT")
    stock["count"] -= number


update_handlers_flatex = {
    ACTION_TRANSFER : increase_flatex,
    ACTION_BUY : increase_flatex,
    ACTION_SELL : decrease_flatex,
    ACTION_CLR_TRANSFER : clr_trans_flatex
}


def update_flatex(stock, trs):
    act = decode_action_flatex(trs)
    stock["history"].append(trs)
    stock["last_change"] = trs["Valuta"]
    stock["last_price"] = trs["Kurs"]
    update_handlers_flatex[act](stock, trs)
    #stock["cost"] += trs["Nominal"] * trs["Kurs"]
    #stock["count"] += trs["Nominal"]
