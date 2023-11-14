from flask import Flask, render_template, request, jsonify
import time
import json
import atexit

app = Flask(__name__)

ENROLLMENTS_FILE = 'enrollments.json'

def load_enrollments():
    try:
        with open(ENROLLMENTS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_enrollments(enrollments):
    with open(ENROLLMENTS_FILE, 'w') as file:
        json.dump(enrollments, file)

enrollments = load_enrollments()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enroll', methods=['POST'])
def enroll():
    enrollment_number = request.form.get('enrollment_number').strip()  # Remove leading and trailing whitespaces

    # Validate enrollment number
    if not enrollment_number:
        return jsonify({'error': 'Enrollment number cannot be empty'})

    # Check if enrollment number already exists and remove the last entry
    existing_entry = next((e for e in reversed(enrollments) if e['number'] == enrollment_number), None)
    if existing_entry:
        enrollments.remove(existing_entry)

    enrollments.append({'number': enrollment_number, 'timestamp': time.time()})
    save_enrollments(enrollments)
    return jsonify({'success': True})


@app.route('/live_count')
def live_count():
    current_time = time.time()
    live_enrollments = [e for e in enrollments if current_time - e['timestamp'] <= 1500]  # 25 minutes in seconds
    return jsonify({'count': len(live_enrollments)})

def save_on_exit():
    save_enrollments(enrollments)

atexit.register(save_on_exit)

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True)



