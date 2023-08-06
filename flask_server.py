from flask import Flask, request
from game_data import process_game_data
import logging
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPoint, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import threading

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
        self.set_image("Audio/pull.png")
        
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
        print("animation started")
        self.animation_group.start()
        print(f"Animation state: {self.animation_group.state()}")
        print("animation ended")



overlay = Overlay_pulse() 
has_run = 0

@app.route('/', methods=['POST'])
def handle_post():
    global seconds 
    global minutes

    data = request.get_json()
    
    if 'map' in data and 'clock_time' in data['map']:
        clock_time = data['map']['clock_time']

        if clock_time >= 0: 
            seconds = clock_time % 60
            minutes = clock_time // 60

            if seconds == 10 or seconds == 20 or seconds == 30 or seconds == 40 or seconds == 50 or seconds == 59 and has_run != seconds:
                overlay.signal_update_image.emit("Audio/stack.png")
                overlay.signal_start_animation.emit() 
                has_run != seconds
            elif seconds == 5 or seconds == 15 or seconds == 25 or seconds == 35 or seconds == 45 or seconds == 55 and has_run != seconds:
                overlay.signal_update_image.emit("Audio/pull.png")
                overlay.signal_start_animation.emit() 
                has_run = seconds
            response = process_game_data(minutes, seconds)
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