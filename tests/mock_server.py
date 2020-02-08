import asyncio
import websockets
import json

import logging

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

INITIAL_STATE = {
    "asks": [
        {
            "id": "23298343",
            "price": "1234.00",
            "volume": "0.93"
        }
    ],
    "bids": [
        {
            "id": "3498282",
            "price": "1201.00",
            "volume": "1.22"
        }
    ],
    "status": "ACTIVE",
    "timestamp": 1528884331021
}


async def periodic_updates(websocket, broken_sequence=False):
    sequence = 1
    credentials = await websocket.recv()

    state = INITIAL_STATE.copy()
    state['sequence'] = sequence if not broken_sequence else '1234'
    await websocket.send(json.dumps(state))

    while True:
        await asyncio.sleep(1)
        sequence += 1
        await websocket.send(
            json.dumps({
                "sequence": str(sequence),
                "trade_updates": None,
                "create_update": None,
                "delete_update": None,
                "status_update": None,
                "timestamp": 1528884331022
            })
        )


async def close_connection(websocket):
    credentials = await websocket.recv()

    state = INITIAL_STATE.copy()
    state['sequence'] = '99'
    await websocket.send(json.dumps(state))
    await websocket.close()


async def luno_server(websocket, path):
    if path == '/simple_updates':
        await periodic_updates(websocket)

    if path == '/broken_sequence':
        await periodic_updates(websocket, broken_sequence=True)

    if path == '/close_connection':
        await close_connection(websocket)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(websockets.serve(luno_server, "localhost", 8765))
    loop.run_forever()
