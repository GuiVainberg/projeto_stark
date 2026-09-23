import unittest
from types import SimpleNamespace
from unittest.mock import patch

import starkbank
import transfer_service


def make_invoice_event(event_id, amount=1000, fee=50, invoice_id="inv1"):
    invoice = SimpleNamespace(id=invoice_id, amount=amount, fee=fee)
    log = SimpleNamespace(invoice=invoice)
    return SimpleNamespace(id=event_id, log=log)


class BuildTransferTest(unittest.TestCase):
    def test_subtracts_fee_from_amount(self):
        event = make_invoice_event("evt1", amount=1000, fee=50)

        data = transfer_service.build_transfer(event)

        self.assertEqual(data["amount"], 950)
        self.assertEqual(data["external_id"], "evt1")


class SendInvoiceMoneyTest(unittest.TestCase):
    @patch("starkbank.transfer.create")
    def test_creates_transfer_with_net_amount(self, mock_create):
        event = make_invoice_event("evt1", amount=1000, fee=50)

        transfer_service.send_invoice_money(event)

        mock_create.assert_called_once()
        [transfer] = mock_create.call_args[0][0]
        self.assertEqual(transfer.amount, 950)

class SendInvoiceMoneyRetryTest(unittest.TestCase):
    def setUp(self):
        self.sleep_patcher = patch("transfer_service.time.sleep")
        self.mock_sleep = self.sleep_patcher.start()
        self.addCleanup(self.sleep_patcher.stop)

    @patch("starkbank.transfer.create")
    def test_succeeds_on_first_attempt_without_retry(self, mock_create):
        event = make_invoice_event("evt1")

        transfer_service.send_invoice_money(event)

        mock_create.assert_called_once()
        self.mock_sleep.assert_not_called()

    @patch("starkbank.transfer.create")
    def test_retries_on_transient_error_then_succeeds(self, mock_create):
        mock_create.side_effect = [starkbank.error.InternalServerError(), None]
        event = make_invoice_event("evt1")

        transfer_service.send_invoice_money(event)

        self.assertEqual(mock_create.call_count, 2)
        self.mock_sleep.assert_called_once()

    @patch("starkbank.transfer.create")
    def test_raises_after_exhausting_retries(self, mock_create):
        mock_create.side_effect = starkbank.error.InternalServerError()
        event = make_invoice_event("evt1")

        with self.assertRaises(starkbank.error.InternalServerError):
            transfer_service.send_invoice_money(event)

        self.assertEqual(mock_create.call_count, transfer_service.MAX_RETRIES + 1)

    @patch("starkbank.transfer.create")
    def test_does_not_retry_permanent_input_error(self, mock_create):
        mock_create.side_effect = starkbank.error.InputErrors([{"code": "invalid", "message": "bad tax_id"}])
        event = make_invoice_event("evt1")

        with self.assertRaises(starkbank.error.InputErrors):
            transfer_service.send_invoice_money(event)

        mock_create.assert_called_once()
        self.mock_sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()