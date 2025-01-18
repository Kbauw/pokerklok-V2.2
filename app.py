from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import threading
import time
import os

app = Flask(__name__)

# Tijd formatteren
def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

# Volledige lijst van blinde levels en pauzes (duur tijdelijk op 10 seconden voor test)
levels = [
    {"name": "Level 1", "small_blind": 25, "big_blind": 50, "duration": 10},
    {"name": "Level 2", "small_blind": 50, "big_blind": 100, "duration": 10},
    {"name": "Level 3", "small_blind": 75, "big_blind": 150, "duration": 10},
    {"name": "Level 4", "small_blind": 100, "big_blind": 200, "duration": 10},
    {"name": "PAUZE 1 - Tijd voor een pauze!", "small_blind": "-", "big_blind": "-", "duration": 10},
    {"name": "Level 5", "small_blind": 150, "big_blind": 300, "duration": 10},
    {"name": "Waarschuwing", "small_blind": "Einde", "big_blind": "rebuy", "duration": 10},
    {"name": "Level 6", "small_blind": 200, "big_blind": 400, "duration": 10},
    {"name": "Level 7", "small_blind": 300, "big_blind": 600, "duration": 10},
    {"name": "PAUZE 2 - Tijd voor een pauze!", "small_blind": "-", "big_blind": "-", "duration": 10}
]

current_level = 0
current_time = levels[current_level]['duration']
timer_running = False
timer_thread = None
pause_event = threading.Event()

# Timerfunctie (aflopend)
def run_timer():
    global current_time, timer_running, current_level
    while timer_running:
        while current_time > 0 and timer_running:
            for _ in range(10):  # Controleer elke 0.1 seconde
                if not timer_running or pause_event.is_set():
                    return
                time.sleep(0.1)
            current_time -= 1
        if timer_running and current_level + 1 < len(levels):
            current_level += 1
            current_time = levels[current_level]['duration']
            play_sound()
        else:
            timer_running = False

# Geluid afspelen
def play_sound():
    os.system('echo \a')  # Simpele beep voor Windows

@app.route('/')
def index():
    current_info = levels[current_level]
    html_template = f"""
        <h1>Pokerklok 🃏⏰</h1>
        <h2>Huidig Level: {current_info['name']}</h2>
        <h3>Blinds: {current_info['small_blind']} / {current_info['big_blind']}</h3>
        <h2 id='timer'>{format_time(current_time)}</h2>
        <button onclick=\"fetch('/start', {{method: 'POST'}})\">Start</button>
        <button onclick=\"fetch('/pause', {{method: 'POST'}})\">Pauze</button>
        <button onclick=\"fetch('/reset', {{method: 'POST'}})\">Reset</button>
        <script>
            setInterval(function() {{
                fetch('/time').then(response => response.json()).then(data => {{
                    document.getElementById('timer').innerText = data.time;
                    document.querySelector('h2').innerText = 'Huidig Level: ' + data.level;
                    document.querySelector('h3').innerText = 'Blinds: ' + data.blinds;
                }});
            }}, 1000);
        </script>
    """
    return html_template

@app.route('/start', methods=['POST'])
def start():
    global timer_running, timer_thread
    if not timer_running:
        timer_running = True
        pause_event.clear()
        if timer_thread is None or not timer_thread.is_alive():
            timer_thread = threading.Thread(target=run_timer)
            timer_thread.start()
    else:
        pause_event.clear()
    return ('', 204)

@app.route('/pause', methods=['POST'])
def pause():
    global timer_running
    pause_event.set()
    timer_running = False
    return ('', 204)

@app.route('/reset', methods=['POST'])
def reset():
    global timer_running, current_level, current_time, timer_thread
    timer_running = False
    pause_event.set()
    current_level = 0
    current_time = levels[current_level]['duration']
    timer_thread = None
    return ('', 204)

@app.route('/time')
def get_time():
    current_info = levels[current_level]
    return jsonify(time=format_time(current_time), level=current_info['name'], blinds=f"{current_info['small_blind']} / {current_info['big_blind']}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
