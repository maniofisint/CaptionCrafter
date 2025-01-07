# Use the official Python image from the Docker Hub
FROM python:3.13.1-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .


# Command to run the application
CMD ["python", "bot.py"]
