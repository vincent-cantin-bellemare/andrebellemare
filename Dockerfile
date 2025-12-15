FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput --settings=config.settings || true

# Expose port
EXPOSE 8000

# Create shortcuts for Django management commands
RUN echo '#!/bin/bash\ncd /app && python3 manage.py runserver "$@"' > /usr/local/bin/runserver && \
    chmod +x /usr/local/bin/runserver

RUN echo '#!/bin/bash\ncd /app && python3 manage.py makemigrations "$@"' > /usr/local/bin/makemigrations && \
    chmod +x /usr/local/bin/makemigrations

RUN echo '#!/bin/bash\ncd /app && python3 manage.py migrate "$@"' > /usr/local/bin/migrate && \
    chmod +x /usr/local/bin/migrate

RUN echo '#!/bin/bash\ncd /app && python3 manage.py shell "$@"' > /usr/local/bin/shell && \
    chmod +x /usr/local/bin/shell

# Run gunicorn (default for production)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "config.wsgi:application"]




