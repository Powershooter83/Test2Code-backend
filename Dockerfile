# Use the official Python 3.11 image as the base image
FROM python:3.11-slim
LABEL authors="raphael"

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory contents into the container's /app directory
COPY src/ .

# Create the logs directory
RUN mkdir -p /app/logs

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
