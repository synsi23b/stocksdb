from stocks_dataclasses import StockAction, StockTransaction
from dataclasses import dataclass
from datetime import datetime
from collections import OrderedDict
from tabulate import tabulate
from util import integer_minus, integer_plus
import xlsxwriter
from mongodb import get_eur2jpy_by_date


@dataclass
class FifoEntry:
    transaction_id: str
    execution_date: datetime
    valuation_date: datetime
    count: float
    price: float
    action: str


class LoggedFiFo:
    def __init__(self):
        self._fifo = []
        self._log = []

    def put(self, val:FifoEntry):
        self._fifo.append(val)
        self._log.append(f"PUT: {val}")

    def pop(self, val:FifoEntry):
        required = val.count
        self._log.append(f"POP: {val}")
        output = []
        while required > 0:
            if required >= self._fifo[0].count:
                required = integer_minus(required, self._fifo[0].count)
                output.append(self._fifo.pop(0))
                self._log.append(f" -> FULL {output[-1]}")
            else:
                # required < fifo[0].count
                self._fifo[0].count = integer_minus(self._fifo[0].count, required)
                output.append(FifoEntry(self._fifo[0].transaction_id, self._fifo[0].execution_date, self._fifo[0].valuation_date, required, self._fifo[0].price, self._fifo[0].action))
                required = 0
                self._log.append(f" -> PART {output[-1]}")
        return output

    def undo(self, val:FifoEntry):
        if self._fifo[-1].count != val.count:
            raise ValueError("Undo fifo not directly after the fact. Needs better implementation")
        self._fifo.pop()
        self._log.append(f"UNDO: {val}")


@dataclass
class SaleTransaction:
    transaction: StockTransaction
    parts: list

    def average_cost(self):
        total_count = 0.0
        total_cost = 0.0
        for p in self.parts:
            total_count += p.count
            total_cost += p.count * p.price
        return total_cost / total_count
    
    def cost(self):
        total_cost = 0.0
        for p in self.parts:
            total_cost += p.count * p.price
        return total_cost

    def cost_jpy(self):
        total_cost = 0.0
        for p in self.parts:
            rate = get_eur2jpy_by_date(p.valuation_date)
            total_cost += round(p.count * p.price * rate)
        return total_cost


class Stock:
    def __init__(self, isin:str, name:str, currency:str):
        self.isin = isin
        self.name = name
        self.currency = currency
        self.position = 0.0
        self.price = 0.0
        self.price_date = datetime(1970, 1, 1)
        self.valuation_date = datetime(1970, 1, 1)
        self.fifo = LoggedFiFo()
        self.transactions = OrderedDict()

    def check(self, trans:StockTransaction, action:str):
        if trans.transaction_id in self.transactions:
            raise ValueError(f"Transaction {trans.transaction_id} already applied to Stock FiFo")
        if trans.isin != self.isin:
            raise ValueError(f"Attempt to add transaction to wrong FiFo {trans.isin} != {self.isin}")
        if trans.action != action:
            raise ValueError(f"Transaction and FiFo action mismatch for transaction number: {trans.transaction_id}")
        if trans.curency != self.currency:
            raise ValueError(f"Currency missmatch for transaction number: {trans.transaction_id}")
        self.transactions[trans.transaction_id] = trans

    def transfer(self, trans:StockTransaction):
        self.check(trans, "transfer")
        self.position = integer_plus(self.position, trans.count) 
        self.price = trans.price
        self.price_date = trans.execution_date
        self.valuation_date = trans.valuation_date
        self.fifo.put(FifoEntry(trans.transaction_id, trans.execution_date, trans.valuation_date, trans.count, trans.price, trans.action))

    def buy(self, trans:StockTransaction):
        self.check(trans, "buy")
        self.position = integer_plus(self.position, trans.count)
        self.price = trans.price
        self.price_date = trans.execution_date
        self.valuation_date = trans.valuation_date
        self.fifo.put(FifoEntry(trans.transaction_id, trans.execution_date, trans.valuation_date, trans.count, trans.price, trans.action))

    def sell(self, trans:StockTransaction):
        self.check(trans, "sell")
        self.position = integer_minus(self.position, trans.count)
        if self.position < 0:
            raise ValueError(f"Selling more Stock than beeing held! Isin {self.isin} -> transaction {trans.transaction_id}")
        self.price = trans.price
        self.price_date = trans.execution_date
        self.valuation_date = trans.valuation_date
        out = self.fifo.pop(FifoEntry(trans.transaction_id, trans.execution_date, trans.valuation_date, trans.count, trans.price, trans.action))
        return SaleTransaction(trans, out)

    def split(self, trans:StockTransaction):
        self.check(trans, "split")
        self.position = integer_plus(self.position, trans.count)
        if trans.count < 0:
            out = self.fifo.pop(FifoEntry(trans.transaction_id, trans.execution_date, trans.valuation_date, -trans.count, trans.price, trans.action))
        else:
            self.fifo.put(FifoEntry(trans.transaction_id, trans.execution_date, trans.valuation_date, trans.count, trans.price, trans.action))
            self.price = trans.price

    def canceled_transfer(self, trans:StockTransaction):
        self.check(trans, "canceled_transfer")
        self.position = integer_minus(self.position, trans.count)
        self.fifo.undo(FifoEntry(trans.transaction_id, trans.execution_date, trans.valuation_date, trans.count, trans.price, trans.action))


