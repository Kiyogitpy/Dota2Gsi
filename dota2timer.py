from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
import keyboard  # import the keyboard package

class Overlay(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 100, 100)

        self.label = QtWidgets.QLabel(self)

        # Load image and convert it to QImage
        image = QtGui.QImage("rosh.png")

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
        keyboard.add_hotkey('f22', self.print_current_time)

    def update_counter(self):
        self.counter -= 1
        if self.counter <= 0:
            self.reset_timer()
        elif self.counter <= 1/3*self.original_counter:
            self.text.setStyleSheet("color: green")
        elif self.counter <= 2/3*self.original_counter:
            self.text.setStyleSheet("color: yellow")
        self.text.setText(self.get_time_string())

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
        if keyboard.is_pressed('f21'):
            if self.timerActive:
                self.reset_timer()  # the sound does not play here anymore
            else:
                self.start_timer()

    def print_current_time(self):
        time_string = self.get_time_string()
        if self.timerActive == True:
            print(time_string)
            keyboard.press_and_release('enter')
            keyboard.write(time_string)
            keyboard.press_and_release('enter')
        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    overlay = Overlay()
    app.exec_()
