import paramiko
import os
import sys

HOST = "116.63.203.1"
PORT = 22
USER = "root"
PASS = "zdmy3n14F"
GAME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
REMOTE_DIR = "/var/www/emoji-battle"

def deploy():
    print(f"Connecting to {HOST}:{PORT} as {USER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=30)
    print("SSH connected!")

    commands = [
        f"mkdir -p {REMOTE_DIR}",
        f"apt-get update -qq && apt-get install -y -qq nginx > /dev/null 2>&1 || yum install -y -q nginx > /dev/null 2>&1 || echo 'nginx install skipped'",
        f"rm -f /etc/nginx/sites-enabled/default 2>/dev/null; rm -f /etc/nginx/conf.d/default.conf 2>/dev/null; true",
    ]

    for cmd in commands:
        print(f"  > {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_code = stdout.channel.recv_exit_status()
        err = stderr.read().decode()
        if err:
            print(f"    stderr: {err.strip()[:200]}")

    sftp = ssh.open_sftp()

    files_to_upload = ["index.html", "icon.jpg", "icon_200_final.jpg"]
    for f in files_to_upload:
        local_path = os.path.join(GAME_DIR, f)
        if os.path.exists(local_path):
            remote_path = f"{REMOTE_DIR}/{f}"
            print(f"  Uploading {f}...")
            sftp.put(local_path, remote_path)
        else:
            print(f"  Skipping {f} (not found)")

    sftp.close()

    nginx_conf = f"""server {{
    listen 80;
    server_name _;
    root {REMOTE_DIR};
    index index.html;
    location / {{
        try_files $uri $uri/ =404;
    }}
}}"""

    sftp = ssh.open_sftp()
    conf_path = "/etc/nginx/conf.d/emoji-battle.conf"
    with sftp.open(conf_path, 'w') as f:
        f.write(nginx_conf)
    print(f"  nginx config written to {conf_path}")
    sftp.close()

    commands = [
        "nginx -t",
        "systemctl restart nginx || service nginx restart",
        "systemctl enable nginx 2>/dev/null || true",
        f"ls -la {REMOTE_DIR}/",
    ]

    for cmd in commands:
        print(f"  > {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        exit_code = stdout.channel.recv_exit_status()
        if out:
            print(f"    {out.strip()[:300]}")
        if err:
            print(f"    {err.strip()[:300]}")

    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
    http_code = stdout.read().decode().strip()
    print(f"\nHTTP status check: {http_code}")

    ssh.close()
    print(f"\nDeployment complete!")
    print(f"Game URL: http://{HOST}/")

if __name__ == "__main__":
    deploy()
