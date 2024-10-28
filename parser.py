import sys
import os
import csv
import json
from tabulate import tabulate
import re
from dateutil.parser import parse

OP_DATE = "#Data operacji"
OP_BOOKDATE = "#Data księgowania"
OP_DESC = "#Opis operacji"
OP_TITLE = "#Tytuł"
OP_PAYEE = "#Nadawca/Odbiorca"
OP_ACCOUNT = "#Numer konta"
OP_AMOUNT = "#Kwota"
OP_BALANCE = "#Saldo po operacji"

HEADER = ";".join(
    [
        OP_DATE,
        OP_BOOKDATE,
        OP_DESC,
        OP_TITLE,
        OP_PAYEE,
        OP_ACCOUNT,
        OP_AMOUNT,
        OP_BALANCE,
    ]
)

OP_CreditCardPayment = "OUT-CC"

OP_TYPE = [
    {"PRZELEW WEWNĘTRZNY WYCHODZĄCY": "OUT-INT"},
    {"PRZELEW ZEWNĘTRZNY WYCHODZĄCY": "OUT-EXT"},
    {"ZAKUP PRZY UŻYCIU KARTY": OP_CreditCardPayment},
    {"PRZELEW PRZYSZŁY DO ZUS": "OUT-ZUS"},
    {"PRZELEW PRZYSZŁY PODATKOWY": "OUT-TAX"},
    {"WYPŁATA W BANKOMACIE": "OUT-CASH"},
    {"PRZELEW ZEWNĘTRZNY PRZYCHODZĄCY": "IN-EXT"},
]

OP_ACC = [
    {"13..8711": "MILL:ROR"},
    {"48..4623": "MB:ROR"},
    {"82..4425": "ZUS"},
]


from accountant.counterpart_manager import (
    CounterpartyManager,
    CounterpartyError,
)

manager = CounterpartyManager()


def extract(filepath: str, opt):
    with open(filepath, newline="", encoding="cp1250") as csvfile:
        offset = get_offset(csvfile, HEADER)
        dialect = csv.Sniffer().sniff(csvfile.readline(), delimiters=";")
        csvfile.seek(offset)

        if len(opt) >= 2 and opt[1] == "raw":
            reader = csv.DictReader(csvfile, dialect=dialect)

            data = list(reader)
            print(data)
            # print(tabulate(data, headers="keys"))
            return

        data = [[OP_DATE, OP_DESC, OP_PAYEE, OP_TITLE]]
        for index, record in enumerate(
            csv.DictReader(csvfile, dialect=dialect)
        ):
            if not re.match(r"\d\d\d\d", record[OP_DATE]):
                continue
            # date = parse(record[OP_DATE]).date()
            date = record[OP_DATE]
            op_type = find(record[OP_DESC], OP_TYPE)
            acc = find(record[OP_ACCOUNT].strip("'"), OP_ACC)
            payee = (
                record[OP_TITLE]
                if op_type == OP_CreditCardPayment
                else record[OP_PAYEE]
            )
            id, payee = ppayee(payee, acc)
            title = record[OP_TITLE]
            p = f"{acc}{payee}" if payee == "@SELF" else payee
            data.append([date, op_type, p, title])
        print(tabulate(data, headers="firstrow"))


def counterparty(op, p, t):
    if op == OP_CreditCardPayment:
        return t
    return p


def ppayee(text: str, acc: str):
    text = re.sub(r"\s+", " ", text).upper()
    if text.startswith("ŁUKASZ STRZĘPEK"):
        return 1, "@SELF"
    if text.find(" /") > 0:
        info = text.strip().split(" /", maxsplit=1)
        name = info[0]
        address = info[1]
        if not name:
            return 1, ""
        return manager.get_or_create_partner(name, address, acc)
    else:
        return manager.get_or_create_partner(text, acc)


def find(text: str, d) -> str:
    for pair in d:
        if text in pair:
            return pair[text]
    return text


def get_offset(file, line_prefix):
    """Rewind file offset to csv header and skip metadata"""
    offset = 0
    for line in file.readlines():

        if line.startswith(line_prefix):
            file.seek(offset)
            break
        else:
            offset += len(line)
            continue
    return offset


# def parse_units(value, unit):
#     """ Returns amount from mbank money statement """
#     price = to_decimal(value)
#     return amount.Amount(price, unit)


# def to_decimal(value):
#     price = value.replace(",", ".")
#     return D(price)

extract("./Downloads/????????.csv", sys.argv)
