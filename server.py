import socket
import threading
import pygame
import eel
import errno 

def get_local_ip():
    # just to get the local ip address
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

# Define the allowed IP address
# ALLOWED_IP = '192.168.236.105'

# Initialize Pygame mixer for audio playback
pygame.mixer.init(channels=2)

# Define audio tracks for different drum values
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
    # Add more drum sounds as needed
}
loadedSounds=dict()
 # Initialize Pygame mixer for audio playback
pygame.mixer.init()
pygame.mixer.set_num_channels(CHANNELS)
# Initialize Eel
eel.init('web')
eel.updateServerIP(CURRENT_SERVER_LOCAL_IP)
# Global variable to track the server status
server_running = False
server_thread = None

for key in drum_sounds:
    print('loading',key)
    loadedSounds[key] = pygame.mixer.Sound(drum_sounds[key])




def playDrumSound(data):
    try:
        commands = data.split(';')
        print(commands)

        for command in commands:
            msg = command.split(':')
            key, value = msg[0], msg[1]

            if key in drum_sounds:
                volume = float(value)/1023
                # find a free channel
                channel = pygame.mixer.find_channel(True)
                channel.set_volume(volume)
                channel.play(loadedSounds[key])
                eel.notifyInstrumentPlayed(key)  
    except Exception as e:
        print(f"Error processing command: {e}")

# Function to handle commands from the first IP
def handle_client_1(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')  # Receive and decode data
        if not data or len(data)<5:
            break  # No more data, break the loop

        print(data)
        #trim the data
        data = data.strip()
        
        # Parse the received command
        playDrumSound(data)

    client_socket.close()  # Close the client socket

# Function to handle incoming connections
def handle_connection(client_socket, addr):
    # if addr[0] == ALLOWED_IP:
    if True:
        handle_client_1(client_socket)
    else:
        print(f"[*] Connection from {addr[0]} denied.")

# Function to run the server loop
def server_loop(server):
    while server_running:
        try:
            client_socket, addr = server.accept()  # Accept a client connection
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
            eel.updateMessage(f"Accepted client connection from {addr[0]}:{addr[1]}")
            client_handler = threading.Thread(target=handle_connection, args=(client_socket, addr))
            client_handler.start()  # Start a new thread to handle the client
        except OSError as e:
                    if e.errno == errno.ENOTSOCK:
                        # print("Socket operation error as the server is stopped.")
                        continue
@eel.expose
def start_server(port):
    global server_running, server, server_thread

    if not server_running:
        # Create the server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # get the local ip of the server
        CURRENT_SERVER_LOCAL_IP = get_local_ip()
        # Bind the server to the host and port
        server.bind((CURRENT_SERVER_LOCAL_IP, port))

        # Start listening for incoming connections
        server.listen(5)

        print(f"[*] Listening on {CURRENT_SERVER_LOCAL_IP}:{port}")
        eel.updateMessage(f"Server Listening on {CURRENT_SERVER_LOCAL_IP}:{port}")
        eel.updateServerIP(CURRENT_SERVER_LOCAL_IP)
        eel.updateServerRunningStatus(True)

        server_running = True

        # Start server in a new thread
        server_thread = threading.Thread(target=server_loop, args=(server,))
        server_thread.start()

@eel.expose
def stop_server():
    global server_running, server

    if server_running:
        server_running = False
        server.close()
        eel.updateMessage("Server stopped.")
        eel.updateServerRunningStatus(False)

        print("[*] Server stopped.")

# when the eel application is closed
def on_close_callback(page, sockets):
    stop_server()
    exit(0)


# Start the Eel application
eel.start('index.html', size=(600, 500))

# keep the script running and listens for exit events 
while True:
    try:
        eel.sleep(1)
    except (SystemExit, KeyboardInterrupt):
        on_close_callback(None, None)