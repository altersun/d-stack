# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY app /app

# Install Sanic and other dependencies
COPY app/requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Install fonts for text-in-images
# Using Symbola_hint for emoji support
RUN apt-get update && apt-get install -y fonts-symbola && \
     rm -rf /var/lib/apt/lists/*

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application

CMD [\ 
"sanic",\
"d_stack.init",\
"--host=0.0.0.0",\
"--port=8000",\
"--workers=1"\
]
