from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from collections import OrderedDict
from tabulate import tabulate
from util import integer_minus, integer_plus


class StockAction(Enum):
    TRANSFER = "transfer"
    BUY = "buy"
    SELL = "sell"
    SPLIT = "split"
    CANCEL_TRANSFER = "canceled_transfer"


@dataclass
class StockTransaction:
    depot: str
    transaction_id: str
    isin: str
    name: str
    action: str
    execution_date: datetime
    valuation_date: datetime
    count: float
    price: float
    curency: str
    original: dict
    
    def to_dict(self) -> dict:
        return {
            "depot": self.depot,
            "transaction_id": self.transaction_id,
            "isin": self.isin,
            "name": self.name,
            "action": self.action,
            "execution_date": self.execution_date,
            "valuation_date": self.valuation_date,
            "count": self.count,
            "price": self.price,
            "curency": self.curency,
            "original": self.original
        }


@dataclass
class FifoEntry:
    transaction_id: str
    aqusition_date: datetime
    count: float
    price: float


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
                required = 0
                output.append(FifoEntry(self._fifo[0].transaction_id, self._fifo[0].aqusition_date, required, self._fifo[0].price))
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

class Stock:
    def __init__(self, isin:str, name:str, currency:str):
        self.isin = isin
        self.name = name
        self.currency = currency
        self.position = 0.0
        self.price = 0.0
        self.price_date = datetime(1970, 1, 1)
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
        self.fifo.put(FifoEntry(trans.transaction_id, trans.execution_date, trans.count, trans.price))

    def buy(self, trans:StockTransaction):
        self.check(trans, "buy")
        self.position = integer_plus(self.position, trans.count)
        self.price = trans.price
        self.price_date = trans.execution_date
        self.fifo.put(FifoEntry(trans.transaction_id, trans.execution_date, trans.count, trans.price))

    def sell(self, trans:StockTransaction):
        self.check(trans, "sell")
        self.position = integer_minus(self.position, trans.count)
        if self.position < 0:
            raise ValueError(f"Selling more Stock than beeing held! Isin {self.isin} -> transaction {trans.transaction_id}")
        self.price = trans.price
        self.price_date = trans.execution_date
        out = self.fifo.pop(FifoEntry(trans.transaction_id, trans.execution_date, trans.count, trans.price))
        return SaleTransaction(trans, out)

    def split(self, trans:StockTransaction):
        self.check(trans, "split")
        self.position = integer_plus(self.position, trans.count)
        if trans.count < 0:
            out = self.fifo.pop(FifoEntry(trans.transaction_id, trans.execution_date, -trans.count, trans.price))
        else:
            self.fifo.put(FifoEntry(trans.transaction_id, trans.execution_date, trans.count, trans.price))
            self.price = trans.price

    def canceled_transfer(self, trans:StockTransaction):
        self.check(trans, "canceled_transfer")
        self.position = integer_minus(self.position, trans.count)
        self.fifo.undo(FifoEntry(trans.transaction_id, trans.execution_date, trans.count, trans.price))


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


if __name__ == "__main__":
    pass