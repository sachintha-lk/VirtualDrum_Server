import socket
import asyncio
import threading
import time

class UDPServer(threading.Thread):
    def __init__(self, on_message=None):
        super().__init__()
        self.port = None
        self.on_message_callback = on_message
        self.server = None
        self.running = False
        self.loop = None

    def start(self, port):
        self.port = port
        super().start()  # Start the thread

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_server())

    async def handler(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(("0.0.0.0", self.port))
        self.server.setblocking(False)
        print(f"UDP server started on port {self.port}")
        
        while self.running:
            try:
                data, addr = await self.loop.run_in_executor(None, self.receive_data)
                if data:
                    message = data.decode('utf-8').strip()
                    print(f"Received: {message} from {addr}")
                    if self.on_message_callback:
                        await self.on_message_callback(message)
            except Exception as e:
                print(f"Error in UDP handler: {e}")
            await asyncio.sleep(0.01)  # Small delay to prevent tight loop

    def receive_data(self):
        try:
            return self.server.recvfrom(1024)
        except BlockingIOError:
            return None, None

    async def start_server(self):
        self.running = True
        await self.handler()

    def stop(self):  # this will raise this RuntimeError: Event loop stopped before Future completed. TODO FIX later, but it works for now
        self.running = False
        if self.server:
            self.server.close()
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop) # FIX these later
        time.sleep(1)
        self.join()  
        print("UDP server stopped")