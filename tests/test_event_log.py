import json
import unittest
from types import SimpleNamespace
from unittest.mock import mock_open, patch

import event_log


def make_invoice_event(event_id, log_type, invoice_id="inv1", amount=1000, errors=None):
    invoice = SimpleNamespace(id=invoice_id, amount=amount)
    log = SimpleNamespace(id=f"log-{event_id}", created="2026-09-23 10:00:00",
                           type=log_type, errors=errors or [], invoice=invoice)
    return SimpleNamespace(id=event_id, log=log, subscription="invoice")


def make_transfer_event(event_id, log_type, transfer_id="trf1", amount=950,
                         external_id="evt1", status=None, errors=None):
    transfer = SimpleNamespace(id=transfer_id, amount=amount, external_id=external_id, status=status or log_type)
    log = SimpleNamespace(id=f"log-{event_id}", created="2026-09-23 10:00:00",
                           type=log_type, errors=errors or [], transfer=transfer)
    return SimpleNamespace(id=event_id, log=log, subscription="transfer")


class ProcessedIdsTest(unittest.TestCase):
    def setUp(self):
        event_log.processed_ids.clear()

    def test_new_id_is_not_processed(self):
        self.assertFalse(event_log.is_processed("evt1"))

    def test_marked_id_is_processed(self):
        event_log.mark_processed("evt1")
        self.assertTrue(event_log.is_processed("evt1"))


class LogEventTest(unittest.TestCase):
    @patch("event_log.open", new_callable=mock_open)
    def test_logs_invoice_fields(self, mock_file):
        event = make_invoice_event("evt1", "credited", invoice_id="inv1", amount=1000)

        event_log.log_event(event)

        written = mock_file().write.call_args[0][0]
        data = json.loads(written)
        self.assertEqual(data["invoice_id"], "inv1")
        self.assertEqual(data["amount"], 1000)

    @patch("event_log.open", new_callable=mock_open)
    def test_logs_transfer_fields(self, mock_file):
        event = make_transfer_event("evt1", "success", transfer_id="trf1", external_id="evt0")

        event_log.log_event(event)

        written = mock_file().write.call_args[0][0]
        data = json.loads(written)
        self.assertEqual(data["transfer_id"], "trf1")
        self.assertEqual(data["external_id"], "evt0")

class LoadProcessedIdsTest(unittest.TestCase):
    def setUp(self):
        event_log.processed_ids.clear()

    @patch("event_log.open", new_callable=mock_open, read_data='{"event_id": "evt1"}\n{"event_id": "evt2"}\n')
    def test_populates_processed_ids_from_existing_log(self, _mock_file):
        event_log.load_processed_ids()

        self.assertIn("evt1", event_log.processed_ids)
        self.assertIn("evt2", event_log.processed_ids)

    @patch("event_log.open", side_effect=FileNotFoundError)
    def test_does_nothing_when_log_file_does_not_exist(self, _mock_file):
        event_log.load_processed_ids()

        self.assertEqual(event_log.processed_ids, set())


if __name__ == "__main__":
    unittest.main()