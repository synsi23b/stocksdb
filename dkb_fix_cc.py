import re


with open("old_cc_trans.txt", "r") as f:
    data = f.readlines()


currency = ""
exchange_start = -1
def find_currency(line:str):
    global currency
    global exchange_start
    exchange_start = -1
    for cur in ["JPY", "USD"]:
        exchange_start = line.find(cur)
        currency = cur
        if exchange_start != -1:
            break
    if exchange_start == -1:
        raise ValueError(f"No excahnge rate found! {line}")


def fix_date(date:str):
    d = date.split(".")
    return f"{d[0]}.{d[1]}.20{d[2]}"


outlines = []
for line in data:
    sline = line.split()
    booking, valuation = fix_date(sline[0]), fix_date(sline[1])

    eur = sline[-2]
    sign = sline[-1]
    recipent = " ".join(sline[2:-2])
    if sign == "+":
        sign = ""
    mc = re.match(".+?([\d\.]+,[\d\.]+,\d+)",recipent)
    if mc:
        values = mc.group(1).split(",")
        find_currency(recipent)
        original = values[0] + "," + values[1][:2] + " " + currency
        recipent = recipent[0:exchange_start]
        outlines.append(["Ja", valuation, booking, recipent, sign+eur, sign+original])
    else:
        outlines.append(["Ja", valuation, booking, recipent, sign+eur, ""])


with open("export_dkb_kredit_4930_9825.csv", "r") as f:
    existing = f.readlines()


with open("export_dkb_kredit_4930_9825_inc_old.csv", "w") as f:
    f.writelines(existing)
    outlines.reverse()
    for line in outlines:
        ol = ""
        for x in line:
            if "," in x:
                x = f"\"{x}\""
            if ol:
                ol = ol + f",{x}"
            else:
                ol = x
        f.write(f"{ol}\n")