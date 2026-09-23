import unittest
from types import SimpleNamespace
from unittest.mock import mock_open, patch

import event_log
import webhook


def make_invoice_event(event_id, log_type, invoice_id="inv1", amount=1000, fee=50, errors=None):
    invoice = SimpleNamespace(id=invoice_id, amount=amount, fee=fee)
    log = SimpleNamespace(id=f"log-{event_id}", created="2026-09-23 10:00:00",
                           type=log_type, errors=errors or [], invoice=invoice)
    return SimpleNamespace(id=event_id, log=log, subscription="invoice")


def make_transfer_event(event_id, log_type, transfer_id="trf1", amount=950,
                         external_id="evt1", status=None, errors=None):
    transfer = SimpleNamespace(id=transfer_id, amount=amount, external_id=external_id, status=status or log_type)
    log = SimpleNamespace(id=f"log-{event_id}", created="2026-09-23 10:00:00",
                           type=log_type, errors=errors or [], transfer=transfer)
    return SimpleNamespace(id=event_id, log=log, subscription="transfer")


class WebhookRouteTest(unittest.TestCase):
    def setUp(self):
        event_log.processed_ids.clear()
        self.client = webhook.app.test_client()

        self.mock_parse = self._start_patch("starkbank.event.parse")
        self.mock_create = self._start_patch("starkbank.transfer.create")
        self._start_patch("event_log.open", new_callable=mock_open)

    def _start_patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock

    def post_webhook(self):
        return self.client.post("/webhook", data=b"{}", headers={"Digital-Signature": "fake"})

    def test_credited_invoice_triggers_transfer_with_net_amount(self):
        self.mock_parse.return_value = make_invoice_event("evt1", "credited", amount=1000, fee=50)

        response = self.post_webhook()

        self.assertEqual(response.status_code, 200)
        self.mock_create.assert_called_once()
        [transfer] = self.mock_create.call_args[0][0]
        self.assertEqual(transfer.amount, 950)

    def test_duplicate_event_is_processed_only_once(self):
        self.mock_parse.return_value = make_invoice_event("evt-dup", "credited")

        self.post_webhook()
        self.post_webhook()

        self.mock_create.assert_called_once()

    def test_transfer_event_does_not_trigger_another_transfer(self):
        self.mock_parse.return_value = make_transfer_event("evt-trf", "success")

        response = self.post_webhook()

        self.assertEqual(response.status_code, 200)
        self.mock_create.assert_not_called()

    def test_credited_invoice_with_zero_amount(self):
        self.mock_parse.return_value = make_invoice_event("evt-zero", "credited", amount=0, fee=0)

        response = self.post_webhook()

        self.assertEqual(response.status_code, 200)
        [transfer] = self.mock_create.call_args[0][0]
        self.assertEqual(transfer.amount, 0)

    def test_invalid_signature_returns_400(self):
        self.mock_parse.side_effect = webhook.starkbank.error.InvalidSignatureError("bad signature")

        response = self.post_webhook()

        self.assertEqual(response.status_code, 400)

    def test_missing_signature_header_returns_400(self):
        response = self.client.post("/webhook", data=b"{}")

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()