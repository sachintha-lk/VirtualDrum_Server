import socket
import threading
import pygame

# Define the server host and port
HOST = '127.0.0.1'
PORT = 7070

# Define the allowed IP address
ALLOWED_IP = '127.0.0.1'

# Initialize Pygame mixer for audio playback
pygame.mixer.init()

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
    'drum10': 'drum10.wav',
    'drum11': 'drum11.wav',


    # Add more drum sounds as needed
}

# Function to handle commands from the first IP
def handle_client_1(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')  # Receive and decode data
        if not data or len(data)<5:
            break  # No more data, break the loop
        
        # Parse the received command
        try:
            commands = data.strip().split(';')
            print(commands)

            for command in commands:
                msg = command.split(':')
                # the drum msg should be sent as -   send.drum1:10
                print(msg)
                key, value = (msg[0],msg[1])
                # key = (msg[0])

                
                if key in drum_sounds:
                    volume = float(value)
                    if volume < 0:
                        volume = 0
                    elif volume > 1:
                        volume = 1
                    pygame.mixer.Sound(drum_sounds[key]).set_volume(volume)
                    pygame.mixer.Sound(drum_sounds[key]).play()
        except Exception as e:
             print(f"Error processing command: {e}")

    client_socket.close()  # Close the client socket

# Function to handle incoming connections
def handle_connection(client_socket, addr):
    if addr[0] == ALLOWED_IP:
        handle_client_1(client_socket)
    else:
        print(f"[*] Connection from {addr[0]} denied.")

# Create the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to the host and port
server.bind((HOST, PORT))

# Start listening for incoming connections
server.listen(5)

print(f"[*] Listening on {HOST}:{PORT}")

while True:
    client_socket, addr = server.accept()  # Accept a client connection
    print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
    client_handler = threading.Thread(target=handle_connection, args=(client_socket, addr))
    client_handler.start()  # Start a new thread to handle the client
