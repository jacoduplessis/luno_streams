import json
import decimal

import logging

logger = logging.getLogger('luno_streams')


# https://stackoverflow.com/a/16957370
# json encode decimal.Decimal objects
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError


def get_consumer(pairs, queues, depth):
    async def consumer(websocket, path):

        logger.debug(f'New connection at "{path}".')
        code = path.strip('/').lower()
        if code not in pairs:
            await websocket.send('Invalid path')
            await websocket.close()

        queue = queues.get(code)
        while True:
            data = await queue.get()
            if depth > 0:
                data['bids'] = data['bids'][:depth]
                data['asks'] = data['asks'][:depth]

            message = json.dumps(data, default=decimal_default)
            await websocket.send(message)

    return consumer
