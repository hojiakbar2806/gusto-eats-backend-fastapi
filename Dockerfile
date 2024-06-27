# Use the latest Python image from Docker Hub
FROM python:latest

# Set working directory inside the container
WORKDIR /src

# Set environment variables to prevent Python from writing byte code and buffering output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy requirements.txt to the container
COPY requirements.txt requirements.txt

# Install dependencies from requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Copy the entire application directory to the container
COPY ./app app/
