import keyboard
from subprocess import Popen
from pygame import mixer, time
import os
import json

# Get the current working directory
current_directory = os.getcwd()

# Create the path to the audio file inside the 'audio' folder
audio_folder = os.path.join(current_directory, 'Audio')
audio_file_path = os.path.join(audio_folder, 'goodbye.wav')

mixer.init()

try:
    with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            mixer.music.set_volume = config['volume_percent'] / 100
except (json.JSONDecodeError, KeyError):
    print("Error reading config.json, using default values")

# List to keep track of all subprocesses
processes = []

# Function to terminate all processes
def terminate_processes():
    for process in processes:
        process.terminate()

    # Load and play the sound
    mixer.music.load(audio_file_path)
    mixer.music.play()

    # Allow time for sound to play
    time.wait(2000)  # waits for 5000 milliseconds

    # Terminate main script
    os._exit(0)

# Create a hotkey that will call terminate_processes when 'page down' is pressed
keyboard.add_hotkey('page down', terminate_processes)

# Run your scripts as subprocesses and append them to the processes list
processes.append(Popen(['python', 'client.py']))
processes.append(Popen(['python', 'flask_server.py']))
processes.append(Popen(['python', 'menu.py']))

# Keep the script running
keyboard.wait()