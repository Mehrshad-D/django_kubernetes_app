# Dockerfile

# Stage 1: Build stage
# Use a Python base image for building the application
FROM --platform=linux/amd64 python:3.9-slim-bookworm AS builder

# Set working directory in the container
WORKDIR /app

# Install system dependencies needed for Python packages.
# libpq-dev is required for psycopg2-binary. gcc is needed for compiling some packages.

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies

RUN python -m pip install --upgrade pip && \
    pip config set global.index-url https://pypi.org/simple/ && \
    pip config set global.trusted-host pypi.org

COPY ./app/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt


# Copy the entire Django project into the container
# This ensures manage.py, settings.py, and all app files are present for subsequent commands.
COPY ./app .

# Set the Python path explicitly AFTER copying the project.
# Adding '.' ensures Python searches the current directory for modules.
# We also set DJANGO_SETTINGS_MODULE here to ensure it's available for manage.py commands.
ENV PYTHONPATH=/app:. \
    DJANGO_SETTINGS_MODULE=kubeweb.settings

# Collect static files (important for Django in production)
# Explicitly pass the settings file to manage.py for robustness.
RUN python manage.py collectstatic --noinput --settings=kubeweb.settings

# Stage 2: Production stage
# Use a lighter base image for the final production image
FROM --platform=linux/amd64 python:3.9-slim-bookworm

# Set working directory in the container
WORKDIR /app

# Install runtime dependencies for psycopg2 (libpq5)
# This is crucial for psycopg2-binary to work without dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the installed Python packages and collected static files from the builder stage
# Ensure that the site-packages from the builder are copied correctly
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app/staticfiles_build /app/staticfiles_build 
# Copy the entire application code from the builder stage
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --from=builder /app /app

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Set environment variables for Django (e.g., to indicate production)
# This is repeated but necessary for the final image to function independently.
# We also keep the DJANGO_SETTINGS_MODULE env var for Gunicorn's default behavior.
ENV DJANGO_SETTINGS_MODULE=kubeweb.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:. \
    PATH="/usr/local/bin:$PATH" 


# Run Gunicorn to serve the Django application
# The '--bind 0.0.0.0:8000' makes Gunicorn listen on all available network interfaces on port 8000.
# The '-w 4' sets 4 worker processes, adjust based on your server's CPU cores and load.
# The 'kubeweb.wsgi:application' refers to your project's WSGI application.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "kubeweb.wsgi:application"]
