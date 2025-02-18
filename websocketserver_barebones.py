#!/usr/bin/env python

import asyncio
from websockets.server import serve

async def echo(websocket):
    async for message in websocket:
        print(message)

async def main():
    async with serve(echo, "0.0.0.0", 7075):
        await asyncio.Future()  # run forever

asyncio.run(main())