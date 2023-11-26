FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy the current directory contents into the container
COPY . /app/

# Install dependencies, Nginx, Supervisor and other necessary tools
RUN apt-get update && \
    apt-get install -y nginx supervisor && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Run collectstatic command during build
RUN python manage.py collectstatic --noinput

# Create necessary directories
RUN mkdir -p /var/log/gunicorn/ /etc/nginx/ssl/

# Copy configuration files into their places
COPY dockerfiles/gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf
COPY dockerfiles/django.conf /etc/nginx/sites-available/django.conf

# Copy SSL stuff
COPY dockerfiles/ca_bundle.crt /etc/nginx/ssl/ca_bundle.crt
COPY dockerfiles/certificate.crt /etc/nginx/ssl/certificate.crt
COPY dockerfiles/private.key /etc/nginx/ssl/private.key


# Remove default nginx configuration and Create symbolic link for your Nginx configuration
RUN rm -f /etc/nginx/sites-enabled/default && \
    ln -s /etc/nginx/sites-available/django.conf /etc/nginx/sites-enabled

# Set the command to run Supervisor when the container starts
CMD ["supervisord", "-n"]
