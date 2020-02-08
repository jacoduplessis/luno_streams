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

    def test_processing(self):
        updater = Updater('123', '456', 'abc')

        self.assertDictEqual(updater.bids, {})
        self.assertDictEqual(updater.asks, {})

        # create a bid
        message = {
            'create_update': {
                'price': 100,
                'volume': 10,
                'order_id': 'a',
                'type': 'BID'
            },
            'delete_update': {},
            'trade_updates': []
        }

        trades = updater.process_message(message)

        expected_bids = {
            'a': [100, 10]
        }
        expected_asks = {}
        expected_trades = []
        self.assertDictEqual(updater.bids, expected_bids)
        self.assertDictEqual(updater.asks, expected_asks)
        self.assertListEqual(trades, expected_trades)

        # create an ask
        message = {
            'create_update': {
                'price': 100,
                'volume': 10,
                'order_id': 'b',
                'type': 'ASK'
            },
            'delete_update': {},
            'trade_updates': []
        }

        trades = updater.process_message(message)

        expected_bids = {
            'a': [100, 10]
        }
        expected_asks = {
            'b': [100, 10]
        }
        expected_trades = []
        self.assertDictEqual(updater.bids, expected_bids)
        self.assertDictEqual(updater.asks, expected_asks)
        self.assertListEqual(trades, expected_trades)

        # delete ask
        message = {
            'create_update': {},
            'delete_update': {
                'order_id': 'b'
            },
            'trade_updates': []
        }

        trades = updater.process_message(message)
        expected_bids = {
            'a': [100, 10]
        }
        expected_asks = {}
        expected_trades = []
        self.assertDictEqual(updater.bids, expected_bids)
        self.assertDictEqual(updater.asks, expected_asks)
        self.assertListEqual(trades, expected_trades)

        # sell half of bid order
        message = {
            'create_update': {},
            'delete_update': {},
            'trade_updates': [
                {
                    'counter': 500,
                    'base': 5,
                    'maker_order_id': 'a'
                }
            ]
        }

        trades = updater.process_message(message)
        expected_bids = {
            'a': [100, 5]
        }
        expected_asks = {}
        expected_trades = [
            {
                'type': 'sell',
                'price': 100,
                'base': 5,
                'counter': 500,
                'maker_order_id': 'a',
            }
        ]
        self.assertDictEqual(updater.bids, expected_bids)
        self.assertDictEqual(updater.asks, expected_asks)
        self.assertListEqual(trades, expected_trades)

        # sell remaining part of bid order
        message = {
            'create_update': {},
            'delete_update': {},
            'trade_updates': [
                {
                    'counter': 500,
                    'base': 5,
                    'maker_order_id': 'a'
                }
            ]
        }

        trades = updater.process_message(message)
        expected_bids = {}
        expected_asks = {}
        expected_trades = [
            {
                'type': 'sell',
                'price': 100,
                'base': 5,
                'counter': 500,
                'maker_order_id': 'a',
            }
        ]
        self.assertDictEqual(updater.bids, expected_bids)
        self.assertDictEqual(updater.asks, expected_asks)
        self.assertListEqual(trades, expected_trades)

        # order is placed that is partially filled

        # first add an existing bid
        message = {
            'create_update': {
                'order_id': 'c',
                'price': 150,
                'volume': 10,
                'type': 'BID',
            },
            'delete_update': {},
            'trade_updates': []
        }
        updater.process_message(message)

        # buy order was placed and partially filled
        message = {
            'create_update': {
                'order_id': 'd',
                'price': 150,
                'volume': 50,
                'type': 'ASK'
            },
            'delete_update': {},
            'trade_updates': [
                {
                    'counter': 1500,
                    'base': 10,
                    'maker_order_id': 'c'
                }
            ]
        }

        trades = updater.process_message(message)
        expected_bids = {}
        expected_asks = {
            'd': [150, 50]
        }
        expected_trades = [
            {
                'type': 'sell',
                'price': 150,
                'base': 10,
                'counter': 1500,
                'maker_order_id': 'c',
            }
        ]
        self.assertDictEqual(updater.bids, expected_bids)
        self.assertDictEqual(updater.asks, expected_asks)
        self.assertListEqual(trades, expected_trades)


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
