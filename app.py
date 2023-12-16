from flask import Flask
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def trigger_job():
    # Return a message indicating that the job is running
    start_background_job()
    return 'Job triggered. It is running in the background.'

def start_background_job():
    # Execute another Python file or script here in the background
    subprocess.Popen(['python', 'images_ai_blog_generator.py'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
