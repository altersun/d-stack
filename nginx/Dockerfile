# Use Nginx as the second stage
FROM nginx:stable-alpine AS nginx

# Copy Nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy static files for Nginx to serve
COPY app/static /var/www/

# Expose Nginx port
EXPOSE 80
