import time
import eel
import sys
import traceback
import pygame
import asyncio
import threading
import audio
from config import init_eel
import socket
from UDPServer import UDPServer
from websocketserver import WebSocketServer

# Global variables to control the server state
start_server_flag = False
stop_server_flag = False
server_port = 7075
server_type = "WebSocket"  # Default to WebSocket. Can be "UDP" or "WebSocket"
global server_thread
server_thread = None
server_local_ip = None


# GLOVE Status
left_glove_is_connected = False
right_glove_is_connected = False

left_glove_ip_port = [None, None]
right_glove_ip_port = [None, None]

left_glove_battery = 0
right_glove_battery = 0


def get_local_ip():
    # Just to get the local IP address with UDP socket
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        temp_socket.connect(("8.8.8.8", 80))  # Only to get the local IP address
        local_ip = temp_socket.getsockname()[0]
    finally:
        temp_socket.close()
    return local_ip

def start_server_eel_command(port):
    global start_server_flag, server_port
    server_port = port
    start_server_flag = True
    print(f"Received command to start server on port {port}")

def stop_server_eel_command():
    global stop_server_flag, left_glove_is_connected, right_glove_is_connected, left_glove_ip_port, right_glove_ip_port
    stop_server_flag = True
    print("Received command to stop server")
    left_glove_is_connected = False
    right_glove_is_connected = False
    left_glove_ip_port = [None, None]
    right_glove_ip_port = [None, None]
    eel.updateGloveStatus('0', left_glove_ip_port[0], left_glove_ip_port[1], False)()
    eel.updateGloveStatus('1', right_glove_ip_port[0], right_glove_ip_port[1], False)()


def change_server_type(new_type):
    global server_type
    if new_type in ["UDP", "WebSocket"]:
        server_type = new_type
        print(f"Changed server type to {new_type}")
    else:
        print(f"Invalid server type: {new_type}")

def updateBatteryLevel(level, glove):
    eel.updateBatteryLevel(level, glove)

def on_close_callback(page, sockets):
    print("Eel close callback triggered")
    global stop_server_flag
    stop_server_flag = True
    sys.exit(0)

def updateBatteryLevelFromMessage(message ):
    global left_glove_battery, right_glove_battery
    message = message.replace('bat:', '')
    glove, battery = message.split(':')
    if glove == '0':
        left_glove_battery = battery
        updateBatteryLevel(battery, 'left')
    elif glove == '1':
        right_glove_battery = battery
        updateBatteryLevel(battery, 'right')


# For the WebSocket server
async def on_message_callback_ws(websocket, message):

    if message.startswith('play:'):
        message = message.replace('play:', '')
        audio.playDrumSound(message)
        eel.notifyInstrumentPlayed(message)
    elif message.startswith('bat:'):
        #message would be 'bat:0:70' for example
        updateBatteryLevelFromMessage(message)

    elif message.startswith('batReq'):
        # print("Received battery request")
        global left_glove_battery, right_glove_battery
        await websocket.send(f"batLevels:{left_glove_battery}:{right_glove_battery}")
    elif message.startswith('con'):
        global left_glove_ip_port, right_glove_ip_port, left_glove_is_connected, right_glove_is_connected
        glove = message.replace('con:', '')
        if glove == '0':
           left_glove_is_connected = True
           left_glove_ip_port = websocket.remote_address
           print(websocket.remote_address[0], websocket.remote_address[1])
           eel.updateGloveStatus(glove, websocket.remote_address[0], websocket.remote_address[1], True)
        elif glove == '1':
           right_glove_is_connected = True
           right_glove_ip_port = websocket.remote_address
           eel.updateGloveStatus(glove, websocket.remote_address[0], websocket.remote_address[1], True)

