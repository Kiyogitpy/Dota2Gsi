from flask import Flask, request
from menu import mute
import logging
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPoint, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import threading
import os
import json
from pygame import mixer

current_directory = os.getcwd()
audio_folder = os.path.join(current_directory, 'Audio')

last_played = {"stack": -1, "exprune": -1, "thirdsound": -1, "bounty": -1, "power": -1, "pull": -1,"lotus": -1}

images = {
    'stack': os.path.join(audio_folder, 'stack.png'),
    'exprune': os.path.join(audio_folder, 'exprune.png'),
    'lotus': os.path.join(audio_folder, 'lotus.png'),
    'bounty': os.path.join(audio_folder, 'bounty.png'),
    'power': os.path.join(audio_folder, 'power.png'),
    'pull': os.path.join(audio_folder, 'pull.png'),
}


def play_overlay_and_sound(sound_file, image_path, key, minutes):
    print(f"Playing {sound_file}")
    mixer.music.load(os.path.join(audio_folder, sound_file))
    mixer.music.play()
    last_played[key] = minutes
    return os.path.join(audio_folder, f'{key}.png')


def process_game_data(minutes, seconds):
    global last_played
    global mute
    mixer.init()

    with open('config.json', 'r') as file:
        settings = json.load(file)

    if not mute:
        
        alerts = [
            (settings['stack_checkbox'] and minutes >= 1 and seconds == 40, 'stack'),
            (settings['exprune_checkbox'] and (minutes == 6 and seconds == 30) or (minutes > 6 and (minutes - 6) % 7 == 0 and seconds == 30), 'exprune'),
            (settings['thirdsound_checkbox'] and (minutes - 2) % 3 == 0 and seconds == 50 and minutes < 10, 'lotus'),
            (settings['bounty_checkbox'] and (minutes - 2) % 3 == 0 and seconds == 45, 'bounty'),
            (settings['power_checked'] and (minutes - 5) % 2 == 0 and seconds == 51, 'power'),
            (settings['pull_checkbox'] and (minutes - 1) % 2 == 0 and seconds == 10 and minutes < 10, 'pull'),
        ]

        for alert in alerts:
            condition, key = alert
            if condition and minutes != last_played[key]:
                return play_overlay_and_sound(f'{key}.wav', images[key], key, minutes)

    return "OK"

seconds = 0
minutes = 0

app2 = QApplication([])
app = Flask(__name__)

class Overlay_pulse(QWidget):
    signal_start_animation = pyqtSignal()
    signal_update_image = pyqtSignal(str)  # New signal for updating the image
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Create a QLabel to hold the PNG image
        self.image_label = QLabel(self)
        self.setFixedSize(400, 400)
        # Center the window on the screen
        screen_center = QApplication.desktop().screen().rect().center()
        self.move(screen_center - QPoint(self.width() // 2, self.height() // 2))
        # Initialize without an image
        self.set_image("")
        
        # Create a sequence of animations
        self.animation_group = QSequentialAnimationGroup()

        # Fade-in animation
        self.fade_in_animation = QPropertyAnimation(self, b'windowOpacity')
        self.fade_in_animation.setDuration(750)
        self.fade_in_animation.setStartValue(0) 
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Fade-out animation
        self.fade_out_animation = QPropertyAnimation(self, b'windowOpacity')
        self.fade_out_animation.setDuration(750)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Add the fade-in and fade-out animations to the sequence
        self.animation_group.addAnimation(self.fade_in_animation)
        self.animation_group.addAnimation(self.fade_out_animation)
        
        self.show()

        self.signal_start_animation.connect(self.start_animation)
        self.signal_update_image.connect(self.set_image)  # Connect the update image signal

    def set_image(self, image_path: str):
        """Set or update the displayed image."""
        if image_path:
            pixmap = QPixmap(image_path)
            
            # Scale the pixmap to fit inside the widget while keeping its aspect ratio
            scaled_pixmap = pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio)
            
            self.image_label.setPixmap(scaled_pixmap)
            
            # Adjust the position of the QLabel within the QWidget to be centered
            label_x = (self.width() - scaled_pixmap.width()) // 2
            label_y = (self.height() - scaled_pixmap.height()) // 2
            self.image_label.setGeometry(label_x, label_y, scaled_pixmap.width(), scaled_pixmap.height())

    def start_animation(self):
        self.animation_group.start()
        print(f"Animation state: {self.animation_group.state()}")



overlay = Overlay_pulse() 
has_run = 0

@app.route('/', methods=['POST'])
def handle_post():
    global seconds 
    global minutes
    global has_run
    data = request.get_json()
    
    if 'map' in data and 'clock_time' in data['map']:
        clock_time = data['map']['clock_time']

        if clock_time >= 0: 
            seconds = clock_time % 60
            minutes = clock_time // 60

            response = process_game_data(minutes, seconds)
            if response and response != "OK" and has_run != seconds:
                overlay.signal_update_image.emit(response)
                overlay.signal_start_animation.emit() 
            return str(response) if response else "OK"
    return "OK"



def run_flask_app():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(port=3000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    app2.exec_()