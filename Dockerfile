# Use a base Python image
FROM python:3.12-slim as python-base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set up a working directory
WORKDIR /python_tutorial

# Copy pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock* ./

# Install Poetry
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy the rest of the application code
COPY . .

# Expose the port for FastAPI
EXPOSE 8000

# Command to run FastAPI server using Gunicorn and Uvicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
