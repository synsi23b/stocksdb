from mongodb import get_all_depots, get_all_stock_transactions
from stocks import Depot

depots = []
for name in get_all_depots():
    trans = get_all_stock_transactions(name)
    if trans:
        dep = Depot(name)
        for tr in trans:
            dep.exec(tr)
        depots.append(dep)

for dep in depots:
    print("-"*20)
    print(dep.id)
    dep.current_holdings()