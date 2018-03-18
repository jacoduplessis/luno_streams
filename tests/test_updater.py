from luno_streams import Updater, BackoffException
import time
import pytest


def test_order_book_consolidation():
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
    assert consolidated['asks'] == [[600, 10]]
    assert consolidated['bids'] == [[500, 3]]


def test_backoff():
    updater = Updater('123', '456', 'abc')
    # 0 seconds should raise
    updater.time_last_connection_attempt = time.time()
    with pytest.raises(BackoffException):
        updater.check_backoff()
    # 5 seconds should also raise
    updater.time_last_connection_attempt = time.time() - 5
    with pytest.raises(BackoffException):
        updater.check_backoff()
    # 12 seconds should not
    updater.time_last_connection_attempt = time.time() - 12
    updater.check_backoff()
