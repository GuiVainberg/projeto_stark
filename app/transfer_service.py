import starkbank
from stark_client import project


def send_invoice_money(event):
    transfer_data = build_transfer(event)
    starkbank.transfer.create([
        starkbank.Transfer(
            amount=transfer_data["amount"],
            tax_id=transfer_data["tax_id"],
            name=transfer_data["name"],
            bank_code=transfer_data["bank_code"],
            branch_code=transfer_data["branch_code"],
            account_number=transfer_data["account_number"],
            account_type=transfer_data["account_type"],
            external_id=transfer_data["external_id"],
        )
    ], user=project)


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