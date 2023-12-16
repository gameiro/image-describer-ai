from flask import Flask, jsonify
import subprocess
import os
import threading
from queue import Queue, Empty
import sys

app = Flask(__name__)

job_status = "Not Running"
output_queue = Queue()

def execute_job():
    global job_status
    job_status = "Running"
    try:
        process = subprocess.Popen(['python', 'images_ai_blog_generator.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        for stdout_line in iter(process.stdout.readline, ''):
            output_queue.put(stdout_line.strip())

        process.stdout.close()

        for stderr_line in iter(process.stderr.readline, ''):
            output_queue.put(stderr_line.strip())

        process.stderr.close()

        return_code = process.wait()

        if return_code == 0:
            job_status = "Job completed successfully!"
        else:
            job_status = f"Error: Unable to complete the job (Return code: {return_code})"
    except Exception as e:
        job_status = f"Error: {str(e)}"

@app.route('/')
def trigger_job():
    global job_thread
    global job_status
    if 'job_thread' in globals() and job_thread.is_alive():
        return 'Job is already running!'

    job_thread = threading.Thread(target=execute_job)
    job_thread.start()
    return 'Job triggered successfully!'

@app.route('/status')
def job_status_route():
    return job_status

@app.route('/logs')
def get_logs():
    logs = []
    while True:
        try:
            log_line = output_queue.get_nowait()
            logs.append(log_line)
        except Empty:
            break
    return jsonify(logs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
