import starkbank
import random
from typing import Any
from datetime import date, datetime, timedelta
from stark_client import project

def create_invoice(invoice_data) -> None:
    starkbank.invoice.create([
        starkbank.Invoice(
            amount=invoice_data["amount"],
            #descriptions=[{'key': 'Thor\'s pub bill', 'value': 'U$500,00'}],
            #discounts=[{'percentage': 10, 'due': datetime(2026, 7, 20, 15, 23, 26, 689377)}],
            #due=datetime(2026, 9, 20, 15, 23, 26, 689377),
            #expiration=5097600,
            #fine=2.5,
            #interest=1.3,
            name=invoice_data["name"],
            #tags=['War supply', 'Invoice #1234'],
            tax_id=invoice_data["tax_id"],
            # rules=[
            #     {
            #         'key': 'allowedTaxIds',
            #         'value': [
            #             '012.345.678-90',
            #             '45.059.493/0001-73'
            #         ]
            #     }
            # ],
            # splits=[
            #     starkbank.Split(amount=3000, receiverId="5742447426535424"), starkbank.Split(amount=5000, receiverId="5743243941642240")
            # ]
        )
    ], user=project)

def generate_random_invoices() -> None:
    invoices_amount = random.randint(8,12)
    for i in range(invoices_amount):
        invoice_data = build_invoice_data()
        create_invoice(invoice_data)

    return print(f"{invoices_amount} invoices sucessfully created!")

def build_invoice_data() -> dict:
    amount = random.randint(0,50000)
    name_list = ["Guilherme", "Natally", "Camila", "Rafael"]
    name = random.choice(name_list)

    invoice_data = {
    "amount": amount,
    "name": name,
    "tax_id": "012.345.678-90",
    }

    return invoice_data

if __name__ == "__main__":
    generate_random_invoices()