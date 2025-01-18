from flask import Flask, render_template_string, request, jsonify
import threading
import time
import os

app = Flask(__name__)

def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

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

def play_sound():
    os.system('echo \a')

def run_timer():
    global current_time, timer_running, current_level
    while timer_running and current_time > 0:
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
        if not timer_thread or not timer_thread.is_alive():
            timer_thread = threading.Thread(target=run_timer)
            timer_thread.start()
    return ('', 204)

@app.route('/pause', methods=['POST'])
def pause():
    global timer_running
    if timer_running:
        if pause_event.is_set():
            pause_event.clear()
        else:
            pause_event.set()
    return ('', 204)

@app.route('/reset', methods=['POST'])
def reset():
    global timer_running, current_level, current_time, timer_thread
    timer_running = False
    pause_event.clear()
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

@app.route('/')
def index():
    current_info = levels[current_level]
    next_info = levels[current_level + 1] if current_level + 1 < len(levels) else {"name": "Einde", "small_blind": "-", "big_blind": "-"}
    html_template = f"""
        <style>
            body {{ background-color: #66C266; font-family: Arial, sans-serif; text-align: center; color: black; }}
            h1 {{ font-size: 50px; margin: 10px 0; }}
            #timer {{ font-size: 100px; margin: 20px 0; color: white; }}
            .blinds {{ display: inline-block; width: 45%; font-size: 60px; }}
            .label {{ font-size: 30px; }}
            #next {{ font-size: 30px; color: gray; margin-top: 20px; }}
            .button-container {{ display: flex; justify-content: center; gap: 10px; margin-top: 20px; }}
            button {{ padding: 10px 20px; font-size: 18px; border: none; border-radius: 5px; cursor: pointer; }}
        </style>
        <h1 id='current-level'>{current_info['name']}</h1>
        <div id='timer'>{format_time(current_time)}</div>
        <div>
            <div class='blinds'><div class='label'>Small Blind</div><div id='small-blind'>{current_info['small_blind']}</div></div>
            <div class='blinds'><div class='label'>Big Blind</div><div id='big-blind'>{current_info['big_blind']}</div></div>
        </div>
        <div id='next'>NEXT BLINDS: {next_info['name']} - {next_info['small_blind']} / {next_info['big_blind']}</div>
        <div class='button-container'>
            <form method='POST' action='/start'><button type='submit'>Start</button></form>
            <form method='POST' action='/pause'><button type='submit'>Pause</button></form>
            <form method='POST' action='/reset'><button type='submit'>Reset</button></form>
            <form method='POST' action='/next'><button type='submit'>Next Level</button></form>
            <form method='POST' action='/previous'><button type='submit'>Previous Level</button></form>
        </div>
        <script>
            setInterval(function() {{
                fetch('/time').then(response => response.json()).then(data => {{
                    document.getElementById('timer').innerText = data.time;
                    document.getElementById('current-level').innerText = data.level;
                    document.getElementById('small-blind').innerText = data.small_blind;
                    document.getElementById('big-blind').innerText = data.big_blind;
                    document.getElementById('next').innerText = 'NEXT BLINDS: ' + data.next_level + ' - ' + data.next_small_blind + ' / ' + data.next_big_blind;
                }});
            }}, 1000);
        </script>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
