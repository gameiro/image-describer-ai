# Use an official Python runtime as a parent image
FROM python:3.9

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libheif-examples \
    && rm -rf /var/lib/apt/lists/*
    
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install image converter
RUN pip install heic2png

# Expose the port on which your Flask app runs
EXPOSE 8080

# Define command to run the application
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0","--port=8080"]
