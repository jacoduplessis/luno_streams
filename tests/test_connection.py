import asyncio
from unittest import TestCase
from luno_streams import Updater
from websockets.protocol import State
import logging
from concurrent import futures

logging.getLogger('luno_streams').addHandler(logging.StreamHandler())


class TestConnection(TestCase):

    def test_simple_updates(self):
        num_updates = 0

        def hook(cob, t):
            nonlocal num_updates
            num_updates += 1

        updater = Updater('XBTZAR', 'key', 'secret', [hook])
        updater.url = 'ws://localhost:8765/simple_updates'

        with self.assertRaises(futures.TimeoutError):
            asyncio.run(asyncio.wait_for(updater.run(), 5))

        self.assertEqual(num_updates, 4)

    def test_broken_sequence(self):
        # the updater should automatically close the connection and later reconnect

        updater = Updater('XBTZAR', 'key', 'secret', [])
        updater.url = 'ws://localhost:8765/broken_sequence'

        async def main():
            task = asyncio.create_task(updater.run())
            await asyncio.sleep(1)
            self.assertEqual(updater.websocket.state, State.OPEN)
            await asyncio.sleep(2)
            self.assertEqual(updater.websocket.state, State.CLOSED)
            task.cancel()

        asyncio.run(main())

    def test_disconnecting_server(self):
        # no exceptions should be raised, the coroutine just finishes
        updater = Updater('XBTZAR', 'key', 'secret', [])
        updater.url = 'ws://localhost:8765/close_connection'
        asyncio.run(updater.run())
