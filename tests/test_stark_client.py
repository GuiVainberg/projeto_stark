import os
import unittest
from unittest.mock import patch

import stark_client


class GetRequiredEnvTest(unittest.TestCase):
    @patch.dict(os.environ, {"MEU_VAR": "valor"})
    def test_returns_value_when_set(self):
        self.assertEqual(stark_client.get_required_env("MEU_VAR"), "valor")

    def test_raises_when_missing(self):
        with self.assertRaises(ValueError):
            stark_client.get_required_env("VARIAVEL_QUE_NAO_EXISTE")


if __name__ == "__main__":
    unittest.main()