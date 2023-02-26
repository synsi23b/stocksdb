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

tax = [
    TAX_NA,      
]


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
    wb = xlsxwriter.Workbook(filename)
    ws = wb.add_worksheet()
    ws.write_row(0, 0, itemlist[0].get_header())
    for idx, item in enumerate(itemlist):
        ws.write_row(idx + 1, 0, item.to_list())
    wb.close()



expendit_headers = [
    "発生日",        # Accural Date
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