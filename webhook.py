from flask import Flask, request
import starkbank
from stark_client import project
from transfer_service import send_invoice_money
from event_log import log_event, is_processed, mark_processed

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def receive_event():
    try:
        signature = request.headers.get("Digital-Signature")
        if signature is None:
            return "Header Digital-Signature ausente", 400

        body = starkbank.event.parse(request.data.decode("utf-8"), signature, user=project)

        if is_processed(body.id):
            return "", 200
        mark_processed(body.id)

        if body.log.type == "credited" and body.subscription == "invoice":
            send_invoice_money(body)

        log_event(body)
    except starkbank.error.InvalidSignatureError:
        return "Assinatura inválida", 400
    except Exception as e:
        print(f"Erro inesperado processando webhook: {e}")
        return "Erro interno", 500
    return "", 200


if __name__ == "__main__":
    app.run(port=5000)