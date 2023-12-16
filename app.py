from flask import Flask, jsonify, Response
import logging
import os
import subprocess
import concurrent.futures
from queue import Queue, Empty
import sys

app = Flask(__name__)

# Initialize logging to capture subprocess logs
logging.basicConfig(level=logging.INFO)
log_queue = Queue()

# Function to execute subprocess and capture logs
def execute_job():
    try:
        process = subprocess.Popen(['python', 'images_ai_blog_generator.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                log_queue.put(output.strip())

        return_code = process.wait()

        if return_code == 0:
            log_queue.put("Job completed successfully!")
        else:
            log_queue.put(f"Error: Unable to complete the job (Return code: {return_code})")
    except Exception as e:
        log_queue.put(f"Error: {str(e)}")

# Route to trigger job execution
@app.route('/')
def trigger_job():
    global job_thread
    if 'job_thread' in globals() and job_thread.is_alive():
        return 'Job is already running!'

    job_thread = threading.Thread(target=execute_job)
    job_thread.start()
    return 'Job triggered successfully!'

# Route to retrieve and display logs
@app.route('/logs')
def get_logs():
    logs = []
    while True:
        try:
            log_line = log_queue.get_nowait()
            logs.append(log_line)
        except Empty:
            break
    return Response('\n'.join(logs), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
