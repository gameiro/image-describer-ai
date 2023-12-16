from flask import Flask, Response
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def trigger_job():
    # Execute another Python file or script here and capture the output
    try:
        process = subprocess.Popen(['python', 'images_ai_blog_generator.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        logs = f"STDOUT:\n{stdout}"
        
        if process.returncode == 0:  # Check if the subprocess ran successfully
            return Response(f'Job triggered successfully!\n\n{logs}', content_type='text/plain')
        else:
            return Response(f'Error: Unable to trigger the job\n\n{logs}', content_type='text/plain'), 500
    except subprocess.CalledProcessError as e:
        return f'Error: Unable to trigger the job\n{e}', 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
