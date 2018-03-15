import websockets
import asyncio
import json

from decimal import Decimal
import logging
from collections import defaultdict

logger = logging.getLogger('luno_streams')


class Updater:

    def __init__(self, pair_code, api_key, api_secret, hooks=None):
        self.pair_code = pair_code
        self.api_key = api_key
        self.api_secret = api_secret
        self.sequence = None
        self.bids = {}
        self.asks = {}
        self.websocket = None
        self.hooks = hooks or []

    async def connect(self):
        if self.websocket is not None:  # reconnecting
            logger.info(f'[{self.pair_code}] Closing existing connection...')
            await self.websocket.ws_client.close()

        logger.info(f'[{self.pair_code}] Connecting...')
        self.websocket = await websockets.connect(f'wss://ws.luno.com/api/1/stream/{self.pair_code}')
        await self.websocket.send(json.dumps({
            'api_key_id': self.api_key,
            'api_key_secret': self.api_secret,
        }))

        initial = await self.websocket.recv()
        initial_data = json.loads(initial)
        self.sequence = int(initial_data['sequence'])
        self.asks = {x['id']: [Decimal(x['price']), Decimal(x['volume'])] for x in initial_data['asks']}
        self.bids = {x['id']: [Decimal(x['price']), Decimal(x['volume'])] for x in initial_data['bids']}
        logger.info(f'[{self.pair_code}] Initial state received.')

    async def run(self):
        await self.connect()
        async for message in self.websocket:
            if message == '""':
                # keep alive
                continue
            await self.handle_message(message)

    async def handle_message(self, message):
        data = json.loads(message)
        new_sequence = int(data['sequence'])
        if new_sequence != self.sequence + 1:
            logger.warning(
                f'[{self.pair_code}] Sequence broken: expected "{self.sequence+1}", received "{new_sequence}".'
            )
            logger.info(f'[{self.pair_code}] Reconnecting...')
            return await self.connect()

        self.sequence = new_sequence

        if data['delete_update']:
            order_id = data['delete_update']['order_id']

            try:
                del self.bids[order_id]
            except KeyError:
                pass
            try:
                del self.asks[order_id]
            except KeyError:
                pass

        if data['create_update']:
            update = data['create_update']
            price = Decimal(update['price'])
            volume = Decimal(update['volume'])
            key = update['order_id']
            book = self.bids if update['type'] == 'BID' else self.asks
            book[key] = [price, volume]

        trades = []

        if data['trade_updates']:

            for update in data['trade_updates']:
                update['price'] = Decimal(update['counter']) / Decimal(update['base'])
                maker_order_id = update['maker_order_id']
                if maker_order_id in self.bids:
                    self.update_existing_order(key='bids', update=update)
                    trades.append({**update, 'type': 'sell'})
                elif maker_order_id in self.asks:
                    self.update_existing_order(key='asks', update=update)
                    trades.append({**update, 'type': 'buy'})

        for fn in self.hooks:
            args = [self.consolidated_order_book, trades]
            if asyncio.iscoroutinefunction(fn):
                await fn(*args)
            else:
                fn(*args)

    def update_existing_order(self, key, update):
        book = getattr(self, key)
        order_id = update['maker_order_id']
        existing_order = book[order_id]
        existing_volume = existing_order[1]
        new_volume = existing_volume - Decimal(update['base'])
        if new_volume == Decimal('0'):
            del book[order_id]
        else:
            existing_order[1] -= Decimal(update['base'])

    @property
    def consolidated_order_book(self):

        def consolidate(orders, reverse=False):
            price_map = defaultdict(Decimal)

            for order in orders:
                price_map[order[0]] += order[1]

            rounded_list = map(lambda x: [round(x[0], ndigits=8), round(x[1], ndigits=8)], price_map.items())
            return sorted(rounded_list, key=lambda a: a[0], reverse=reverse)

        return {
            'bids': consolidate(self.bids.values(), reverse=True),  # highest bid on top
            'asks': consolidate(self.asks.values()),  # lowest ask on top
        }
