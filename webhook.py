from flask import Flask, request
import starkbank
from stark_client import project

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def receive_event():
    try:
        body = starkbank.event.parse(request.data, request.headers["Digital-Signature"], user=project)
        if body.log.type == "credited" and body.subscription == "invoice":
            send_invoice_money(body)
        elif body.subscription == "transfer":
            log_transfer_result(body.log)
    except starkbank.error.InvalidSignatureError as r:
        error_message = f"Assinatura inválida: {request.headers["Digital-Signature"]}"
        return error_message, 400
    return "", 200

def send_invoice_money(event):
    transfer_data = build_transfer(event)
    transfers = starkbank.transfer.create([
    starkbank.Transfer(
        amount= transfer_data["amount"],
        tax_id=transfer_data["tax_id"],
        name=transfer_data["name"],
        bank_code=transfer_data["bank_code"],
        branch_code=transfer_data["branch_code"],
        account_number=transfer_data["account_number"],
        account_type=transfer_data["account_type"],
        external_id=transfer_data["external_id"]
    )
    ], user=project)

def build_transfer(event):
    invoice = event.log.invoice
    transfer_data = {
        "amount": invoice.amount - invoice.fee,
        "name": "Stark Bank S.A.",
        "tax_id": "20.018.183/0001-80",
        "account_number": "6341320293482496",
        "bank_code": "20018183",
        "branch_code": "0001",
        "account_type": "payment",
        "external_id": event.id
        }
    return transfer_data

def log_transfer_result(log):
    if log.type == "success":
        print("Transferências ralizadas com sucesso")
    if log.errors:
        print(f"Erro ao processar transferências: {log.errors}")

if __name__ == "__main__":
    app.run(port=5000)