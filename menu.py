import json
import os
import sys
from time import sleep

import keyboard  # import the keyboard package
from pygame import mixer
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QGridLayout, QSlider

from template import find_template_on_screen

# Get the current working directory
current_directory = os.getcwd()

# Create the path to the audio file inside the 'audio' folder
audio_folder = os.path.join(current_directory, 'Audio')

image_folder = os.path.join(current_directory, 'Images')

mute = False


class DraggableWidget(QtWidgets.QWidget):
    def __init__(self, on_move_callback=None):
        super().__init__()
        self.on_move_callback = on_move_callback

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

        # Call the callback if provided
        if self.on_move_callback:
            self.on_move_callback()


class Overlay(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 100, 100)
        self.notification_shown = False
        self.label = QtWidgets.QLabel(self)

        # Load image and convert it to QImage
        image = QImage(os.path.join(image_folder, 'rosh.png'))

        # Convert QImage to QPixmap and resize
        self.pixmap = QPixmap.fromImage(image).scaled(
            100, 100, QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(self.pixmap)

        self.original_counter = 11*60
        self.counter = self.original_counter
        self.text = QtWidgets.QLabel(self.get_time_string(), self.label)
        self.text.setStyleSheet("color: white")
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.text.setGeometry(0, 0, 100, 100)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_counter)

        self.timerActive = False

        screen_resolution = QtWidgets.QApplication.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()

        # Position window
        self.move(350, height - 250)

        # Initially hide the window
        self.hide()

        # Timer to check for the template on screen every 500ms
        self.template_check_timer = QtCore.QTimer()
        self.template_check_timer.timeout.connect(self.check_template)
        self.template_check_timer.start(1500)

        self.hotkey_timer = QtCore.QTimer()
        self.hotkey_timer.timeout.connect(self.check_hotkey)
        self.hotkey_timer.start(100)

        self.rosh_timer_keybind = 'f21'
        self.chat_keybind = 'f22'

    def set_chat_keybind(self, keybind):
        self.chat_keybind = keybind

    def set_rosh_timer_keybind(self, keybind):
        self.rosh_timer_keybind = keybind

    def check_template(self):
        # Check for the template on screen
        if find_template_on_screen():
            self.reset_timer()
            self.start_timer()

    def update_counter(self):
        self.counter -= 1
        if self.counter <= 0:
            self.reset_timer()
        elif self.counter <= 1/3*self.original_counter:
            self.text.setStyleSheet("color: green")
        elif self.counter <= 2/3*self.original_counter:
            self.text.setStyleSheet("color: yellow")
        self.text.setText(self.get_time_string())

        # Check if time_string is less than 3 minutes remaining and the notification hasn't been shown
        if self.timerActive and not self.notification_shown:
            time_string = self.get_time_string()
            if self.counter <= 180:
                self.notify_roshan_up(time_string)
                self.notification_shown = True

    def get_time_string(self):
        minutes, seconds = divmod(self.counter, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def start_timer(self):
        if not self.timerActive:
            self.timerActive = True
            self.timer.start(1000)
            self.show()

    def reset_timer(self):
        self.counter = self.original_counter
        self.timer.stop()
        self.timerActive = False
        self.text.setStyleSheet("color: white")
        self.hide()

    def check_hotkey(self):
        rosh_timer_keybind = self.rosh_timer_keybind if hasattr(
            self, 'rosh_timer_keybind') else 'f21'
        if keyboard.is_pressed(rosh_timer_keybind):
            if self.timerActive:
                self.reset_timer()
            else:
                self.start_timer()
        # Check for chat keybind press
        if keyboard.is_pressed(self.chat_keybind):
            self.print_current_time()

    def notify_roshan_up(self, time_string):
        if self.timerActive and self.counter <= 180:
            print(time_string)
            mixer.music.load(os.path.join(audio_folder, 'exprune.wav'))
            mixer.music.play()
            keyboard.press_and_release('enter')
            sleep(0.1)
            keyboard.write(
                " Roshan can be up from now and guaranteed to be up in:  " + time_string + " min")
            sleep(0.1)
            keyboard.press_and_release('enter')
            sleep(0.1)

    def print_current_time(self):
        time_string = self.get_time_string()
        if self.timerActive == True:
            print(time_string)
            keyboard.press_and_release('enter')
            sleep(0.1)
            keyboard.write(
                time_string + " Until roshan is guaranteed to spawn")
            sleep(0.1)
            keyboard.press_and_release('enter')
            sleep(0.1)


class MainWindow(DraggableWidget):
    def __init__(self, overlay):
        super().__init__(on_move_callback=self.save_config)
        self.overlay = overlay  # Store the overlay instance
        self.setWindowTitle('Welcome')
        self.setObjectName("mainwindow")
        self.setGeometry(200, 200, 400, 300)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.oldPos = QtCore.QPoint(0, 0)
        self.is_recording = False
        self.recording_for = None
        grid_layout = QGridLayout()

        try:
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                x, y = config['position']
                self.move(x, y)
        except (json.JSONDecodeError, KeyError):
            print("Error reading config.json, using default values")

        layout = QtWidgets.QVBoxLayout()
        # Exit Button
        exit_button = QtWidgets.QPushButton("✕", self)
        exit_button.setObjectName("exitButton")

        exit_button.setFixedWidth(30)
        exit_button.clicked.connect(self.close)

        # Create a horizontal layout for the header
        header_layout = QtWidgets.QHBoxLayout()

        # Create a label for the header text
        header_label = QtWidgets.QLabel("Dota 2 Timer", self)
        header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #d2f5fe;
            }
        """)
        header_layout.addWidget(
            header_label)  # Add the label to the header layout

        # Add an icon to the header layout
        icon_label = QtWidgets.QLabel(self)
        pixmap = QPixmap(os.path.join(
            image_folder, "retush.png"))  # Load the image
        # Set the image to the label, resizing as needed
        icon_label.setPixmap(pixmap.scaled(30, 30, QtCore.Qt.KeepAspectRatio))
        # Add the icon to the header layout
        header_layout.addWidget(icon_label, alignment=QtCore.Qt.AlignCenter)

        # Add exit button to the header layout
        header_layout.addWidget(exit_button, alignment=QtCore.Qt.AlignRight)

        # Add the header layout to the main layout
        layout.addLayout(header_layout)

        # Button for rosh timer keybind
        self.rosh_timer_button = QtWidgets.QPushButton(
            'Set rosh timer keybind', self)
        self.rosh_timer_button.clicked.connect(
            lambda: self.apply_keybind_button('rosh'))
        grid_layout.addWidget(self.rosh_timer_button, 0, 0)

        # Button for chat keybind
        self.chat_timer_button = QtWidgets.QPushButton(
            'Set chat keybind', self)
        self.chat_timer_button.clicked.connect(
            lambda: self.apply_keybind_button('chat'))
        grid_layout.addWidget(self.chat_timer_button, 0, 1)

        # Button for mute keybind
        self.mute_keybind_button = QtWidgets.QPushButton(
            'Set mute keybind', self)
        self.mute_keybind_button.clicked.connect(
            lambda: self.apply_keybind_button('mute'))
        grid_layout.addWidget(self.mute_keybind_button, 1, 0)

        # Button for show/hide keybind
        self.show_hide_button = QtWidgets.QPushButton(
            'Set show/hide keybind', self)
        self.show_hide_button.clicked.connect(
            lambda: self.apply_keybind_button('show_hide'))
        grid_layout.addWidget(self.show_hide_button, 1, 1)

        layout.addLayout(grid_layout)

        # checkboxes
        checkbox_layout = QGridLayout()

        self.bounty_checkbox = QtWidgets.QCheckBox('Enable Bounty Rune', self)
        self.bounty_checkbox.setChecked(True)  # Initially checked
        checkbox_layout.addWidget(
            self.bounty_checkbox, 0, 0)  # Add to grid layout

        self.power_checked = QtWidgets.QCheckBox('Enable Power rune', self)
        self.power_checked.setChecked(True)  # Initially checked
        checkbox_layout.addWidget(
            self.power_checked, 0, 1)  # Add to grid layout

        self.stack_checkbox = QtWidgets.QCheckBox('Enable Stack Alert', self)
        self.stack_checkbox.setChecked(True)  # Initially checked
        checkbox_layout.addWidget(
            self.stack_checkbox, 1, 0)  # Add to grid layout

        self.exprune_checkbox = QtWidgets.QCheckBox(
            'Enable Express Rune Alert', self)
        self.exprune_checkbox.setChecked(True)  # Initially checked
        checkbox_layout.addWidget(
            self.exprune_checkbox, 1, 1)  # Add to grid layout

        self.thirdsound_checkbox = QtWidgets.QCheckBox(
            'Enable Lotus Alert', self)
        self.thirdsound_checkbox.setChecked(True)  # Initially checked
        checkbox_layout.addWidget(
            self.thirdsound_checkbox, 0, 2)  # Add to grid layout

        self.pull_checkbox = QtWidgets.QCheckBox('Enable pull alert', self)
        self.pull_checkbox.setChecked(True)  # Initially checked
        checkbox_layout.addWidget(
            self.pull_checkbox, 1, 2)  # Add to grid layout

        # Add the grid layout to the main layout
        layout.addLayout(checkbox_layout)

        # Connect checkbox state change to configuration saving
        self.bounty_checkbox.stateChanged.connect(self.save_config)
        self.power_checked.stateChanged.connect(self.save_config)
        self.stack_checkbox.stateChanged.connect(self.save_config)
        self.exprune_checkbox.stateChanged.connect(self.save_config)
        self.thirdsound_checkbox.stateChanged.connect(self.save_config)
        self.pull_checkbox.stateChanged.connect(self.save_config)

        # Connect the buttons' clicked signals to save configuration as well
        self.rosh_timer_button.clicked.connect(self.save_config)
        self.chat_timer_button.clicked.connect(self.save_config)
        self.mute_keybind_button.clicked.connect(self.save_config)
        self.show_hide_button.clicked.connect(self.save_config)

        # Create a Volume Slider
        self.volume_slider = QSlider(QtCore.Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)  # 0 to 100 percent
        self.volume_slider.setValue(50)  # Initial value
        # Add this line in the constructor (probably in the __init__ method) after defining the volume_slider
        self.volume_slider.valueChanged.connect(self.save_volume_config)
        layout.addWidget(self.volume_slider)

        self.load_config()
        # Set Layout
        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_key_press)
        self.timer.start(100)  # Check every 100 milliseconds

    # Add this method to save the current configuration whenever the volume slider's value is changed
    def save_volume_config(self):
        self.save_config()

    # Crude way of loading/saving config, should rework to json to use pandas
    def load_config(self):
        try:
            with open('config.json', 'r') as file:
                config_data = json.load(file)
                self.bounty_checkbox.setChecked(config_data['bounty_checkbox'])
                self.power_checked.setChecked(config_data['power_checked'])
                self.stack_checkbox.setChecked(config_data['stack_checkbox'])
                self.exprune_checkbox.setChecked(
                    config_data['exprune_checkbox'])
                self.thirdsound_checkbox.setChecked(
                    config_data['thirdsound_checkbox'])
                self.pull_checkbox.setChecked(config_data['pull_checkbox'])
                self.mute_keybind = config_data['mute_keybind']
                self.rosh_keybind = config_data['rosh_keybind']
                self.chat_keybind = config_data['chat_keybind']

                volume_percent = config_data['volume_percent']
                self.volume_slider.setValue(volume_percent)
                mixer.music.set_volume(volume_percent / 100)

                self.show_hide_keybind = config_data['show_hide_keybind']
                x, y = config_data['position']
                self.move(x, y)

                self.mute_keybind_button.setText(
                    f'Mute keybind: {self.mute_keybind}')
                self.rosh_timer_button.setText(
                    f'Rosh timer keybind: {self.rosh_keybind}')
                self.chat_timer_button.setText(
                    f'Chat keybind: {self.chat_keybind}')
                self.show_hide_button.setText(
                    f'Show/Hide keybind: {self.show_hide_keybind}')

                self.overlay.set_rosh_timer_keybind(self.rosh_keybind)
                self.overlay.set_chat_keybind(self.chat_keybind)

        except Exception as e:
            print(f'An error occurred while loading the config: {str(e)}')
            print(f'Falling back to the default keybinds')

    def save_config(self):
        config_data = {
            'bounty_checkbox': self.bounty_checkbox.isChecked(),
            'power_checked': self.power_checked.isChecked(),
            'stack_checkbox': self.stack_checkbox.isChecked(),
            'exprune_checkbox': self.exprune_checkbox.isChecked(),
            'thirdsound_checkbox': self.thirdsound_checkbox.isChecked(),
            'pull_checkbox': self.pull_checkbox.isChecked(),
            'mute_keybind': getattr(self, 'mute_keybind', 'm'),
            'rosh_keybind': getattr(self, 'rosh_keybind', 'f21'),
            'chat_keybind': getattr(self, 'chat_keybind', 'f22'),
            'volume_percent': self.volume_slider.value(),
            'show_hide_keybind': getattr(self, 'show_hide_keybind', 'home'),
            "muted": mute,
            'position': [self.x(), self.y()],
        }

        with open('config.json', 'w') as file:
            json.dump(config_data, file, indent=4)

        print("Configuration saved!")

    def keyPressEvent(self, event):
        if self.is_recording:
            key = event.key()
            modifiers = event.modifiers()
            key_combination = ''

            if modifiers & Qt.ControlModifier:
                key_combination += 'Ctrl+'
            if modifiers & Qt.AltModifier:
                key_combination += 'Alt+'
            if modifiers & Qt.ShiftModifier:
                key_combination += 'Shift+'

            if Qt.Key_A <= key <= Qt.Key_Z:
                key_combination += chr(key).lower()
            elif Qt.Key_F1 <= key <= Qt.Key_F12:
                key_combination += 'F' + str(key - Qt.Key_F1 + 1)

            if key_combination != '' and key_combination[-1] != '+':
                self.apply_key_combination(key_combination)

    def apply_key_combination(self, key_combination):
        if self.recording_for == 'rosh':
            self.rosh_keybind = key_combination
            self.overlay.set_rosh_timer_keybind(key_combination)
            self.rosh_timer_button.setText(
                f'Rosh timer keybind: {key_combination}')
        elif self.recording_for == 'chat':
            self.chat_keybind = key_combination
            self.overlay.set_chat_keybind(key_combination)
            self.chat_timer_button.setText(f'Chat keybind: {key_combination}')
        elif self.recording_for == 'mute':
            self.mute_keybind = key_combination
            self.mute_keybind_button.setText(
                f'Mute keybind: {key_combination}')
        elif self.recording_for == 'show_hide':
            self.show_hide_keybind = key_combination
            self.show_hide_button.setText(
                f'Show/Hide keybind: {key_combination}')

        self.is_recording = False
        self.recording_for = None
        self.save_config()

    def apply_keybind_button(self, key_type):
        self.is_recording = True
        self.recording_for = key_type
        button = {
            'rosh': self.rosh_timer_button,
            'chat': self.chat_timer_button,
            'mute': self.mute_keybind_button,
            'show_hide': self.show_hide_button   # Add this line
        }[key_type]
        button.setText('Recording...')
        # Save the changes to the config file
        self.save_config()

    def check_key_press(self):
        global mute
        with open("config.json", "r") as file:
            config_data = json.load(file)
            volume_percent = config_data["volume_percent"] / 100
        if hasattr(self, 'show_hide_keybind') and keyboard.is_pressed(self.show_hide_keybind):
            if self.isVisible():
                self.hide()
            else:
                self.show()
        if hasattr(self, "mute_keybind") and keyboard.is_pressed(self.mute_keybind):
            if mute == False:
                mixer.music.load(os.path.join(audio_folder, 'muted.wav'))
                mixer.music.play()
                sleep(0.5)
                mixer.music.set_volume(0)
                mute = True
                config_data["muted"] = True
            else:
                mixer.music.set_volume(volume_percent)
                mixer.music.load(os.path.join(audio_folder, 'unmuted.wav'))
                mixer.music.play()
                mute = False  # Fixed line
                config_data["muted"] = False
            self.save_config()


if __name__ == "__main__":
    # Global stylesheet for the application
    mixer.init()
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        * {
            font-family: Arial, sans-serif;
            font-size: 12px;
            color: #f6e1d5; /* --text */    
        }
        #mainwindow{
            background-color:#272727;
                      }
        QLineEdit, QLabel, QCheckBox {
            padding: 5px;
        }
        QLabel {
            color: #f6e1d5; /* --text */
        }
        QLineEdit {
            border: 1px solid #080c26; /* --secondary */
            border-radius: 4px;
            background-color: #110804; /* --background */
        }
        QPushButton {
            color: #FFF; /* --text */
            background-color: #1a577a; /* --primary */
            border: 2px solid #080c26; /* --accent */
            border-radius: 4px;
            padding: 10px 20px;
            text-align: center;
        }
        QPushButton:hover {
            background-color: #2cceb9; /* --accent */
        }
        #exitButton {
                color: #d2f5fe;
                font-weight: bold;
                background-color: transparent;
                border: none;
                font-size: 20px;
        }
        #exitButton:hover {
            color: #ec0445;
        }
        QCheckBox {
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 13px;
            height: 13px;
            border: 1px solid #080c26; /* --secondary */
            border-radius: 3px;
            background-color: #110804; /* --background */
        }
        QCheckBox::indicator:checked {
            background-color: #2cceb9; /* --accent */
        }
    """)

    icon_path = os.path.abspath("Audio/retush.png")
    app_icon = QIcon()
    app_icon.addFile(icon_path, QSize(16, 16))
    app.setWindowIcon(app_icon)
    overlay = Overlay()
    config_menu = MainWindow(overlay)
    config_menu.show()
    sys.exit(app.exec_())  # Start the application's main loop
