from flask import Flask, jsonify
import subprocess
import os
import threading

app = Flask(__name__)

job_status = {'status': 'idle'}

def start_job():
    global job_status
    try:
        subprocess.run(['python', 'images_ai_blog_generator.py'], check=True)
        job_status = {'status': 'Job triggered successfully!'}
    except subprocess.CalledProcessError:
        job_status = {'status': 'Error: Unable to trigger the job'}

@app.route('/')
def trigger_job():
    global job_status
    if job_status['status'] == 'idle':
        threading.Thread(target=start_job).start()
        job_status = {'status': 'Job is running...'}
        return jsonify(job_status), 200
    else:
        return jsonify({'status': 'A job is already running...'}), 409

@app.route('/status')
def get_status():
    global job_status
    return jsonify(job_status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
