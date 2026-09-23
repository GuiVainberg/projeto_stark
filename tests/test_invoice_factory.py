import unittest
from unittest.mock import patch

import invoice_factory


class BuildInvoiceDataTest(unittest.TestCase):
    def setUp(self):
        self.invoice_data = invoice_factory.build_invoice_data()

    def test_amount_should_be_int(self):
        self.assertIsInstance(self.invoice_data["amount"], int)

    def test_amount_should_be_within_valid_range(self):
        self.assertGreaterEqual(self.invoice_data["amount"], 0)
        self.assertLessEqual(self.invoice_data["amount"], 50000)

    def test_name_should_be_a_non_empty_string_with_full_name(self):
        name = self.invoice_data["name"]
        self.assertIsInstance(name, str)
        self.assertIn(" ", name)  # nome e sobrenome

    def test_tax_id_should_be_a_valid_cpf_or_cnpj(self):
        tax_id = self.invoice_data["tax_id"]
        is_valid = (invoice_factory._cpf_generator.validate(tax_id)
                    or invoice_factory._cnpj_generator.validate(tax_id))
        self.assertTrue(is_valid)


class RandomTaxIdTest(unittest.TestCase):
    def test_generates_different_documents_across_calls(self):
        documents = {invoice_factory.random_tax_id() for _ in range(20)}
        self.assertGreater(len(documents), 1)


class CreateInvoiceTest(unittest.TestCase):
    @patch("invoice_factory.starkbank.invoice.create")
    def test_sends_correct_fields_to_stark_bank(self, mock_create):
        invoice_data = {"amount": 1000, "name": "Guilherme", "tax_id": "012.345.678-90"}

        invoice_factory.create_invoice(invoice_data)

        mock_create.assert_called_once()
        [invoice] = mock_create.call_args[0][0]
        self.assertEqual(invoice.amount, 1000)


class GenerateRandomInvoicesTest(unittest.TestCase):
    @patch("invoice_factory.random.randint")
    @patch("invoice_factory.create_invoice")
    @patch("invoice_factory.build_invoice_data")
    def test_creates_between_8_and_12_invoices(self, mock_build_data, mock_create_invoice, mock_randint):
        mock_randint.return_value = 10
        mock_build_data.return_value = {"amount": 1000, "name": "Guilherme", "tax_id": "012.345.678-90"}

        invoice_factory.generate_random_invoices()

        self.assertEqual(mock_create_invoice.call_count, 10)


if __name__ == "__main__":
    unittest.main()