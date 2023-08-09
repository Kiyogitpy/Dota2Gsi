import keyboard
from subprocess import Popen
from pygame import mixer, time
import os
import json


current_directory = os.getcwd()
audio_folder = os.path.join(current_directory, 'Audio')
audio_file_path = os.path.join(audio_folder, 'goodbye.wav')

mixer.init()

try:
    with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            mixer.music.set_volume = config['volume_percent'] / 100
except (json.JSONDecodeError, KeyError):
    print("Error reading config.json, using default values")

processes = []

def terminate_processes():
    for process in processes:
        process.terminate()

    
    mixer.music.load(audio_file_path)
    mixer.music.play()

    
    time.wait(2000)  # waits for 2sec

    
    os._exit(0)


keyboard.add_hotkey('page down', terminate_processes)


processes.append(Popen(['python', 'flask_server.py']))
processes.append(Popen(['python', 'menu.py']))

keyboard.wait()