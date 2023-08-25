# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install system dependencies required for mysqlclient
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libmariadbclient-dev build-essential

# Copy the application code into the container
COPY . .

# Install the Python dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which your application will listen
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Start the application
CMD ["flask", "run"]
