import argparse
import asyncio
import logging
import threading
from collections import defaultdict

import websockets

from .app import get_server
from .server import get_consumer
from .updater import Updater

logging.basicConfig()
logger = logging.getLogger('luno_streams')


def main():
    parser = argparse.ArgumentParser()
    parser.description = 'Run a websocket server to serve updates.'
    parser.add_argument('api_key', type=str, help='API Key ID.')
    parser.add_argument('api_secret', type=str, help='API Key Secret.')
    parser.add_argument('pairs', type=str, nargs='+', help='Pairs to subscribe to, e.g. XBTZAR.')
    parser.add_argument('--log-level', '-l', default='WARNING', help='Log level [default WARNING]')
    parser.add_argument('--port', '-p', default=8010, help='Server port [default 8010].')
    parser.add_argument('--address', default='', help='Server address [default ''].')
    parser.add_argument('--depth', '-d', default=0, type=int,help='Maximum amount of orders to display on each side of the order book.')
    parser.add_argument('--app', default=False, action='store_true', help='Run example app (serves single html file).')
    parser.add_argument('--app-port', default=8011, type=int, help='Port on which to run example app [default 8011].')
    options = parser.parse_args()

    logger.setLevel(options.log_level)
    pairs = list(map(str.lower, options.pairs))
    hooks = defaultdict(list)
    queues = {}

    for code in pairs:
        queue = asyncio.Queue()

        def hook(order_book, trades):
            payload = {**order_book, 'trades': trades}
            queue.put_nowait(payload)

        hooks[code].append(hook)
        queues[code] = queue

    async def run_updater(code):

        updater = Updater(
            pair_code=code,
            api_key=options.api_key,
            api_secret=options.api_secret,
            hooks=hooks.get(code),
        )
        await updater.run()

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(run_updater(code)) for code in pairs]
    if options.app:
        server = get_server(options.address, options.app_port)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        app_url = f'http://localhost:{options.app_port}'
        print('Open the app in your browser:', app_url)

    consumer = get_consumer(pairs, queues, options.depth)
    tasks.append(websockets.serve(consumer, options.address, options.port))
    print('Running websocket server on port', options.port)

    loop.run_until_complete(asyncio.gather(*tasks))
