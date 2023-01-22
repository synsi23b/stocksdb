from mongodb import get_all_depots, get_all_stock_transactions
from stocks import Depot

for name in get_all_depots():
    trans = get_all_stock_transactions(name)
    if trans:
        dep = Depot(name)
        for tr in trans:
            dep.exec(tr)
        print("-"*20)
        print(dep.id)
        #dep.current_holdings()
        #dep.win_los_simple(2022)
        dep.sales_jpy_by_year(2022)

