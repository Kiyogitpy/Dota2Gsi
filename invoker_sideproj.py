
import json
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPainterPath

def get_image_path(ability_name):
    """Returns the image path for a given ability."""
    # Remove the "invoker_" prefix, replace underscores with spaces, and then revert back to underscores for filename
    spell_name = ability_name.replace("invoker_", "").replace("_", " ").title().replace(" ", "_")
    
    # Append the file extension
    file_name = f"{spell_name}.webp"  # Change this to .png if your images are .png
    
    # Construct the full path
    image_path = os.path.join(image_folder, file_name)  # Assuming image_folder is a global variable
    
    return image_path

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
global_cooldowns = {}
previous_clock_time = None
global previous_clock_time

#flask handle for json invoker
global global_cooldowns
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




        main etc()
        invoker_window = InvokerAbilityWindow()