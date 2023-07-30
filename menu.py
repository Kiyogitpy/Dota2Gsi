from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QLineEdit
import keyboard  # import the keyboard package
from time import sleep
import os


# Get the current working directory
current_directory = os.getcwd()

# Create the path to the audio file inside the 'audio' folder
audio_folder = os.path.join(current_directory, 'Audio')



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
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 100, 100)
        self.notification_shown = False
        self.label = QtWidgets.QLabel(self)

        # Load image and convert it to QImage
        image = QtGui.QImage(os.path.join(audio_folder, 'rosh.png'))

        # Convert QImage to QPixmap and resize
        self.pixmap = QtGui.QPixmap.fromImage(image).scaled(100, 100, QtCore.Qt.KeepAspectRatio)
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

        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile("roshan.wav")))

        # Initially hide the window
        self.hide()

        self.hotkey_timer = QtCore.QTimer()
        self.hotkey_timer.timeout.connect(self.check_hotkey)
        self.hotkey_timer.start(100)

        self.rosh_timer_keybind = 'f21'
        self.chat_keybind = 'f22'
    def set_chat_keybind(self, keybind):
        self.chat_keybind = keybind
    def set_rosh_timer_keybind(self, keybind):
        self.rosh_timer_keybind = keybind

    
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
        rosh_timer_keybind = self.rosh_timer_keybind if hasattr(self, 'rosh_timer_keybind') else 'f21'
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
            keyboard.press_and_release('enter')
            sleep(0.1)
            keyboard.write(" Roshan can be up from now and guaranteed to be up in:  " + time_string + " min")
            sleep(0.1)
            keyboard.press_and_release('enter')
            sleep(0.1)

    def print_current_time(self):
        time_string = self.get_time_string()
        if self.timerActive == True:
            print(time_string)
            keyboard.press_and_release('enter')
            sleep(0.1)
            keyboard.write(time_string + " Until roshan is guaranteed to spawn")
            sleep(0.1)
            keyboard.press_and_release('enter')
            sleep(0.1)

