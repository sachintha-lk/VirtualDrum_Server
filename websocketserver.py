import asyncio
import time
import websockets
import threading

class WebSocketServer(threading.Thread):
    def __init__(self, on_connect=None, on_message=None, on_disconnect=None):
        super().__init__()
        self.server = None
        self.port = None
        self.connected_clients = set()
        self.on_connect_callback = on_connect
        self.on_message_callback = on_message
        self.on_disconnect_callback = on_disconnect
        self.loop = None
        self.running = False

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_server())

    async def handler(self, websocket, path):
        self.connected_clients.add(websocket)

        print(f"Client connected")
                   
        try:
            async for message in websocket:
                print(f"Received: {message} from client")
                if self.on_message_callback:
                    await self.on_message_callback(websocket, message)

        except websockets.ConnectionClosedError:
            print(f"Connection closed error")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.connected_clients.remove(websocket)
            if self.on_disconnect_callback:
                await self.on_disconnect_callback(websocket)
            print(f"Client disconnected")

    async def start_server(self):
        self.server = await websockets.serve(self.handler, "0.0.0.0", self.port)
        print(f"WebSocket server started on port {self.port}")

        self.running = True
        while self.running:
            await asyncio.sleep(1)
        await self.server.wait_closed()

    def start(self, port):
        self.port = port
        super().start()
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.start_server(), self.loop)

    def stop(self):
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.server.close)
        time.sleep(0.1)  
        self.join()
        print("WebSocket server stopped")