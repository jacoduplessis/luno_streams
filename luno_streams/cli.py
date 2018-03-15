import argparse
import asyncio
import websockets
from .updater import Updater
from .server import get_consumer
from collections import defaultdict
import logging
import pathlib


logging.basicConfig()
logger = logging.getLogger('luno_streams')
logger.setLevel(logging.DEBUG)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('api_key', type=str, help='API Key ID.')
    parser.add_argument('api_secret', type=str, help='API Key Secret.')
    parser.add_argument('pairs', type=str, nargs='+', help='Pairs to subscribe to, e.g. XBTZAR.')
    parser.add_argument('--server', action='store_true', help='Run optional Websocket server.')
    parser.add_argument('--port', default=8010, help='Server port.')
    parser.add_argument('--address', default='127.0.0.1', help='Server address.')
    parser.add_argument('--depth', default=0, type=int, help='Maximum amount of orders to display on each side of the order book.')
    parser.add_argument('--app', default=False, action='store_true', help='Print URL of local app to display order books.')
    options = parser.parse_args()

    pairs = options.pairs
    run_server = options.server
    hooks = defaultdict(list)
    queues = {}
    if run_server:
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
        if not run_server:
            print('You can only use the app if you are running the websocket server with --server.')
        else:
            url = 'file://' + str(pathlib.Path(__file__).parent / 'app.html')
            print(f'Open the following file in your browser: {url}')

    if run_server:
        consumer = get_consumer(pairs, queues, options.depth)
        tasks.append(websockets.serve(consumer, options.address, options.port))
    loop.run_until_complete(asyncio.gather(*tasks))
