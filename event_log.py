import json

processed_ids = set()


def is_processed(event_id):
    return event_id in processed_ids


def mark_processed(event_id):
    processed_ids.add(event_id)


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

    with open("webhook.log", "a") as f:
        f.write(json.dumps(data) + "\n")