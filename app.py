from flask import Flask, render_template
from flask_socketio import SocketIO
from subprocess import Popen, PIPE
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def generate_logs():
    try:
        process = Popen(['python', 'images_ai_blog_generator.py'], stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True)

        for stdout_line in iter(process.stdout.readline, ''):
            socketio.emit('log', {'data': stdout_line})
        process.stdout.close()

        for stderr_line in iter(process.stderr.readline, ''):
            socketio.emit('log', {'data': stderr_line})
        process.stderr.close()

        return_code = process.wait()
        socketio.emit('log', {'data': f'Process completed with return code {return_code}'})
    except Exception as e:
        socketio.emit('log', {'data': f'Error: {str(e)}'})

@socketio.on('connect')
def test_connect():
    socketio.emit('log', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('trigger_job')
def trigger_job():
    socketio.start_background_task(target=generate_logs)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
