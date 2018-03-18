from luno_streams import Updater


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
