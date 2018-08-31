from luno_streams import Updater, BackoffException
import time
from unittest import TestCase


class TestOrderBook(TestCase):

    def test_order_book_consolidation(self):
        updater = Updater('123', '456', 'abc')
        updater.bids = {
            'a': [500, 1],
            'b': [500, 2],
        }
        updater.asks = {
            'c': [600, 4],
            'd': [600, 6]
        }
        consolidated = updater.consolidated_order_book
        self.assertEqual(consolidated['asks'], [[600, 10]])
        self.assertEqual(consolidated['bids'], [[500, 3]])


class TestBackoff(TestCase):

    def test_backoff(self):

        updater = Updater('123', '456', 'abc')
        # 0 seconds should raise
        updater.time_last_connection_attempt = time.time()
        with self.assertRaises(BackoffException):
            updater.check_backoff()
        # 5 seconds should also raise
        updater.time_last_connection_attempt = time.time() - 5
        with self.assertRaises(BackoffException):
            updater.check_backoff()
        # 12 seconds should not
        updater.time_last_connection_attempt = time.time() - 12
        updater.check_backoff()
