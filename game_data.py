import os
import json
from pygame import mixer


current_directory = os.getcwd()
audio_folder = os.path.join(current_directory, 'Audio')

mute = False
last_played = {"stack": -1, "exprune": -1, "thirdsound": -1, "bounty": -1, "power": -1, "pull": -1}

images = {
    'stack': os.path.join(audio_folder, 'rosh.png'),
    'exprune': os.path.join(audio_folder, 'rosh.png'),
    'lotus': os.path.join(audio_folder, 'rosh.png'),
    'bounty': os.path.join(audio_folder, 'rosh.png'),
    'power': os.path.join(audio_folder, 'rosh.png'),
    'pull': os.path.join(audio_folder, 'rosh.png'),
}


def play_overlay_and_sound(sound_file, image_path, key, minutes):
    global overlay_window
    print(f"Playing {sound_file}")
    mixer.music.load(os.path.join(audio_folder, sound_file))
    mixer.music.play()
    last_played[key] = minutes
    return "OK"


def process_game_data(minutes, seconds):
    global last_played
    global mute
    print(minutes,seconds)
    mixer.init()

    with open('config.json', 'r') as file:
        settings = json.load(file)

    if not mute:
        alerts = [
            (settings['stack_checkbox'] and minutes >= 1 and seconds == 40, None, None, 'stack'),
            (settings['exprune_checkbox'] and minutes == 6 and seconds == 30 or minutes > 6 and (minutes - 6) % 7 == 0 and seconds == 30, None, None, 'exprune'),
            (settings['thirdsound_checkbox'] and (minutes - 2) % 3 == 0 and seconds == 50 and minutes < 10, None, None, 'lotus'),
            (settings['bounty_checkbox'] and (minutes - 2) % 3 == 0 and seconds == 45, None, None, 'bounty'),
            (settings['power_checked'] and (minutes - 5) % 2 == 0 and seconds == 51, None, None, 'power'),
            (settings['pull_checkbox'] and (minutes - 1) % 2 == 0 and seconds == 10 and minutes < 10, None, None, 'pull'),
            (settings['pull_checkbox'] and seconds == 3 and minutes < 10, None, None, 'pull'), #debugger
        ]

        for alert in alerts:
            if alert[0] and (alert[1] is None or minutes >= alert[1]) and (alert[2] is None or seconds == alert[2]) and minutes != last_played[alert[3]]:
                return play_overlay_and_sound(f'{alert[3]}.wav', images[alert[3]], alert[3], minutes)

    return "OK"

