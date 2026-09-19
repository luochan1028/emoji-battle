import paramiko
import os
import time

HOST = "116.63.203.1"
PORT = 22
USER = "root"
PASS = "zdmy3n14F"
GAME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
REMOTE_DIR = "/var/www/emoji-battle"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=30)
print("SSH connected!")

# Install Flask
print("Installing Flask...")
stdin, stdout, stderr = ssh.exec_command("pip3 install flask flask-cors 2>&1 | tail -3")
print(stdout.read().decode().strip())

# Upload server.py
sftp = ssh.open_sftp()
print("Uploading server.py...")
sftp.put(os.path.join(GAME_DIR, "server.py"), f"{REMOTE_DIR}/server.py")

# Upload updated index.html
print("Uploading index.html...")
sftp.put(os.path.join(GAME_DIR, "index.html"), f"{REMOTE_DIR}/index.html")
sftp.close()

# Write systemd service for the backend
service_conf = """[Unit]
Description=Emoji Battle Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/emoji-battle
ExecStart=/usr/bin/python3 /var/www/emoji-battle/server.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target"""

sftp = ssh.open_sftp()
with sftp.open("/etc/systemd/system/emoji-battle.service", 'w') as f:
    f.write(service_conf)
sftp.close()
print("Systemd service created")

# Update nginx config: serve static files + proxy API to Flask
nginx_conf = """server {
    listen 8090;
    server_name _;
    root /var/www/emoji-battle;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri $uri/ =404;
    }
}"""

sftp = ssh.open_sftp()
with sftp.open("/etc/nginx/conf.d/emoji-battle.conf", 'w') as f:
    f.write(nginx_conf)
sftp.close()
print("Nginx config updated")

# Restart services
commands = [
    "systemctl daemon-reload",
    "systemctl restart emoji-battle",
    "systemctl enable emoji-battle",
    "nginx -t 2>&1",
    "systemctl reload nginx",
]
for cmd in commands:
    print(f"> {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"  {out[:200]}")
    if err: print(f"  {err[:200]}")

time.sleep(2)

# Test
stdin, stdout, stderr = ssh.exec_command("systemctl is-active emoji-battle")
print(f"Backend service: {stdout.read().decode().strip()}")

stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8090/")
print(f"Frontend HTTP: {stdout.read().decode().strip()}")

stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8090/api/scores")
print(f"API test: {stdout.read().decode().strip()[:100]}")

ssh.close()
print("\nDeployment complete!")
print(f"Game URL: http://{HOST}:8090/")
print(f"API: http://{HOST}:8090/api/scores")
