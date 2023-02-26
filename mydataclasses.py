from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from decimal import Decimal

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
    count: Decimal
    price: Decimal
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


@dataclass
class CCTransaction:
    inputfile: str
    index: int
    cardnum: str
    action: str
    description: str
    execution_date: datetime
    valuation_date: datetime
    value: Decimal
    curency: str
    foreign_value: Decimal
    foreign_currency: str
    original: dict

    def to_dict(self) -> dict:
        return {
            "inputfile": self.inputfile,
            "index": self.index,
            "cardnum": self.cardnum,
            "action": self.action,
            "description": self.description,
            "execution_date": self.execution_date,
            "valuation_date": self.valuation_date,
            "value": self.value,
            "curency": self.curency,
            "foreign_value": self.foreign_value,
            "foreign_currency": self.foreign_currency,
            "original": self.original
        }


class WiseAction(Enum):
    CONVERSION = "conversion"
    TOP_UP = "top_up"
    SEND = "send"


@dataclass
class WiseTransaction:
    inputfile: str
    currency: str
    transaction_id: str
    action: str
    date: datetime
    amount: Decimal
    description: str
    running_balance: Decimal
    exfrom: str
    exto: str
    examount: Decimal
    rate: Decimal
    payee_name: str
    payee_account: str
    fees: Decimal
    original: dict

    def to_dict(self) -> dict:
        return {
            "inputfile": self.inputfile,
            "currency": self.currency,
            "transaction_id": self.transaction_id,
            "action": self.action,
            "date": self.date,
            "amount": self.amount,
            "description": self.description,
            "running_balance": self.running_balance,
            "exfrom": self.exfrom,
            "exto": self.exto,
            "examount": self.examount,
            "rate": self.rate,
            "payee_name": self.payee_name,
            "payee_account": self.payee_account,
            "fees": self.fees,
            "original": self.original
        }

