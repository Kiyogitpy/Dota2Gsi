import keyboard
from subprocess import Popen
from pygame import mixer, time
import os

# Get the current working directory
current_directory = os.getcwd()

# Create the path to the audio file inside the 'audio' folder
audio_folder = os.path.join(current_directory, 'Audio')
audio_file_path = os.path.join(audio_folder, 'goodbye.wav')

mixer.init()

with open('config.txt', 'r') as file:
    lines = file.readlines() # Read all lines into a list
    volume_percent = int(lines[8].strip()) # Get the value from the 7th line (index 6)
    mixer.music.set_volume(volume_percent / 100) # Set the volume in Pygame as a fraction

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
processes.append(Popen(['python', 'Menu.py']))
processes.append(Popen(['python', 'dota2gsi.py']))

# Keep the script running
keyboard.wait()
