import socket

HEADER = 64
PORT = 7075
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECTED'
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
valid = True

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    client.send(message)
    # print(client.recv(2048).decode(FORMAT))

while valid:

    send_message = input("Enter the command: ")
    send(send_message)
    if send_message == DISCONNECT_MESSAGE:
        valid = False
