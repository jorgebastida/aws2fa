import sys
import unittest

try:
    from mock import patch, Mock
except ImportError:
    from unittest.mock import patch, Mock

from aws2fa import AWS2FA
from aws2fa.bin import main


class TestAWS2FA(unittest.TestCase):

    def test_aaa(self):
        pass
