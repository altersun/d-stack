#!/bin/bash

# The domain is passed as the first argument to the deploy-hook script
DOMAIN=$1
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"

# Check if the certificate directory already exists
if [ -d "$CERT_DIR" ]; then
  echo "Certificate for $DOMAIN already exists. Exiting gracefully."
  exit 0
fi

certbot certonly --standalone --agree-tos --no-eff-email \
    -m david.james.alderson@gmail.com -d www.donnybrook.boston \
    --keep-until-expiring --reuse-key \
    --cert-path /etc/letsencrypt/live \
    --key-path /etc/letsencrypt/live

ln -sf /etc/letsencrypt/live/www.donnybrook.boston/fullchain.pem \
    /etc/letsencrypt/live/fullchain.pem &&
ln -sf /etc/letsencrypt/live/www.donnybrook.boston/privkey.pem \
    /etc/letsencrypt/live/privkey.pem


