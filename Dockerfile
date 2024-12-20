# Use the official Python 3.8 slim image as the base image
FROM python:3.8-slim

# Metadata about the image
LABEL maintainer="Wengliang Zeng" \
      description="Prometheus Nacos Service Discovery" \
      version="1.0.0"

# Set environment variables
# Ensure Python outputs everything in real-time
ENV PYTHONUNBUFFERED=1 \  
    # Prevent Python from writing .pyc files
    PYTHONDONTWRITEBYTECODE=1 \  
    # Nacos server address
    NACOS_SERVER=http://127.0.0.1:8848 \  
    # Nacos namespace
    NACOS_NAMESPACE=public \  
    # Nacos username
    NACOS_USERNAME=nacos \  
    # Nacos password
    NACOS_PASSWORD=nacos \  
    # Nacos group name
    GROUP_NAME=DEFAULT_GROUP  

# Create a non-root user named 'prometheus'
RUN useradd -m -s /bin/bash prometheus

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
# This step is separated to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies using pip
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Set proper permissions for the 'prometheus' user to the /app directory
RUN chown -R prometheus:prometheus /app

# Create Prometheus config directory and set proper permissions
RUN mkdir -p /prometheus/conf && \
    chown -R prometheus:prometheus /prometheus

# Switch to the 'prometheus' non-root user
USER prometheus

# Define a health check for the container
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8848/nacos/v1/console/health/liveness')"

# Declare a volume for Prometheus configuration
VOLUME ["/prometheus"]

# Define the command to run the application
CMD ["python", "main.py"]