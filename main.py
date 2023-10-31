import json
import os
import subprocess

import keyboard
from pygame import mixer, time


class AudioPlayer:
    def __init__(self, file_path, volume_percent):
        self.file_path = file_path
        self.volume_percent = volume_percent
        mixer.init()
        self.load_file()

    def load_file(self):
        try:
            mixer.music.load(self.file_path)
            mixer.music.set_volume(self.volume_percent / 100)
        except Exception as e:
            print(f"Error initializing the audio player: {e}")

    def play(self):
        mixer.music.play()
        time.wait(2000)  # waits for 2sec


class ProcessHandler:
    def __init__(self, python_scripts, shutdown_key):
        self.processes = []
        self.shutdown_key = shutdown_key
        for script in python_scripts:
            self.spawn_process(script)

        keyboard.add_hotkey(self.shutdown_key, self.terminate_processes)
        keyboard.wait()

    def spawn_process(self, script):
        try:
            p = subprocess.Popen(['python', script])
            self.processes.append(p)
        except Exception as errs:
            print(f'Error running {script}: {errs}')

    def terminate_processes(self):
        for process in self.processes:
            process.terminate()


def from_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config


def main():
    base_dir = os.getcwd()
    config = from_config()
    audio_file = os.path.join(
        base_dir, 'Audio', config.get('audio_file', 'goodbye.wav'))
    audio_volume = config.get('volume_percent', 100)

    player = AudioPlayer(audio_file, audio_volume)

    handler = ProcessHandler(['flask_server.py', 'menu.py'], 'page down')

    player.play()

    os._exit(0)


if __name__ == '__main__':
    main()
