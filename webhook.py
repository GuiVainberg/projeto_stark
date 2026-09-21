from flask import Flask, request
import starkbank
from stark_client import project

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def receive_event():
    try:
        body = starkbank.event.parse(request.data, request.headers["Digital-Signature"], user=project)
        print(body)
    except starkbank.error.InvalidSignatureError as r:
        error_message = f"Assinatura inválida: {request.headers["Digital-Signature"]}"
        return error_message, 400
    return "", 200

if __name__ == "__main__":
    app.run(port=5000)