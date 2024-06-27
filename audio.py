import pygame
import eel
from config import CHANNELS, drum_sounds

loadedSounds = {}
pygame.mixer.init(channels=2)
pygame.mixer.set_num_channels(CHANNELS)

for key, sound_file in drum_sounds.items():
    try:
        print(f'Loading {key}')
        loadedSounds[key] = pygame.mixer.Sound(sound_file)
    except pygame.error as e:
        print(f"Failed to load sound {sound_file}: {e}")

def playDrumSound(data):
    try:
        commands = data.split(';')
        print(commands)

        for command in commands:
            msg = command.split(':')
            key, value = msg[0], msg[1]

            if key in loadedSounds:
                volume = float(value) / 1023
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.set_volume(volume)
                    channel.play(loadedSounds[key])
                    eel.notifyInstrumentPlayed(key)
                else:
                    print("No free channel available")
    except Exception as e:
        print(f"Error processing command: {e}")