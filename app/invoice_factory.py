import random

import starkbank
from faker import Faker
from stark_client import project
from validate_docbr import CNPJ, CPF

fake = Faker("pt_BR")
_cpf_generator = CPF()
_cnpj_generator = CNPJ()


def create_invoice(invoice_data) -> None:
    starkbank.invoice.create([
        starkbank.Invoice(
            amount=invoice_data["amount"],
            name=invoice_data["name"],
            tax_id=invoice_data["tax_id"],
        )
    ], user=project)


def generate_random_invoices() -> None:
    invoices_amount = random.randint(8, 12)
    for i in range(invoices_amount):
        invoice_data = build_invoice_data()
        create_invoice(invoice_data)

    return print(f"{invoices_amount} invoices sucessfully created!")


def build_invoice_data() -> dict:
    amount = random.randint(0, 50000)
    name = fake.name()
    tax_id = random_tax_id()

    return {
        "amount": amount,
        "name": name,
        "tax_id": tax_id,
    }


def random_tax_id() -> str:
    generator = random.choice([_cpf_generator, _cnpj_generator])
    return generator.generate(mask=True)


if __name__ == "__main__":
    generate_random_invoices()