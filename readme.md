# Luno Streams

Python library to connect to the Luno API with websockets. 

Includes example app to replicate the Luno Exchange interface as well 
as proxy server for easy consumption of practical market data.

Luno reference: https://www.luno.com/en/api#streaming

## Install

```
pip install luno_streams
```

## Example usage

```python

import asyncio
from luno_streams import Updater

def print_it(consolidated_order_book, trades):
    print(consolidated_order_book, trades)

updater = Updater(
    pair_code='XBTZAR',
    api_key='123',
    api_secret='456',
    hooks=[print_it],
)

loop = asyncio.get_event_loop()
loop.run_until_complete(updater.run())
```

See the `cli.py` file for example of running multiple websocket connections in parallel, as well
as how hooks are used to store results and proxy to other websockets.

## Hooks

The `Updater` accepts a `hooks` parameter - a list of functions or coroutines that will be called
whenever the order book is updated.

Each hook will receive two arguments:

1. a consolidated order book, which groups all orders by price. See **Order Book Structure** below.
2. a list of trades that were performed during the last update. See **Trade Structure** below.

Scan the list of trades if you need to determine whether your order was fulfilled without making 
an API call.

## Order Book Structure

An order book is a dict with two keys: `bids` and `asks`. Each side contains a list
of entries, where each entry is a list of the form `[price, volume]`.

Entries are ordered — `bids` are ordered with the highest price on top, and `asks` are ordered with the lowest
price on `top`.

Example:

```json
{
    "bids": [
      ["500", "0.5"],
      ["480", "0.7"]
    ],
    "asks": [
      ["520", "0.4"],
      ["540", "0.6"]
    ]
}
```

# Trade Structure

A trade is a dict with the following keys: 

* `type` - `buy` or `sell`
* `price`
* `base` - volume
* `taker_order_id`
* `maker_order_id`

## Running the socket server

```
luno_streams api_key api_secret pairs [pairs ...]
```


Extras:

* `--app` - print a local file URL to open in your browser
* `--depth` - specify an integer `n` to trim the order book to at most `n` orders on each side

Run `luno_streams --help` to view all commands.

It is highly recommended to use the `--depth` option, usually somewhere between 100 - 200 is a good choice.
