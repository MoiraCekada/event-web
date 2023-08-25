# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install required system packages
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential pkg-config default-mysql-client curl && \
    apt-get clean

# Install Rust compiler
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Rust binaries to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the source code into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set an environment variable to define the MySQL database configuration
ENV MYSQL_HOST your_mysql_host
ENV MYSQL_PORT 3306
ENV MYSQL_USER your_mysql_user
ENV MYSQL_PASSWORD your_mysql_password
ENV MYSQL_DB your_mysql_database

EXPOSE 8080

# Set SQLAlchemy track modifications option
ENV SQLALCHEMY_TRACK_MODIFICATIONS False

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]

