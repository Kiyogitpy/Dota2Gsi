from flask import Flask, request
from menu import process_game_data

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_json()

    # Check if the 'map' key exists in the data
    if 'map' in data and 'clock_time' in data['map']:
        clock_time = data['map']['clock_time']

        if clock_time >= 0:  # Only consider times after the game has started
            seconds = clock_time % 60
            minutes = clock_time // 60

            response = process_game_data(minutes, seconds)
            return str(response) if response else "OK"
    return "OK"

if __name__ == '__main__':
    app.run(port=3000,debug=False)