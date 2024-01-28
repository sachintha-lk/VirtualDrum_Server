import serial
import threading
import pygame

# Define the serial port settings
SERIAL_PORT = 'COM4'  # Change this to the appropriate serial port on your system
SERIAL_BAUDRATE = 9600

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

# Function to handle commands from the serial port
def handle_serial_commands(ser):
    while True:
        data = ser.readline().decode('utf-8').strip()
        if not data or len(data) < 5:
            break  # No more data, break the loop

        try:
            commands = data.split(';')
            print(commands)

            for command in commands:
                msg = command.split(':')
                key, value = msg[0], msg[1]

                if key in drum_sounds:
                    volume = float(value)
                    if volume < 0:
                        volume = 0
                    elif volume > 0:
                        volume = 1
                        pygame.mixer.Sound(drum_sounds[key]).set_volume(volume)
                        pygame.mixer.Sound(drum_sounds[key]).play()
        except Exception as e:
            print(f"Error processing command: {e}")

# Open the serial port
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)

print(f"[*] Listening on {SERIAL_PORT} at {SERIAL_BAUDRATE} baudrate")

# Start handling commands from the serial port
handle_serial_commands(ser)
