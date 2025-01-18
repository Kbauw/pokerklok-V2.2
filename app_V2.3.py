from flask import Flask, render_template_string, request, jsonify
import threading
import time
from playsound import playsound  # Geluid direct afspelen

app = Flask(__name__)

def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

levels = [
    {"name": "Level 1", "small_blind": 25, "big_blind": 50, "duration": 900},
    {"name": "Level 2", "small_blind": 50, "big_blind": 100, "duration": 900},
    {"name": "Level 3", "small_blind": 75, "big_blind": 150, "duration": 900},
    {"name": "Level 4", "small_blind": 100, "big_blind": 200, "duration": 900},
    {"name": "PAUZE 1", "small_blind": "Even", "big_blind": "Pauze", "duration": 420},
    {"name": "Level 5", "small_blind": 150, "big_blind": 300, "duration": 900},
    {"name": "Waarschuwing", "small_blind": "Einde", "big_blind": "rebuy", "duration": 5},
    {"name": "Level 6", "small_blind": 200, "big_blind": 400, "duration": 900},
    {"name": "Level 7", "small_blind": 300, "big_blind": 600, "duration": 900},
    {"name": "PAUZE 2", "small_blind": "Even", "big_blind": "Pauze", "duration": 420},
    {"name": "Level 8", "small_blind": 400, "big_blind": 800, "duration": 900},
    {"name": "Level 9", "small_blind": 500, "big_blind": 1000, "duration": 900},
    {"name": "Level 10", "small_blind": 600, "big_blind": 1200, "duration": 900},
    {"name": "Level 11", "small_blind": 800, "big_blind": 1600, "duration": 900},
    {"name": "PAUZE 3", "small_blind": "Even", "big_blind": "Pauze", "duration": 420},
    {"name": "Level 12", "small_blind": 1000, "big_blind": 2000, "duration": 900},
    {"name": "Level 13", "small_blind": 1200, "big_blind": 2400, "duration": 900},
    {"name": "Level 14", "small_blind": 1500, "big_blind": 3000, "duration": 900},
    {"name": "Level 15", "small_blind": 2000, "big_blind": 4000, "duration": 900},
    {"name": "PAUZE 4", "small_blind": "Even", "big_blind": "Pauze", "duration": 420},
    {"name": "Level 16", "small_blind": 3000, "big_blind": 6000, "duration": 900},
    {"name": "Level 17", "small_blind": 4000, "big_blind": 8000, "duration": 900},
    {"name": "Level 18", "small_blind": 5000, "big_blind": 10000, "duration": 900},
    {"name": "Level 19", "small_blind": 6000, "big_blind": 12000, "duration": 900},
    {"name": "PAUZE 5", "small_blind": "Even", "big_blind": "Pauze", "duration": 420},
    {"name": "Level 20", "small_blind": 7000, "big_blind": 14000, "duration": 900},
    {"name": "Level 21", "small_blind": 8000, "big_blind": 16000, "duration": 900},
    {"name": "Level 22", "small_blind": 9000, "big_blind": 18000, "duration": 900},
    {"name": "Level 23", "small_blind": 10000, "big_blind": 20000, "duration": 900}
]


current_level = 0
current_time = levels[current_level]['duration']
timer_running = False
timer_thread = None
pause_event = threading.Event()

def play_sound():
    threading.Thread(target=playsound, args=(r'C:\Windows\Media\tada.wav',), daemon=True).start()  # Geluid afspelen zonder blokkade

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
            body {{ background-image: url('https://img.freepik.com/free-vector/flat-design-poker-table-background_23-2151047002.jpg'); background-size: cover; background-position: center; background-repeat: no-repeat; font-family: Arial, sans-serif; text-align: center; color: white; }}
            .button-container {{ display: flex; justify-content: center; gap: 50px; margin-top: 20px; }}
            button {{ padding: 15px 30px; font-size: 20px; border: none; border-radius: 10px; cursor: pointer; background-color: #28a745; color: white; transition: background-color 0.3s ease; }}
            button:hover {{ background-color: #218838; }}
            .blinds-container {{ display: flex; justify-content: center; gap: 100px; margin-top: 20px; }}
            .blinds {{ font-size: 70px; color: white; }}
            .label {{ font-size: 40px; color: white; }}
            #timer {{ font-size: 120px; margin-top: 20px; color: white; }}
            #next {{ font-size: 30px; color: gray; margin-top: 20px; }}
        </style>
        <h1 id='current-level' style='font-size: 80px;'>{current_info['name']}</h1>
        <div id='timer'>{format_time(current_time)}</div>
        <div class='blinds-container'>
            <div class='blinds'><div class='label'>Small Blind</div><div id='small-blind'>{current_info['small_blind']}</div></div>
            <div class='blinds'><div class='label'>Big Blind</div><div id='big-blind'>{current_info['big_blind']}</div></div>
        </div>
        <div id='next'>NEXT BLINDS: {next_info['name']} - {next_info['small_blind']} / {next_info['big_blind']}</div>
<div class='button-container' style="display: flex; justify-content: center; gap: 5px; margin-top: 20px;">
    <form method='POST' action='/start'><button type='submit'>Start</button></form>
    <form method='POST' action='/pause'><button type='submit'>Pause</button></form>
    <form method='POST' action='/reset'><button type='submit'>Reset</button></form>
    <form method='POST' action='/next'><button type='submit'>Next Level</button></form>
    <form method='POST' action='/previous'><button type='submit'>Previous Level</button></form>
</div>

        <script>
            function updateData() {{
                fetch('/time').then(response => response.json()).then(data => {{
                    document.getElementById('timer').innerText = data.time;
                    document.getElementById('current-level').innerText = data.level;
                    document.getElementById('small-blind').innerText = data.small_blind;
                    document.getElementById('big-blind').innerText = data.big_blind;
                    document.getElementById('next').innerText = 'NEXT BLINDS: ' + data.next_level + ' - ' + data.next_small_blind + ' / ' + data.next_big_blind;
                }});
            }}
            setInterval(updateData, 1000);
        </script>
    """
    return render_template_string(html_template)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
