# Luno Streams

Python library to connect to the Luno API with websockets.

## CLI

```
luno_streams <api_key> <api_secret> [<pairs>,]
```

Extras:

* `--server` - run a websocket server that sends updates to
* `--app` - print a local file URL to open in your browser

Run `luno_streams --help` to view all commands

## Example usage

```python

import asyncio
from luno_streams import Updater

def print_it(consolidated_order_book, trades):
    print(consolidated_order_book, trades)

async def async_fn(consolidated_order_book, trades):
    await asyncio.sleep(10)
    print(consolidated_order_book, trades)

updater = Updater(
    pair_code='XBTZAR',
    api_key='123',
    api_secret='456',
    hooks=[print_it, async_fn], # list of functions/coroutines to be executed when order book is updated
)

loop = asyncio.get_event_loop()
loop.run_until_complete(updater.run)
```

See the `cli.py` file for example of running multiple websocket connections in parallel.
