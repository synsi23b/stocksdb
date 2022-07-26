from mongodb import get_all_transactions, replace_collection
import util


trans = get_all_transactions()
#print(trans)

depot = {}

def update_held(trs):
    isin = trs["ISIN"]
    if isin not in depot:
        stock = util.make_new_stock_flatex(trs)
        depot[isin] = stock
        return
    stock = depot[isin]
    util.update_flatex(stock, trs)
    

for trs in trans:
    update_held(trs)

print(depot)