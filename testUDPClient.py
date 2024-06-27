import socket
import time

UDP_IP = "127.0.0.1"  # IP address of the server
UDP_PORT = 7075       # Port number of the server

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_single_message():
    message = "play:drum1:10000"
    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
    print(f"Sent message: {message}")

def send_multiple_messages(count):
    i = 1
    for _ in range(count):
        message = f"play:drum1:{i}"
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        time.sleep(0.001)  # Sleep for 1ms to achieve approximately 1000 messages per second
        i = i + 1
    print(f"Sent {count} messages")

# Uncomment one of these lines to test
# send_single_message()
send_multiple_messages(1000)