# For the UDP server
async def on_message_callback_udp(message, addr):
    if message.startswith('play:'):
        message = message.replace('play:', '')
        audio.playDrumSound(message)
        eel.notifyInstrumentPlayed(message)
    elif message.startswith('bat:'):
        #message would be 'bat:0:70' for example
        updateBatteryLevelFromMessage(message)
    elif message.startswith('batReq:'):
        global left_glove_battery, right_glove_battery
        await server_thread.send_message(f"bat:{left_glove_battery}:{right_glove_battery}", addr)
    elif message.startswith('con'):
        global left_glove_ip_port, right_glove_ip_port, left_glove_is_connected, right_glove_is_connected
        glove = message.replace('con:', '')
        # not sure if this working didnt test yet
        if glove == '0':
            left_glove_is_connected = True
            left_glove_ip_port = addr
            # eel.updateGloveStatus(glove, addr, True)()
        elif glove == '1':
            right_glove_is_connected = True
            right_glove_ip_port = addr
            # eel.updateGloveStatus(glove, addr, True)()


# websocket on disconnect callback
async def on_disconnect_callback_ws(websocket):
    global left_glove_is_connected, right_glove_is_connected, left_glove_ip_port, right_glove_ip_port
    address = websocket.remote_address
    if address == left_glove_ip_port:
        left_glove_is_connected = False
        left_glove_ip_port = [None, None]
        eel.updateGloveStatus('0', left_glove_ip_port[0], left_glove_ip_port[1], False)()
    elif address == right_glove_ip_port:
        right_glove_is_connected = False
        right_glove_ip_port = [None, None]
        eel.updateGloveStatus('1', right_glove_ip_port[0], right_glove_ip_port[1], False)()

    

# ws_server = websocketserver.WebSocketServer(on_message=on_message_callback_ws)
# udp_server = UDPServer.UDPServer(on_message=on_message_callback_udp)

# Thread class to run asyncio event loop
class AsyncioThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._running = True
        self._stop_event = threading.Event()

    async def server_listener(self):
        global start_server_flag, stop_server_flag, server_port, server_type, server_thread
        while self._running and not self.stopped():
            # print("ServerListener running")
            if start_server_flag:
                start_server_flag = False
                if server_thread and server_thread.is_alive():
                    server_thread.stop()
                    server_thread.join()
                if server_type == "UDP":
                    server_thread = UDPServer(on_message=on_message_callback_udp)
                elif server_type == "WebSocket":
                    server_thread = WebSocketServer(on_message=on_message_callback_ws, on_disconnect=on_disconnect_callback_ws)
               
                server_thread.start(server_port)
                eel.updateMessage(f"{server_type} server started on port {server_port}")()
                eel.updateServerRunningStatus(True)()
            if stop_server_flag:
                stop_server_flag = False
                if server_thread and server_thread.is_alive():
                    server_thread.stop()
                    time.sleep(0.1)
                    server_thread.join()
                    eel.updateMessage(f"{server_type} server stopped")()
                    eel.updateServerRunningStatus(False)()
                    server_thread = None
            await asyncio.sleep(1)

    def run(self):
        self.loop.run_until_complete(self.server_listener())
        self.loop.close()

    def stop(self):
        self._running = False
        self._stop_event.set()
        self.loop.call_soon_threadsafe(self.loop.stop)

    def stopped(self):
        return self._stop_event.is_set()


def eel_thread():
    init_eel()
    global server_local_ip
    print("Starting Eel...")
    eel.start('index.html', size=(800, 600), close_callback=on_close_callback, block=False)
    print("Eel started.")
    server_local_ip = get_local_ip()
    eel.updateServerIP(server_local_ip)

def main():
    global asyncio_thread

    try:
        print("Starting main function...")

        # Start asyncio event loop in a separate thread
        asyncio_thread = AsyncioThread()
        asyncio_thread.start()

        # Start Eel in the main thread
        eel_thread()

        print("Entering main loop...")
        # Keep the main thread alive
        while True:
            eel.sleep(1.0)
    except (SystemExit, MemoryError, KeyboardInterrupt):
        print("Closing application due to exit signal...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
    finally:
        print("Shutting down server...")
        if server_thread and server_thread.is_alive():
            server_thread.stop()
            server_thread.join()

        if asyncio_thread:
            asyncio_thread.stop()
            time.sleep(0.1)

            asyncio_thread.join() # stop the asyncio serverlistener loop

        print("Quitting Pygame...")
        pygame.quit()
        print("Application closed.")
        exit(0)

if __name__ == "__main__":
    # Expose the start and stop commands to Eel
    eel.expose(start_server_eel_command)
    eel.expose(stop_server_eel_command)
    eel.expose(change_server_type)
    
    main()
