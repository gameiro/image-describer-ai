from flask import Flask
import subprocess
import os
import threading

app = Flask(__name__)

job_status = "Not Running"

def execute_job():
    global job_status
    job_status = "Running"
    try:
        subprocess.run(['python', 'images_ai_blog_generator.py'], check=True)
        job_status = "Job completed successfully!"
    except subprocess.CalledProcessError:
        job_status = "Error: Unable to complete the job"

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
