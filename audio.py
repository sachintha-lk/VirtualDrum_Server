import pygame
import eel
import sys
import os
from config import CHANNELS, drum_sounds

loadedSounds = {}
pygame.mixer.init(channels=2)
pygame.mixer.set_num_channels(CHANNELS)

left_selected_set = 'set-1'
right_selected_set = 'set-2'

def select_left_set(set_name):
    global left_selected_set
    left_selected_set = set_name
    print(f"Selected set: {set_name}")

def select_right_set(set_name):
    global right_selected_set
    right_selected_set = set_name
    print(f"Selected set: {set_name}")

def resource_path(relative_path):
    global selected_set
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

for set_name, sounds in drum_sounds.items():
    loadedSounds[set_name] = {}
    for key, sound_file in sounds.items():
        try:
            print(f'Loading {set_name} - {key}')
            loadedSounds[set_name][key] = pygame.mixer.Sound(resource_path(sound_file))
        except pygame.error as e:
            print(f"Failed to load sound {sound_file}: {e}")

# print(f"Loaded {len(loadedSounds)} sound sets")

#print loaded sounds 
for set_name, sounds in loadedSounds.items():
    print(f"Set: {set_name}")
    for key, sound in sounds.items():
        print(f"  {key}: {sound}")
    
def playDrumSound(data):
    try:
        commands = data.split(';')
        print(commands)

        for command in commands:
            msg = command.split(':')
            key, value = msg[0], msg[1]
            original_key = key
            if (key == 'drum5' or key == 'drum6' or key == 'drum7' or key == 'drum8'):
                if (key == 'drum5'):
                    key = 'drum1'
                elif (key == 'drum6'):
                    key = 'drum2'
                elif (key == 'drum7'):
                    key = 'drum3'
                elif (key == 'drum8'):
                    key = 'drum4'
                
                selected_set = left_selected_set
            else: 
                selected_set = right_selected_set


            if key in loadedSounds[selected_set]:
                volume = float(value) / 1023
                channel = pygame.mixer.find_channel(True)
                print(f"DRum Playing {selected_set} - {key} at volume {value}")

                if channel:
                    channel.set_volume(volume)
                    channel.play(loadedSounds[selected_set][key])
                    eel.notifyInstrumentPlayed(original_key) # notfiy ui with original key
                else:
                    print("No free channel available")
    except Exception as e:
        print(f"Error processing command: {e}")