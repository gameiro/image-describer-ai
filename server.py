from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/')
def trigger_job():
    # Execute another Python file or script here
    try:
        subprocess.run(['python', 'images_ai_blog_generator.py'], check=True)
        return 'Job triggered successfully!'
    except subprocess.CalledProcessError:
        return 'Error: Unable to trigger the job'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
