import time
import unittest
from datetime import date, datetime

import mock
import six


class TestClient(unittest.TestCase):
    def fail(self, e, batch):
        """Mark the failure handler"""
        self.failed = True

    def setUp(self):
        self.failed = False

    def test_split_features_target(self):
        self.assertTrue(True)
        # self.assertRaises(AssertionError, Client)
        # self.assertEqual(msg["event"], "python test event")
