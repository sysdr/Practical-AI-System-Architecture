# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .
COPY llm_switcher.py .
COPY dashboard.py .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for dashboard
EXPOSE 5000

# Default command (can be overridden)
CMD ["python", "dashboard.py"]