class MainWindow(DraggableWidget):
    def __init__(self, overlay):
        super().__init__(on_move_callback=self.save_config)
        self.overlay = overlay  # Store the overlay instance
        self.setWindowTitle('Welcome')
        self.setStyleSheet("background-color: #01242d")
        self.setGeometry(200, 200, 400, 300)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        try:
            with open('config.txt', 'r') as config_file:
                lines = config_file.readlines()
                x, y = map(int, lines[-1].strip().split(',')) # Get the last line for the x and y positions
                self.move(x, y)
        except (ValueError, IndexError):
            print("Error reading config.txt, using default values")
            # Set default x and y values if needed

        layout = QtWidgets.QVBoxLayout()
        # Exit Button
        exit_button = QtWidgets.QPushButton("✕", self)
        exit_button.setStyleSheet("""
            QPushButton {
                color: #d2f5fe;
                font-weight: bold;
                background-color: transparent;
                border: none;
                font-size: 20px;
            }
            QPushButton:hover {
                color: #ec0445;
            }
        """)
        exit_button.setFixedWidth(30)
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button, alignment=QtCore.Qt.AlignRight)


        # Button for rosh timer keybind
        self.rosh_timer_button = QtWidgets.QPushButton('Set rosh timer keybind', self)
        self.rosh_timer_button.clicked.connect(lambda: self.apply_keybind_button('rosh'))
        layout.addWidget(self.rosh_timer_button)

        # Button for chat keybind
        self.chat_timer_button = QtWidgets.QPushButton('Set chat keybind', self)
        self.chat_timer_button.clicked.connect(lambda: self.apply_keybind_button('chat'))
        layout.addWidget(self.chat_timer_button)

        # Button for mute keybind
        self.mute_keybind_button = QtWidgets.QPushButton('Set mute keybind', self)
        self.mute_keybind_button.clicked.connect(lambda: self.apply_keybind_button('mute'))
        layout.addWidget(self.mute_keybind_button)


        self.stack_checkbox = QtWidgets.QCheckBox('Enable stack alert', self)
        self.stack_checkbox.setChecked(True)  # Initially checked
        layout.addWidget(self.stack_checkbox)

        self.exprune_checkbox = QtWidgets.QCheckBox('Enable Express Rune alert', self)
        self.exprune_checkbox.setChecked(True)  # Initially checked
        layout.addWidget(self.exprune_checkbox)

        self.thirdsound_checkbox = QtWidgets.QCheckBox('Enable Third Sound alert', self)
        self.thirdsound_checkbox.setChecked(True)  # Initially checked
        layout.addWidget(self.thirdsound_checkbox)

        # Connect checkbox state change to configuration saving
        self.stack_checkbox.stateChanged.connect(self.save_config)
        self.exprune_checkbox.stateChanged.connect(self.save_config)
        self.thirdsound_checkbox.stateChanged.connect(self.save_config)

        # Connect the buttons' clicked signals to save configuration as well
        self.rosh_timer_button.clicked.connect(self.save_config)
        self.chat_timer_button.clicked.connect(self.save_config)
        self.mute_keybind_button.clicked.connect(self.save_config)
        
        self.load_config() 
        # Set Layout
        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_key_press)
        self.timer.start(100)  # Check every 100 milliseconds

    def load_config(self):
        try:
            with open('config.txt', 'r') as file:
                lines = file.readlines()
                self.stack_checkbox.setChecked(lines[0].strip() == 'True')
                self.exprune_checkbox.setChecked(lines[1].strip() == 'True')
                self.thirdsound_checkbox.setChecked(lines[2].strip() == 'True')
                self.mute_keybind = lines[3].strip()
                self.rosh_keybind = lines[4].strip()
                self.chat_keybind = lines[5].strip()
                x, y = map(int, lines[6].strip().split(','))
                self.move(x, y)

                # Apply the loaded keybinds to buttons' text
                self.mute_keybind_button.setText(f'Mute keybind: {self.mute_keybind}')
                self.rosh_timer_button.setText(f'Rosh timer keybind: {self.rosh_keybind}')
                self.chat_timer_button.setText(f'Chat keybind: {self.chat_keybind}')

                # Apply the keybinds to the overlay
                self.overlay.set_rosh_timer_keybind(self.rosh_keybind)
                self.overlay.set_chat_keybind(self.chat_keybind)
        except (ValueError, IndexError, FileNotFoundError):
            print("Error reading config.txt, using default values")
    
    
    def save_config(self):
        config_lines = [
            str(self.stack_checkbox.isChecked()) + '\n',
            str(self.exprune_checkbox.isChecked()) + '\n',
            str(self.thirdsound_checkbox.isChecked()) + '\n',
            (self.mute_keybind if hasattr(self, 'mute_keybind') else 'm') + '\n',
            (self.rosh_keybind if hasattr(self, 'rosh_keybind') else 'f21') + '\n',
            (self.chat_keybind if hasattr(self, 'chat_keybind') else 'f22') + '\n',
            f'{self.x()},{self.y()}\n'
        ]
        
        with open('config.txt', 'w') as file:
            file.writelines(config_lines)
        
        print("Configuration saved!")

    

    def apply_keybind_button(self, key_type):
        key = QtWidgets.QInputDialog.getText(self, 'Keybind', f'Press the key you want to use for the {key_type} keybind')[0]
        
        if key_type == 'rosh':
            self.rosh_keybind = key
            self.overlay.set_rosh_timer_keybind(key)
            self.rosh_timer_button.setText(f'Rosh timer keybind: {key}')
        elif key_type == 'chat':
            self.chat_keybind = key
            self.overlay.set_chat_keybind(key)
            self.chat_timer_button.setText(f'Chat keybind: {key}')
        elif key_type == 'mute':
            self.mute_keybind = key
            self.mute_keybind_button.setText(f'Mute keybind: {key}')

        # Save the changes to the config file
        self.save_config()



    def check_key_press(self):
        if keyboard.is_pressed('home'):
            if self.isVisible():
                self.hide()
            else:
                self.show()



if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    # Global stylesheet for the application
    app.setStyleSheet("""
        * {
            font-family: Arial, sans-serif;
            font-size: 12px;
            color: #FFF;
        }
        QLineEdit, QLabel, QCheckBox {
            padding: 5px;
        }
        QLabel {
            color: #d2f5fe;
        }
        QLineEdit {
            border: 1px solid #231901;
            border-radius: 4px;
            background-color: #01242d;
        }
        QPushButton {
            color: #d2f5fe;
            background-color: #fc5122;
            border: 1px solid #fc5122;
            border-radius: 4px;
            padding: 10px 20px;
            text-align: center;
        }
        QPushButton:hover {
            background-color: #ec0445;
        }
        QCheckBox {
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 13px;
            height: 13px;
            border: 1px solid #231901;
            border-radius: 3px;
            background-color: #01242d;
        }
        QCheckBox::indicator:checked {
            background-color: #fc5122;
        }
    """)

    overlay = Overlay()
    config_menu = MainWindow(overlay)
    config_menu.show()
    app.exec_()