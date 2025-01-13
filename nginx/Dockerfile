# Use Nginx as the second stage
FROM nginx:stable AS nginx

# Copy Nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy static files for Nginx to serve
COPY app/static /var/www/

# Copy SSL stuff
COPY nginx/ssl/selfsigned.crt /etc/nginx/ssl/selfsigned.crt
COPY nginx/ssl/selfsigned.key /etc/nginx/ssl/selfsigned.key
COPY nginx/ssl/dhparam.pem /etc/nginx/ssl/dhparam.pem

# Expose Nginx port
EXPOSE 80 443

