# Dockerfile for FastAPI service
FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install virtualenv
RUN pip install virtualenv

# Create a virtual environment
RUN python -m virtualenv venv

# Install dependencies from requirements.txt within the virtual environment
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Command to run FastAPI server within the virtual environment
CMD ["/app/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
