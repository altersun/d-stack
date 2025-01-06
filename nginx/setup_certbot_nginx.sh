# Install python requirements
apt-get update
apt-get install -y python3 python3-venv libaugeas0

# Make a venv for certbot
python3 -m venv /opt/certbot/
/opt/certbot/bin/pip install --upgrade pip

# Install certbot
/opt/certbot/bin/pip install certbot certbot-nginx
ln -s /opt/certbot/bin/certbot /usr/bin/certbot

# Make the cert
certbot --nginx \
    --agree-tos \
    --non-interactive \
    -m david.james.alderson@gmail.com \
    -d www.donnybrook.boston
    # -d donnybrook.boston \

# Auto renew the cert
echo "0 0,12 * * * root /opt/certbot/bin/python -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew -q" | tee -a /etc/crontab > /dev/null
