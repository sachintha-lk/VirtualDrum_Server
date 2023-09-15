import socket
import threading
import pygame

# Define the server host and port
HOST = 'your_server_ip'
PORT = your_server_port

# Define the allowed IP address
ALLOWED_IP = 'ip_address_1'

# Initialize Pygame mixer for audio playback
pygame.mixer.init()

# Define audio tracks for different drum values
drum_sounds = {
    'drum1': 'drum1.wav',
    'drum2': 'drum2.wav',
    # Add more drum sounds as needed
}

# Function to handle commands from the first IP
def handle_client_1(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')  # Receive and decode data
        if not data:
            break  # No more data, break the loop
        
        # Parse the received command
        try:
            commands = data.strip().split(';')
            for command in commands:
                key, value = command.split(':')
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
