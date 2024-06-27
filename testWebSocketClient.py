import asyncio
from websockets.sync.client import connect
import time
def send_messages():
    uri = "ws://127.0.0.1:7075"
    with connect(uri) as websocket:
        while True:
            message = input("Enter message to send (or 'quit' to exit): ")
            if message.lower() == 'quit':
                break

            websocket.send(message)
            send_ten_thousand_messages(websocket=websocket)
            websocket.send("play:drum3:10000")

            # response = websocket.recv()
            # print(f"Received: {response}")

    
def send_ten_thousand_messages(websocket):
    for i in range(5):
        websocket.send("play:drum1:10000")
        print("message:"+ str(i))
        time.sleep(0.05)

send_messages()



