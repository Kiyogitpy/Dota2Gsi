# Dota 2 Timer and Roshan Overlay

This project provides a simple Dota 2 timer and Roshan overlay for your desktop, offering a convenient way to keep track of in-game time and events. The overlay includes a countdown timer for Roshan's respawn, and the timer plays audio alerts for different in-game events such as stacking, lotus and exp rune.

## Features

- In-game timer that tracks the current Dota 2 game time
- Roshan respawn countdown overlay with color-coding: red for the first 1/3, yellow for the second 1/3, and green for the last 3 minutes.
- Plays an audio alert when Roshan respawns
- Provides audible alerts for stacking camps, express runes, and a third customizable sound alert.
- Hotkey support: Press 'F21' to start/reset the Roshan timer, 'Page Down' to stop the script (an audio alert plays on termination), 'F22' to send the current Roshan time to chat, and 'Page Up' to mute the sounds.

## Setup and Installation

This project requires Python 3.8 or higher. Follow the steps below to set it up:

1. Clone the repository: `git clone https://github.com/Kiyogitpy/Dota2Gsi`
2. Navigate to the project directory: `cd your-directory/Dota2Gsi`
3. Install the required Python packages: `pip install -r requirements.txt`
4. Run the script: `python main.py`

Or alternativly use the release and just run the main.exe

## Usage

- After launching the script, "home" is the keybind to make the ui visible or hide it, by default f21 is the key for roshan timer.
- The timer will count down, changing colors as it progresses.
- When the countdown reaches zero, an audio alert will play, and the overlay will disappear.
- Press 'Page Down' to stop the script. An audio alert will play upon termination.
- Press 'F22' to send the current Roshan time to chat.
- Press 'M' to mute all sounds.

## License

This project is licensed under the terms of the MIT license.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

