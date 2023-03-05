import xlsxwriter
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

transfer_headers = [
    "日付",          # Date

    "借方勘定科目",   # Debit Account
    "借方品目",      # Debit Item
    "借方金額",      # Debit Amount
    "借方税区分",    # Debit Tax Segment
    "借方税額",      # Debit Tax Amount

    "貸方勘定科目",   # Credit Account
    "貸方品目",      # Credit Item
    "貸方金額",      # Credit Amount
    "貸方税区分",    # Credit Tax Segment
    "貸方税額",      # Credit Tax Amount

    "摘要",         # Remarks
    ]

TAX_NA = "対象外" # Not Applicable
TAX_EXPORT_SALE = "輸出売返" 
TAX_PURCHASE = "課対仕入 10%"

@dataclass
class TransferDetail:
    account: str
    item: str
    amount: Decimal
    tax_segment: str
    tax_amount: Decimal

    def to_list(self):
        return [
            self.account,
            self.item,
            self.amount,
            self.tax_segment,
            self.tax_amount
        ]


@dataclass
class Transfer:
    date: datetime
    debit: TransferDetail
    credit: TransferDetail
    remarks: str

    def get_header(self):
        return transfer_headers

    def to_list(self):
        header = [ self.date.strftime("%Y-%m-%d") ]
        footer = [ self.remarks ]
        return header + self.debit.to_list() + self.credit.to_list() + footer


def make_xlsx(filename, itemlist):
    if itemlist:
        wb = xlsxwriter.Workbook(filename)
        ws = wb.add_worksheet()
        ws.write_row(0, 0, itemlist[0].get_header())
        for idx, item in enumerate(itemlist):
            ws.write_row(idx + 1, 0, item.to_list())
        wb.close()


expendit_headers = [
    "発生日",        # Accrual Date
    #"決済期日",      # Settlement Date
    "収支区分",      # category
    "取引先",       # Client
    "勘定科目",      # reason?
    "決済口座",      # Settlement Account
    "金額",         # Amount
    "税区分",       # Tax Segment
    "備考",         # Remarks
]


EXP_COMMISSION_PAID = "支払手数料"
EXP_OWNER_LOAN = "事業主貸"
EXP_MISC = "雑費"
EXP_FX_LOSS = "為替差損"
EXP_EXPENDIBLES = "消耗品費"
EXP_COMMUNICATION = "通信費"

@dataclass
class Expenditure:
    date: datetime
    client: str
    category: str
    account: str
    amount: Decimal
    tax_segment: str
    remarks: str

    def get_header(self):
        return expendit_headers

    def to_list(self):
        header = [ self.date.strftime("%Y-%m-%d"), "支出" ]
        center = [
            self.client,
            self.category,
            self.account,
            self.amount,
            self.tax_segment
        ]
        footer = [ self.remarks ]
        return header + center + footer


def expend_private(date, client, account, amount, remarks):
    return Expenditure(date, client, EXP_OWNER_LOAN, account, amount, TAX_NA, remarks)


def expend_fx(date, client, account, amount, remarks):
    return Expenditure(date, client, EXP_MISC, account, amount, TAX_NA, f"{EXP_FX_LOSS} {remarks}")


def expend_purchase(date, client, account, amount, remarks):
    return Expenditure(date, client, EXP_EXPENDIBLES, account, amount, TAX_PURCHASE, remarks)


def expend_communication(date, client, account, amount, remarks):
    return Expenditure(date, client, EXP_COMMUNICATION, account, amount, TAX_PURCHASE, remarks)


def expend_travel(date, client, account, amount, remarks):
    return Expenditure(date, client, EXP_COMMUNICATION, account, amount, TAX_PURCHASE, remarks)


INC_ONWER_LOAN = "事業主借"
INC_MISC = "雑収入"
INC_FX_GAIN = "為替差益"
INC_SALE = "売上高"

@dataclass
class Income:
    date: datetime
    client: str
    category: str
    account: str
    amount: Decimal
    tax_segment: str
    remarks: str

    def get_header(self):
        return expendit_headers

    def to_list(self):
        header = [ self.date.strftime("%Y-%m-%d"), "収入" ]
        center = [
            self.client,
            self.category,
            self.account,
            self.amount,
            self.tax_segment
        ]
        footer = [ self.remarks ]
        return header + center + footer
    

def income_sale_export(date, client, account, amount, remarks):
    return Income(date, client, INC_SALE, account, amount, TAX_EXPORT_SALE, remarks)


def income_private(date, client, account, amount, remarks):
    return Income(date, client, INC_ONWER_LOAN, account, amount, TAX_NA, remarks)


def income_fx(date, client, account, amount, remarks):
    return Income(date, client, INC_MISC, account, amount, TAX_NA, f"{INC_FX_GAIN} {remarks}")