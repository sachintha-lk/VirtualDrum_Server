import asyncio
import socket
import threading
import pygame
import eel
import websockets
import errno

def get_local_ip():
    # just to get the local ip address with UDP socket
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        temp_socket.connect(("8.8.8.8", 80)) # only to get the local ip address 
        local_ip = temp_socket.getsockname()[0]
    finally:
        temp_socket.close()
    return local_ip

# Define the server host and port
HOST = '0.0.0.0'
CURRENT_SERVER_LOCAL_IP = get_local_ip()
PORT = 7075
CHANNELS = 32

# Initialize Pygame mixer for audio playback
pygame.mixer.init(channels=2)

# Define audio tracks for different drum values
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
# Initialize Pygame mixer for audio playback
pygame.mixer.init()
pygame.mixer.set_num_channels(CHANNELS)

# Initialize Eel
eel.init('web')
eel.updateServerIP(CURRENT_SERVER_LOCAL_IP)
# Global variable to track the server status
server_running = False
server = None

for key in drum_sounds:
    print('loading', key)
    loadedSounds[key] = pygame.mixer.Sound(drum_sounds[key])

def playDrumSound(data):
    try:
        commands = data.split(';')
        print(commands)

        for command in commands:
            msg = command.split(':')
            key, value = msg[0], msg[1]

            if key in drum_sounds:
                volume = float(value) / 1023
                # find a free channel
                channel = pygame.mixer.find_channel(True)
                channel.set_volume(volume)
                channel.play(loadedSounds[key])
                eel.notifyInstrumentPlayed(key)  
    except Exception as e:
        print(f"Error processing command: {e}")

async def handle_client(websocket, path):
    print(f"Client connected from {websocket.remote_address}")
    while True:
        try:
            message = await websocket.recv()
            print(f"Received message from client: {message}")
            # Play a sound when a message is received in a separate thread
            if message.startswith('play'):
                message = message.replace('play:', '')
                threading.Thread(target=playDrumSound, args=(message,)).start()

            # elif message == 'BatL':
            #     # save the bat level
            #     pass
        

            # elif message == 'reqBatL':
            #     # Send the battery level to the client
            #     battery_level = 100
            #     await websocket.send(f"batteryLevel:{battery_level}")

        except websockets.exceptions.ConnectionClosedError:
            print(f"Client {websocket.remote_address} disconnected.")
            break

    

async def start_server(port):
    global server
    server = await websockets.serve(handle_client, HOST, port)
    print(f"Server started on port {port}, waiting for connections...")
    CURRENT_SERVER_LOCAL_IP = get_local_ip()
    eel.updateMessage(f"Server Listening on {CURRENT_SERVER_LOCAL_IP}:{port}")
    eel.updateServerIP(CURRENT_SERVER_LOCAL_IP)
    eel.updateServerRunningStatus(True)
    await server.wait_closed()

@eel.expose
def start_server_eel_command(port):
    global server_running
    if not server_running:
        server_running = True
        asyncio.run(start_server(port))

@eel.expose
def stop_server_eel_command():
    asyncio.run(stop_server())

async def stop_server():
    global server_running, server
    if server_running:
        server.close()
        await server.wait_closed()
        server_running = False
        eel.updateMessage("Server stopped.")
        eel.updateServerRunningStatus(False)
        print("[*] Server stopped.")

# when the eel application is closed
def on_close_callback(page, sockets):
    stop_server()
    exit(0)

def main():
    try:
        eel.start('index.html', size=(800, 600), close_callback=on_close_callback)  # Start the eel front-end
    except (SystemExit, MemoryError, KeyboardInterrupt):
        pygame.quit()
        print("Application closed.")

if __name__ == "__main__":
    main()
