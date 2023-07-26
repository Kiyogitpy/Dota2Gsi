from flask import Flask, request
import pygame
import logging
import keyboard

app = Flask(__name__)

# Use these to keep track of the last time the sounds were played
last_stack_played = -1
last_exprune_played = -1
last_thirdsound_played = -1

# Flag for muting the sounds
mute_sounds = False

@app.route('/', methods=['POST'])
def handle_post():
    global last_stack_played
    global last_exprune_played
    global last_thirdsound_played
    global mute_sounds

    data = request.get_json()

    # Check if the 'map' key exists in the data
    if 'map' in data and 'clock_time' in data['map']:
        clock_time = data['map']['clock_time']

        if clock_time >= 0:  # Only consider times after game has started
            seconds = clock_time % 60
            minutes = clock_time // 60

            # Only play sounds if they're not muted
            if not mute_sounds:
                # Stack alert
                if minutes >= 1 and seconds == 45 and minutes != last_stack_played:
                    print("Playing stack.wav")
                    pygame.mixer.music.load('stack.wav')
                    pygame.mixer.music.play()
                    last_stack_played = minutes
                    return "OK"

                # Express Rune alert
                if (minutes == 6 and seconds == 30 and minutes != last_exprune_played) or \
                (minutes > 6 and (minutes - 6) % 7 == 0 and seconds == 30 and minutes != last_exprune_played):
                    print("Playing exprune.wav")
                    pygame.mixer.music.load('exprune.wav')
                    pygame.mixer.music.play()
                    last_exprune_played = minutes
                    return "OK"


                # Third sound alert
                if (minutes - 2) % 3 == 0 and seconds == 30 and minutes != last_thirdsound_played:
                    print("Playing lotus.wav")
                    pygame.mixer.music.load('lotus.wav')
                    pygame.mixer.music.play()
                    last_thirdsound_played = minutes
                    return "OK"

    return "OK"

def toggle_mute(e):
    global mute_sounds
    mute_sounds = not mute_sounds
    
    if mute_sounds:
        print('Muted')
        pygame.mixer.music.load('muted.wav')
    else:
        print('Unmuted')
        pygame.mixer.music.load('unmuted.wav')

    pygame.mixer.music.play()


if __name__ == '__main__':
    pygame.mixer.init()

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # Register the hotkey and attach it to the toggle_mute function
    # In this case, 'ctrl+alt+m' is used as the hotkey
    keyboard.on_press_key('page up', toggle_mute, suppress=False)

    app.run(port=3000)
