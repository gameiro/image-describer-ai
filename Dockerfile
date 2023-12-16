# Use an official Python runtime as a parent image
FROM python:3.9

# Install Rust (and thereby Cargo)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Set up Cargo in PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Install necessary system dependencies for pngquant
RUN apt-get update && apt-get install -y \
    build-essential \
    libpng-dev \
    libheif-examples \
    && rm -rf /var/lib/apt/lists/*

# Install heic2png using pip
RUN pip install heic2png

# Install GCP AI platform
RUN pip install google-cloud-aiplatform 

# Set the working directory in the container
WORKDIR /app

# Create a temporary folder named 'temp' inside the container
RUN mkdir temp

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which your Flask app runs
EXPOSE 8080

# Define command to run the application
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0","--port=8080"]
