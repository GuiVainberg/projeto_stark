import unittest
from invoice_factory import build_invoice_data

class InvoiceGenerator(unittest.TestCase):
    def setUp(self):
        self.invoice_data = build_invoice_data()
    
    def test_amount_should_be_int(self):
        self.assertIsInstance(self.invoice_data["amount"], int)
    def test_name_should_be_string(self):
        self.assertIsInstance(self.invoice_data["name"], str)


if __name__ == '__main__':
    unittest.main()