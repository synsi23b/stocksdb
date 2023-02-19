from dataclasses import dataclass
from enum import Enum
from datetime import datetime


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


class CCAction(Enum):
    PAY = "pay"
    PAY_INTL = "pay_intl"
    BALANCING = "balancing"
    DEPOSIT = "deposit"