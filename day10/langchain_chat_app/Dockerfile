# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .
COPY app.py .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container (if we were building a web app)
# EXPOSE 8000 

# Define environment variable for LLM model
ENV LLM_MODEL="gpt-3.5-turbo"

# Run app.py when the container launches
# CMD ["python", "app.py"]
# For interactive use, we'll override CMD in docker run