class Depot:
    def __init__(self, id:str):
        self.id = id
        self.stocks = {}
        self.transactions = OrderedDict()
        self.sales = []

    def exec(self, trans:StockTransaction):
        if trans.transaction_id in self.transactions:
            raise ValueError(f"Transaction {trans.transaction_id} already applied to depot {self.id}")
        self.transactions[trans.transaction_id] = trans
        if trans.isin not in self.stocks:
            self.stocks[trans.isin] = Stock(trans.isin, trans.name, trans.curency)
        func = Stock.__dict__[trans.action]
        ret = func(self.stocks[trans.isin], trans)
        if ret is not None:
            self.sales.append(ret)
            
    def current_holdings(self):
        table = []
        for k, v in self.stocks.items():
            if v.position > 0:
                table.append([k, v.name, v.position])
        print(tabulate(table, ["ISIN", "Name", "Position"]))

    def win_los_simple(self, year=None):
        profit = 0.0
        table = []
        for s in self.sales:
            trs = s.transaction
            if year and trs.valuation_date.year != year:
                continue
            avgc = s.average_cost()
            winlose = (trs.price - avgc) * trs.count
            profit += winlose
            table.append([trs.valuation_date, trs.name, trs.count, trs.price, avgc, f"{winlose:.3f}"])
        print(tabulate(table, ["Valuta", "Name", "Count", "Price", "Avg Cost", "Result"]))
        print(f"Overall Profit: {profit:.3f}")

    def sales_jpy_by_year(self, year:int):
        wb = xlsxwriter.Workbook(f'stock_sales_{self.id}_year_{year}.xlsx')
        sheet = wb.add_worksheet("sales")
        row = 0
        for sale in self.sales:
            row = self._write_sale_row(sheet, row, sale) + 2
        wb.close()


    def _write_sale_row(self, sheet:xlsxwriter.Workbook.worksheet_class, row:int, sale:SaleTransaction):
        headers = [
            "ISIN", "Name", "Transacion", "Booking Date", "Valuation Date", "Exchange Rate", 
            "Action", "Count", "Price EUR", "Price YEN", "Total EUR", "Total YEN",
            "Cost EUR", "Cost YEN", "Sales Result EUR", "Sales Result YEN"
            ]
        sheet.write_row(row, 0, headers)
        tr = sale.transaction
        rate = get_eur2jpy_by_date(tr.valuation_date)
        cost = sale.cost()
        cost_jpy = sale.cost_jpy()
        total = tr.count * tr.price
        result = total - cost
        result_jpy = round(total * rate - cost_jpy)
        data = [
            tr.isin, tr.name, tr.transaction_id, tr.execution_date, tr.valuation_date, rate,
            tr.action, tr.count, tr.price, round(tr.price * rate), total, round(total * rate),
            cost, cost_jpy, result, result_jpy
            ]
        row += 1
        sheet.write_row(row, 0, data)
        for p in sale.parts:
            #p = FifoEntry
            rate = get_eur2jpy_by_date(p.valuation_date)
            data = [
                "", "", p.transaction_id, p.execution_date, p.valuation_date, rate,
                p.action, p.count, p.price, round(p.price * rate), p.count * p.price, round(p.count * p.price * rate)
            ]
            row += 1
            sheet.write_row(row, 0, data)
        return row


if __name__ == "__main__":
    pass