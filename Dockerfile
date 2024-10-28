# Use a base image compatible with Raspberry Pi (ARM architecture)
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire bot code to the working directory
COPY . /app

# Define the command to run the bot
CMD ["python", "src/main.py"]
