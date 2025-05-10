# rest_service_project/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install all required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire source directory to the container
COPY ./src /app/src

# Change working directory to the source folder
WORKDIR /app/src

# Expose port 5000 to the host
EXPOSE 5000

# Run the Flask app using Waitress WSGI server
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "main:app_dispatch"]
