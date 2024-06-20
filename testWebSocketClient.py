# import asyncio
# import websockets

# async def connect():
#     uri = "ws://127.0.0.1:7076"
#     async with websockets.connect(uri) as websocket:
#         print("Connected to the WebSocket server")

#         async def receive_message():
#             while True:
#                 message = await websocket.recv()
#                 print(f"Received message: {message}")

#         async def send_message():
#             while True:
#                 message = input("Enter message to send: ")
#                 for i in range(10):
#                     await websocket.send(message)
        
#         receive_task = asyncio.create_task(receive_message())
#         send_task = asyncio.create_task(send_message())

#         await asyncio.gather(receive_task, send_task)

# asyncio.run(connect())


import asyncio
import websockets
import time

async def send_messages():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        messages = ["Hello, World!", "How are you?", "Goodbye!"]
        for message in messages:
            await websocket.send(message)
            print(f"> {message}")

            response = await websocket.recv()
            print(f"< {response}")
            time.sleep(5)

asyncio.get_event_loop().run_until_complete(send_messages())