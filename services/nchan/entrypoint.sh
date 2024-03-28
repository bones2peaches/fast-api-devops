#!/bin/sh

# Assuming USERNAME and PASSWORD are environment variables
# Example: export USERNAME=test PASSWORD=api

# Generate .htpasswd file at the specified location
htpasswd -cb /etc/nginx/.htpasswd $NCHAN_USERNAME $NCHAN_PASSWORD


# Start Nginx
exec "$@"
