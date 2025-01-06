# Use Nginx as the second stage
FROM nginx:stable AS nginx

# Copy Nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx/setup_certbot_nginx.sh /usr/local/bin/setup_certbot
RUN chmod +x /usr/local/bin/setup_certbot
# Copy static files for Nginx to serve
COPY app/static /var/www/

# Expose Nginx port
EXPOSE 80

# Setup ssl cert
CMD ["sh", "/usr/local/bin/setup_certbot"]

