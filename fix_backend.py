import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('116.63.203.1', port=22, username='root', password='zdmy3n14F', timeout=30)
print("SSH connected!")

# Install Flask with --break-system-packages
commands = [
    "pip3 install --break-system-packages flask flask-cors 2>&1 | tail -5",
    "systemctl restart emoji-battle",
]
for cmd in commands:
    print(f"> {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"  {out[:300]}")
    if err: print(f"  {err[:300]}")

time.sleep(3)

# Check status
stdin, stdout, stderr = ssh.exec_command("systemctl is-active emoji-battle")
status = stdout.read().decode().strip()
print(f"Backend service: {status}")

if status != "active":
    stdin, stdout, stderr = ssh.exec_command("systemctl status emoji-battle 2>&1 | tail -15")
    print(stdout.read().decode().strip())

# Test API
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8090/api/scores")
print(f"API test: {stdout.read().decode().strip()[:200]}")

# Test frontend
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8090/")
print(f"Frontend HTTP: {stdout.read().decode().strip()}")

ssh.close()
print("Done!")
