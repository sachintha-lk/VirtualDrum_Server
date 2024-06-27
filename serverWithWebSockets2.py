import asyncio
import socket
import threading
import pygame
import eel
import websockets
import sys
import traceback
from queue import Queue

def get_local_ip():
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        temp_socket.connect(("8.8.8.8", 80))
        local_ip = temp_socket.getsockname()[0]
    finally:
        temp_socket.close()
    return local_ip

HOST = '0.0.0.0'
CURRENT_SERVER_LOCAL_IP = get_local_ip()
PORT = 7075
CHANNELS = 32

try:
    pygame.mixer.init(channels=2)
except pygame.error as e:
    print(f"Failed to initialize pygame mixer: {e}")
    sys.exit(1)

drum_sounds = {
    'drum1': 'drum1.wav',
    'drum2': 'drum2.wav',
    'drum3': 'drum3.wav',
    'drum4': 'drum4.wav',
    'drum5': 'drum5.wav',
    'drum6': 'drum6.wav',
    'drum7': 'drum7.wav',
    'drum8': 'drum8.wav',
    'drum9': 'drum9.wav',
}

loadedSounds = {}
pygame.mixer.set_num_channels(CHANNELS)

try:
    eel.init('web')
except Exception as e:
    print(f"Failed to initialize Eel: {e}")
    sys.exit(1)

eel.updateServerIP(CURRENT_SERVER_LOCAL_IP)

server_running = False
server = None
stop_event = threading.Event()
command_queue = Queue()

for key, sound_file in drum_sounds.items():
    try:
        print(f'Loading {key}')
        loadedSounds[key] = pygame.mixer.Sound(sound_file)
    except pygame.error as e:
        print(f"Failed to load sound {sound_file}: {e}")

def playDrumSound(data):
    try:
        commands = data.split(';')
        print(commands)

        for command in commands:
            msg = command.split(':')
            key, value = msg[0], msg[1]

            if key in loadedSounds:
                volume = float(value) / 1023
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.set_volume(volume)
                    channel.play(loadedSounds[key])
                    eel.notifyInstrumentPlayed(key)
                else:
                    print("No free channel available")
    except Exception as e:
        print(f"Error processing command: {e}")

async def handle_client(websocket, path):
    print(f"Client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received: {message}")
            if message.startswith('play:'):
                msg = message.replace('play:', '')
                await asyncio.get_event_loop().run_in_executor(None, playDrumSound, msg)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected at", websocket.remote_addreess)

async def start_server_async(port):
    global server, server_running
    try:
        server = await websockets.serve(handle_client, HOST, port, reuse_address=True)
        server_running = True
        print(f"Server started on port {port}, waiting for connections...")
        CURRENT_SERVER_LOCAL_IP = get_local_ip()
        eel.updateMessage(f"Server Listening on {CURRENT_SERVER_LOCAL_IP}:{port}")
        eel.updateServerIP(CURRENT_SERVER_LOCAL_IP)
        eel.updateServerRunningStatus(True)
        
        while server_running:
            try:
                command = await asyncio.wait_for(command_queue.get(), timeout=1)
                if command == "stop":
                    await stop_server_async()
            except asyncio.TimeoutError:
                pass

    except Exception as e:
        print(f"Error in server: {e}")
    finally:
        server_running = False
        eel.updateServerRunningStatus(False)

def start_server_thread(port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server_async(port))

@eel.expose
def start_server_eel_command(port):
    global server_running
    if not server_running:
        threading.Thread(target=start_server_thread, args=(port,)).start()

async def stop_server_async():
    global server_running, server
    try:
        if server_running:
            server.close()
            await server.wait_closed()
            
            # Close all remaining connections
            for ws in server.websockets:
                await ws.close()
            
            server_running = False
            eel.updateMessage("Server stopped.")
            eel.updateServerRunningStatus(False)
            print("[*] Server stopped.")
    except Exception as e:
        print(f"Error stopping server: {e}")
    finally:
        stop_event.set()

@eel.expose
def stop_server_eel_command():
    global server_running
    if server_running:
        command_queue.put_nowait("stop")
        if stop_event.wait(timeout=5):  # 5 second timeout
            print("Server stopped successfully")
        else:
            print("Failed to stop server within timeout period")
    else:
        print("Server is not running")

def on_close_callback(page, sockets):
    stop_server_eel_command()
    sys.exit(0)

def main():
    try:
        eel.start('index.html', size=(800, 600), close_callback=on_close_callback, block=False)
        while True:
            eel.sleep(1.0)
    except (SystemExit, MemoryError, KeyboardInterrupt):
        print("Closing application...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
    finally:
        stop_server_eel_command()
        pygame.quit()
        print("Application closed.")

if __name__ == "__main__":
    main()