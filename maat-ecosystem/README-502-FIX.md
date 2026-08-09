# 502 Bad Gateway Fix for n8n

## Problem
A docker-proxy process (running as root) is holding port 5678, preventing n8n from starting.

## Solution (Run with sudo)

```bash
sudo /home/suspect/.n8n/KILL-DOCKER-PROXY-5678.sh
```

Then restart n8n:
```bash
sudo systemctl restart n8n.service
sudo systemctl status n8n.service
```

## If that doesn't work

The docker-proxy keeps respawning. You need to find what's creating it:

1. Check for Docker containers with port 5678:
```bash
docker ps -a --format "{{.ID}} {{.Names}}" | xargs -I {} docker inspect {} --format '{{.Name}}: {{range .NetworkSettings.Ports}}{{.}}{{end}}' | grep 5678
```

2. Check docker-compose files:
```bash
grep -r "5678" ~/.n8n/*/docker-compose.yml
```

3. Stop Docker temporarily to free the port:
```bash
sudo systemctl stop docker
sudo systemctl start n8n.service
sudo systemctl start docker
```

The docker-proxy is created by Docker when a container has port mappings, even if the container is stopped. You need to remove the container or change its port mapping.
