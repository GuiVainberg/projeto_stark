import time

import requests
import starkbank
from stark_client import project

MAX_RETRIES = 3
BASE_DELAY_SECONDS = 0.5


def send_invoice_money(event):
    transfer_data = build_transfer(event)
    transfer = starkbank.Transfer(
        amount=transfer_data["amount"],
        tax_id=transfer_data["tax_id"],
        name=transfer_data["name"],
        bank_code=transfer_data["bank_code"],
        branch_code=transfer_data["branch_code"],
        account_number=transfer_data["account_number"],
        account_type=transfer_data["account_type"],
        external_id=transfer_data["external_id"],
    )
    create_transfer_with_retry(transfer)


def create_transfer_with_retry(transfer):
    for attempt in range(MAX_RETRIES + 1):
        try:
            return starkbank.transfer.create([transfer], user=project)
        except (starkbank.error.InternalServerError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt == MAX_RETRIES:
                raise
            delay = BASE_DELAY_SECONDS * (2 ** attempt)
            print(f"Falha temporária ao criar transfer (tentativa {attempt + 1}/{MAX_RETRIES}): {e}. Retentando em {delay}s.")
            time.sleep(delay)


def build_transfer(event):
    invoice = event.log.invoice
    return {
        "amount": invoice.amount - invoice.fee,
        "name": "Stark Bank S.A.",
        "tax_id": "20.018.183/0001-80",
        "account_number": "6341320293482496",
        "bank_code": "20018183",
        "branch_code": "0001",
        "account_type": "payment",
        "external_id": event.id,
    }