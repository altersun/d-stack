# No need to reinvent the wheel
FROM nginx:stable AS nginx

# Copy Nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy static files for Nginx to serve
COPY app/static /var/www/

# Expose http and https
EXPOSE 80 443

