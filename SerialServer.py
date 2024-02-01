import serial
from threading import Thread
import pygame
import asyncio


# Define the serial port settings
SERIAL_PORT = 'COM4'  # Change this to the appropriate serial port on your system
SERIAL_BAUDRATE = 9600


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
pygame.mixer.set_num_channels(20)
for key in drum_sounds:
    print('loading',key)
    loadedSounds[key] = pygame.mixer.Sound(drum_sounds[key])

# Function to handle commands from the serial port
def handle_serial_commands(ser):
    incomeDataMoniter = Thread(target=MoniterPiezoSerialData,name="IncomeDataMoniter",args=(ser,))
    incomeDataMoniter.start()


def MoniterPiezoSerialData(ser):
    while True:
        data = ser.readline().decode('utf-8').strip()
        if not data or len(data) < 5:
            break  # No more data, break the loop
        # t = Thread(target=playDrumSound,args=(data,))
        # t.start()
        #fix
        playDrumSound(data)
        print(data)

def playDrumSound(data):
    try:
        commands = data.split(';')
        # print(commands)

        for command in commands:
            msg = command.split(':')
            key, value = msg[0], msg[1]

            if key in drum_sounds:
                volume = float(value)/1023
                loadedSounds[key].set_volume(volume)
                loadedSounds[key].play()
                while pygame.mixer.Channel(0).get_busy():
                    pass
    except Exception as e:
        print(f"Error processing command: {e}")

# Open the serial port
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)

print(f"[*] Listening on {SERIAL_PORT} at {SERIAL_BAUDRATE} baudrate")

# Start handling commands from the serial port
handle_serial_commands(ser)
while True:
    uin = input("type 'exit' to end the program\n")
    if uin=='exit':
        ser.close()
        print("serial port closed")
        exit()
