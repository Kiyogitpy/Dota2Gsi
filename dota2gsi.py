from flask import Flask, request
from pygame import mixer
import logging
import keyboard
import os

default_keybind = 'm'

# Get the current working directory
current_directory = os.getcwd()

# Create the path to the audio file inside the 'audio' folder
audio_folder = os.path.join(current_directory, 'Audio')

def read_config():
    with open('config.txt', 'r') as file:
        power_rune_enabled = file.readline().strip() == 'True'
        bounty_rune_enabled = file.readline().strip() == 'True'
        stack_alert_enabled = file.readline().strip() == 'True'
        exprune_alert_enabled = file.readline().strip() == 'True'
        thirdsound_alert_enabled = file.readline().strip() == 'True'
        mute_keybind = file.readline().strip()
        # Skipping the next three lines since they are not used
        file.readline()
        file.readline()
        volume_percent = int(file.readline().strip())  # Get the value as percentage
        mixer.music.set_volume(volume_percent / 100)
    return power_rune_enabled, bounty_rune_enabled, stack_alert_enabled, exprune_alert_enabled, thirdsound_alert_enabled, mute_keybind

app = Flask(__name__)

# Use these to keep track of the last time the sounds were played
last_stack_played = -1
last_exprune_played = -1
last_thirdsound_played = -1
bounty_rune_played = -1
power_rune_played = -1

# Flag for muting the sounds
mute_sounds = False

@app.route('/', methods=['POST'])
def handle_post():
    global last_stack_played
    global last_exprune_played
    global last_thirdsound_played
    global mute_sounds
    global bounty_rune_played
    global power_rune_played

    power_rune_enabled, bounty_rune_enabled, stack_alert_enabled, exprune_alert_enabled, thirdsound_alert_enabled, _ = read_config()
    data = request.get_json()

    # Check if the 'map' key exists in the data
    if 'map' in data and 'clock_time' in data['map']:
        clock_time = data['map']['clock_time']

        if clock_time >= 0:  # Only consider times after game has started
            seconds = clock_time % 60
            minutes = clock_time // 60

            if not mute_sounds:
                # Stack alert

                if stack_alert_enabled  and minutes >= 1 and seconds == 40 and minutes != last_stack_played:
                    print("Playing stack.wav")
                    mixer.music.load(os.path.join(audio_folder, 'stack.wav'))
                    mixer.music.play()
                    last_stack_played = minutes
                    return "OK"

                # Express Rune alert
                if exprune_alert_enabled and (minutes == 6 and seconds == 30 and minutes != last_exprune_played) or \
                (minutes > 6 and (minutes - 6) % 7 == 0 and seconds == 30 and minutes != last_exprune_played):
                    print("Playing exprune.wav")
                    mixer.music.load(os.path.join(audio_folder, 'exprune.wav'))
                    mixer.music.play()
                    last_exprune_played = minutes
                    return "OK"


                # lotus alert
                if thirdsound_alert_enabled and(minutes - 2) % 3 == 0 and seconds == 50 and minutes != last_thirdsound_played:
                    print("Playing lotus.wav")
                    mixer.music.load(os.path.join(audio_folder, 'lotus.wav'))
                    mixer.music.play()
                    last_thirdsound_played = minutes
                    return "OK"
                
                # bounty alert
                if bounty_rune_enabled and (minutes - 2) % 3 == 0 and seconds == 45 and minutes != bounty_rune_played:
                    print("Playing bounty.wav")
                    mixer.music.load(os.path.join(audio_folder, 'bounty.wav'))
                    mixer.music.play()
                    bounty_rune_played = minutes
                    return "OK"
                
                # power alert
                if power_rune_enabled and (minutes - 5) % 2 == 0 and seconds == 51 and minutes != power_rune_played:
                    print("Playing power.wav")
                    mixer.music.load(os.path.join(audio_folder, 'power.wav'))
                    mixer.music.play()
                    power_rune_played = minutes
                    return "OK"

    return "OK"

def toggle_mute():
    global mute_sounds
    mute_sounds = not mute_sounds
    
    if mute_sounds:
        print('Muted')
        mixer.music.load(os.path.join(audio_folder, 'muted.wav'))
    else:
        print('Unmuted')
        mixer.music.load(os.path.join(audio_folder, 'unmuted.wav'))

    mixer.music.play()



if __name__ == '__main__':
    mixer.init()

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    try:
        # Attempt to read the configuration
        _, _, _, _, _, mute_keybind_input = read_config()

        # If the keybind is null or some unknown value, raise an exception
        if not mute_keybind_input:
            raise ValueError('Keybind is not valid')

        # Register the hotkey and attach it to the toggle_mute function
        keyboard.on_press_key(mute_keybind_input, lambda e: toggle_mute(), suppress=False)

    except Exception as e:
        print(f'An error occurred while setting the keybind: {str(e)}')
        print(f'Falling back to the default keybind: {default_keybind}')

        # Register the hotkey using the default keybind
        keyboard.on_press_key(default_keybind, lambda e: toggle_mute(), suppress=False)


    app.run(port=3000)
