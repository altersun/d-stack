#!/bin/bash

# The domain is passed as the first argument to the deploy-hook script
DOMAIN=$1
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"

# Check if the certificate directory already exists
if [ -d "$CERT_DIR" ]; then
  echo "Certificate for $DOMAIN already exists. Exiting gracefully."
  exit 0
fi

# Otherwise, proceed with normal Certbot operation (optional custom logic)
