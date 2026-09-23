import json

LOG_FILE = "webhook.log"

processed_ids = set()


def is_processed(event_id):
    return event_id in processed_ids


def mark_processed(event_id):
    processed_ids.add(event_id)


def load_processed_ids():
    try:
        with open(LOG_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                processed_ids.add(json.loads(line)["event_id"])
    except FileNotFoundError:
        pass


def log_event(event):
    data = {
        "event_id": event.id,
        "type": event.log.type,
        "created": str(event.log.created),
        "error": event.log.errors,
    }
    if event.subscription == "invoice":
        data["invoice_id"] = event.log.invoice.id
        data["amount"] = event.log.invoice.amount
    elif event.subscription == "transfer":
        data["transfer_id"] = event.log.transfer.id
        data["amount"] = event.log.transfer.amount
        data["external_id"] = event.log.transfer.external_id
        data["status"] = event.log.transfer.status

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")