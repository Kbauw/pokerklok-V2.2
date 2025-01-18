from flask import Flask, render_template_string, request, jsonify
import threading
import time
import os

app = Flask(__name__)

# Tijd formatteren
def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

# Levels
levels = [
    {"name": "Level 1", "small_blind": 25, "big_blind": 50, "duration": 10},
    {"name": "Level 2", "small_blind": 50, "big_blind": 100, "duration": 10},
    {"name": "Level 3", "small_blind": 75, "big_blind": 150, "duration": 10},
    {"name": "Level 4", "small_blind": 100, "big_blind": 200, "duration": 10},
    {"name": "PAUZE 1", "small_blind": "-", "big_blind": "-", "duration": 10},
    {"name": "Level 5", "small_blind": 150, "big_blind": 300, "duration": 10}
]

current_level = 0
current_time = levels[current_level]['duration']
timer_running = False
timer_thread = None
pause_event = threading.Event()

# Geluid afspelen
def play_sound():
    os.system('echo \a')

# Timerfunctie
def run_timer():
    global current_time, timer_running, current_level
    while timer_running:
        pause_event.wait()
        time.sleep(1)
        current_time -= 1
        if current_time <= 0:
            if current_level + 1 < len(levels):
                current_level += 1
                current_time = levels[current_level]['duration']
                play_sound()
            else:
                timer_running = False

@app.route('/')
def index():
    current_info = levels[current_level]
    next_info = levels[current_level + 1] if current_level + 1 < len(levels) else {"name": "Einde", "small_blind": "-", "big_blind": "-"}
    html_template = f"""
        <style>
            body {{ background-color: #4CAF50; font-family: Arial, sans-serif; text-align: center; color: white; }}
            h1 {{ font-size: 40px; }}
            #timer {{ font-size: 80px; margin: 20px 0; }}
            button {{ padding: 10px 20px; margin: 10px; font-size: 18px; }}
        </style>
        <h1 id='current-level'>{current_info['name']}</h1>
        <h3>Blinds: <span id='small-blind'>{current_info['small_blind']}</span> / <span id='big-blind'>{current_info['big_blind']}</span></h3>
        <h4>Volgende: <span id='next-level'>{next_info['name']}</span> - <span id='next-small'>{next_info['small_blind']}</span> / <span id='next-big'>{next_info['big_blind']}</span></h4>
        <div id='timer'>{format_time(current_time)}</div>
        <button onclick="fetch('/start', {{method: 'POST'}})">Start</button>
        <button onclick="fetch('/pause', {{method: 'POST'}})">Pauze</button>
        <button onclick="fetch('/reset', {{method: 'POST'}})">Reset</button>
        <button onclick="fetch('/next', {{method: 'POST'}})">Volgende Level</button>
        <button onclick="fetch('/previous', {{method: 'POST'}})">Vorige Level</button>
        <script>
            setInterval(function() {{
                fetch('/time').then(response => response.json()).then(data => {{
                    document.getElementById('timer').innerText = data.time;
                    document.getElementById('current-level').innerText = data.level;
                    document.getElementById('small-blind').innerText = data.small_blind;
                    document.getElementById('big-blind').innerText = data.big_blind;
                    document.getElementById('next-level').innerText = data.next_level;
                    document.getElementById('next-small').innerText = data.next_small_blind;
                    document.getElementById('next-big').innerText = data.next_big_blind;
                }});
            }}, 1000);
        </script>
    """
    return render_template_string(html_template)

@app.route('/time')
def get_time():
    current_info = levels[current_level]
    next_info = levels[current_level + 1] if current_level + 1 < len(levels) else {"name": "Einde", "small_blind": "-", "big_blind": "-"}
    return jsonify(time=format_time(current_time), level=current_info['name'], small_blind=current_info['small_blind'], big_blind=current_info['big_blind'], next_level=next_info['name'], next_small_blind=next_info['small_blind'], next_big_blind=next_info['big_blind'])

@app.route('/start', methods=['POST'])
def start():
    global timer_running, timer_thread
    if not timer_running:
        timer_running = True
        pause_event.set()
        timer_thread = threading.Thread(target=run_timer)
        timer_thread.start()
    return ('', 204)

@app.route('/pause', methods=['POST'])
def pause():
    if pause_event.is_set():
        pause_event.clear()
    else:
        pause_event.set()
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

@app.route('/next', methods=['POST'])
def next_level():
    global current_level, current_time
    if current_level + 1 < len(levels):
        current_level += 1
        current_time = levels[current_level]['duration']
    return ('', 204)

@app.route('/previous', methods=['POST'])
def previous_level():
    global current_level, current_time
    if current_level > 0:
        current_level -= 1
        current_time = levels[current_level]['duration']
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
