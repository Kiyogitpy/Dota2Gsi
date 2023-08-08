from flask import Flask, request
from menu import mute
import logging
from PyQt5.QtWidgets import QWidget, QLabel, QApplication,QGridLayout
from PyQt5.QtGui import QPixmap,QPainter, QColor, QFont, QPainterPath
from PyQt5.QtCore import QPoint, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import threading
import os
import json
from pygame import mixer

current_directory = os.getcwd()
audio_folder = os.path.join(current_directory, 'Audio')
image_folder = os.path.join(current_directory, 'Images')


def get_image_path(ability_name):
    """Returns the image path for a given ability."""
    # Remove the "invoker_" prefix, replace underscores with spaces, and then revert back to underscores for filename
    spell_name = ability_name.replace("invoker_", "").replace("_", " ").title().replace(" ", "_")
    
    # Append the file extension
    file_name = f"{spell_name}.webp"  # Change this to .png if your images are .png
    
    # Construct the full path
    image_path = os.path.join(image_folder, file_name)  # Assuming image_folder is a global variable
    
    return image_path


last_played = {"stack": -1, "exprune": -1, "thirdsound": -1, "bounty": -1, "power": -1, "pull": -1,"lotus": -1}

images = {
    'stack': os.path.join(image_folder, 'stack.png'),
    'exprune': os.path.join(image_folder, 'exprune.png'),
    'lotus': os.path.join(image_folder, 'lotus.png'),
    'bounty': os.path.join(image_folder, 'bounty.png'),
    'power': os.path.join(image_folder, 'power.png'),
    'pull': os.path.join(image_folder, 'pull.png'),
}


def play_overlay_and_sound(sound_file, image_path, key, minutes):
    print(f"Playing {sound_file}")
    mixer.music.load(os.path.join(audio_folder, sound_file))
    mixer.music.play()
    last_played[key] = minutes
    return os.path.join(image_folder, f'{key}.png')


def process_game_data(minutes, seconds):
    global last_played
    mixer.init()

    with open('config.json', 'r') as file:
        settings = json.load(file)

    if not settings['muted']:
        
        alerts = [
            (settings['stack_checkbox'] and minutes >= 1 and seconds == 40, 'stack'),
            (settings['exprune_checkbox'] and (minutes == 6 and seconds == 30) or (minutes > 6 and (minutes - 6) % 7 == 0 and seconds == 30), 'exprune'),
            (settings['thirdsound_checkbox'] and (minutes - 2) % 3 == 0 and seconds == 50 and not minutes > 10, 'lotus'),
            (settings['bounty_checkbox'] and (minutes - 2) % 3 == 0 and seconds == 45, 'bounty'),
            (settings['power_checked'] and (minutes - 5) % 2 == 0 and seconds == 51, 'power'),
            (settings['pull_checkbox'] and (minutes - 1) % 2 == 0 and seconds == 10 and not minutes > 10, 'pull'),
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


class InvokerAbilityWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Window attributes
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Attributes for dragging the window
        self.moving = False
        self.offset = None

        # Load position from config.json
        self.load_position()

        # Initialize the layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.ability_labels = {}
        for i, ability_name in enumerate([
            "invoker_cold_snap", 
            "invoker_ghost_walk",
            "invoker_tornado",
            "invoker_emp",
            "invoker_alacrity",
            "invoker_sun_strike",
            "invoker_forge_spirit",
            "invoker_ice_wall",
            "invoker_deafening_blast",
            "invoker_chaos_meteor"
        ]):  # Add other abilities here
            label = QLabel(self)
            image_path = get_image_path(ability_name)
            self.set_rounded_image(label, image_path)  # Use this to set the pixmap
            self.ability_labels[ability_name] = label
            row, col = divmod(i, 2)
            self.layout.addWidget(label, row, col)

        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = False
            # Save the current position to config.json
            self.save_position()

    def save_position(self):
        config = {}
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
        except:
            pass

        config["position2"] = (self.x(), self.y())

        with open("config.json", "w") as f:
            json.dump(config, f)

    def load_position(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            x, y = config.get("position2", (0, 0))
            self.move(x, y)
        except:
            pass

    def set_rounded_image(self, label, image_path):
        pixmap = QPixmap(image_path)
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)
        painter = QPainter(rounded)
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), 20, 20)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        label.setPixmap(rounded)

    def update_ability(self, ability_name, cooldown):
        # Get the corresponding label for the ability
        label = self.ability_labels[ability_name]

        # Fetch the image path
        image_path = get_image_path(ability_name)
        pixmap = QPixmap(image_path)

        # If there's a cooldown greater than 0, overlay the value
        if cooldown > 0:
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))  # Set the text color to white
            font = QFont()
            font.setPointSize(20)  # Adjust font size to your preference
            painter.setFont(font)
            painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, str(cooldown))
            painter.end()

        label.setPixmap(pixmap)

overlay = Overlay_pulse() 
has_run = 0
global_cooldowns = {}
previous_clock_time = None

@app.route('/', methods=['POST'])
def handle_post():
    global seconds 
    global minutes
    global has_run
    global previous_clock_time
    global global_cooldowns
    data = request.get_json()

    # Current in-game clock time
    current_clock_time = data['map']['clock_time']

    # Calculate elapsed time since the last update
    elapsed_time = 0
    if previous_clock_time is not None:
        elapsed_time = current_clock_time - previous_clock_time
    previous_clock_time = current_clock_time

    # Decrement cooldowns based on elapsed time
    for spell in list(global_cooldowns.keys()):  # Iterate over a copy of keys because we might modify the dictionary
        global_cooldowns[spell] -= elapsed_time
        # Remove the spell from the dictionary if its cooldown is finished
        if global_cooldowns[spell] <= 0:
            del global_cooldowns[spell]

    # Extract spells and cooldowns from ability3 and ability4 and store them
    for main_ability in ['ability3', 'ability4']:
        if main_ability in data['abilities']:
            spell_details = data['abilities'][main_ability]
            spell_name = spell_details['name']
            cooldown = spell_details['cooldown']

        # Only add the spell to the dictionary if it's not already present and its cooldown is not zero
        if spell_name not in global_cooldowns and cooldown > 0:
            global_cooldowns[spell_name] = cooldown

    # Print the spells on cooldown for debugging
    for spell, cooldown in global_cooldowns.items():
        print(f"{spell}: {cooldown}s")
        invoker_window.update_ability(spell, cooldown)

    # Handle map and clock_time
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
    invoker_window = InvokerAbilityWindow()
    app2.exec_()