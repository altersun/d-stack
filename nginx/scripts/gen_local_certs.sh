#!/bin/sh

CERT_DIR="/etc/nginx/ssl"

echo "Checking for existing certificates..."
if [ -f "${CERT_DIR}/server.crt" ] && [ -f "${CERT_DIR}/server.key" ]; then
    echo "Certificates already exist. Skipping generation."
    exit 0
fi

echo "Generating self-signed certificates..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${CERT_DIR}/server.key" -out "${CERT_DIR}/server.crt" \
    -subj "/CN=localhost"

echo "Certificates generated successfully."

