# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install Sanic and other dependencies
RUN pip install --no-cache-dir sanic
RUN pip install --no-cache-dir aiohttp
RUN pip install --no-cache-dir pillow

# Install fonts for text-in-images
# Using Symbola_hint for emoji support
RUN apt-get update && apt-get install -y fonts-symbola && rm -rf /var/lib/apt/lists/*

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# TODO: Experiment with 
# CMD ["sanic", "app.ssb:app", "--host=0.0.0.0", "--port=8000", "--workers=4"]
CMD ["python", "ssb.py"]