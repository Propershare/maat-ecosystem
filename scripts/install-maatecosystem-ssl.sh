#!/usr/bin/env bash
# Free TLS for maatecosystem.com via Let's Encrypt (Certbot).
# Requires: DNS A records → this host (47.200.181.85), nginx, sudo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NGINX_SRC="$ROOT/scripts/nginx/maatecosystem.com.conf"
NGINX_DST="/etc/nginx/sites-available/maatecosystem.com.conf"
CERT_EMAIL="${CERTBOT_EMAIL:-psnpropershare@gmail.com}"
DOMAINS=(maatecosystem.com www.maatecosystem.com)

echo "=== maatecosystem.com — Let's Encrypt (free) ==="

echo ""
echo "=== 1. DNS check ==="
for d in "${DOMAINS[@]}"; do
  ip="$(dig @8.8.8.8 +short "$d" A | head -1 || true)"
  if [[ -z "$ip" ]]; then
    echo "FAIL: no A record for $d — add at registrar first."
    exit 1
  fi
  echo "OK: $d → $ip"
done

echo ""
echo "=== 2. HTTP-only nginx (ACME webroot) for cert issuance ==="
sudo tee "$NGINX_DST" >/dev/null <<'HTTPONLY'
server {
    listen 80;
    server_name maatecosystem.com www.maatecosystem.com;

    location ^~ /.well-known/acme-challenge/ {
        default_type "text/plain";
        root /var/www/html;
        try_files $uri =404;
    }

    location / {
        proxy_pass http://127.0.0.1:3008;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    access_log /var/log/nginx/maatecosystem.com.access.log;
    error_log /var/log/nginx/maatecosystem.com.error.log;
}
HTTPONLY

sudo ln -sf "$NGINX_DST" /etc/nginx/sites-enabled/maatecosystem.com.conf
sudo nginx -t
sudo systemctl reload nginx
echo "Nginx HTTP config active."

echo ""
echo "=== 3. Certbot (webroot — free Let's Encrypt cert) ==="
if [[ -d /etc/letsencrypt/live/maatecosystem.com ]]; then
  echo "Existing cert found — renewing if needed."
  sudo certbot renew --cert-name maatecosystem.com --quiet || true
else
  sudo certbot certonly --webroot \
    -w /var/www/html \
    -d maatecosystem.com \
    -d www.maatecosystem.com \
    --non-interactive \
    --agree-tos \
    -m "$CERT_EMAIL"
fi

echo ""
echo "=== 4. Deploy HTTPS nginx config ==="
sudo cp "$NGINX_SRC" "$NGINX_DST"
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo "=== 5. Verify ==="
curl -sI "https://maatecosystem.com" | head -5
echo ""
echo "Done. HTTPS: https://maatecosystem.com"
echo "Auto-renew: certbot.timer (systemctl status certbot.timer)"
