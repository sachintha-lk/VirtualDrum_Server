import eel
import sys
import threading
from queue import Queue

HOST = '0.0.0.0'
PORT = 7075
CHANNELS = 32
drum_sounds = {
    'set-1': {
        'drum1': 'drum_sounds/set1/drum1.wav',
        'drum2': 'drum_sounds/set1/drum2.wav',
        'drum3': 'drum_sounds/set1/drum3.wav',
        'drum4': 'drum_sounds/set1/drum4.wav',
    },
    'set-2': {
        'drum1': 'drum_sounds/set2/drum2.wav',
        'drum2': 'drum_sounds/set2/drum3.wav',
        'drum3': 'drum_sounds/set2/drum5.wav',
        'drum4': 'drum_sounds/set2/drum9.wav',
    },
    'set-3': {
        'drum1': 'drum_sounds/set3/drum7.wav',
        'drum2': 'drum_sounds/set3/drum8.wav',
        'drum3': 'drum_sounds/set3/drum9.wav',
        'drum4': 'drum_sounds/set3/drum10.mp3',
    },
}

server_running = False
stop_event = threading.Event()
command_queue = Queue()  #eel commands

def init_eel():
    try:
        eel.init('web')
    except Exception as e:
        print(f"Failed to initialize Eel: {e}")
        sys.exit(1)