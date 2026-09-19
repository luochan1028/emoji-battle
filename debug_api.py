import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('116.63.203.1', port=22, username='root', password='zdmy3n14F', timeout=30)
print("SSH connected!")

# Check backend service status
commands = [
    "systemctl is-active emoji-battle",
    "systemctl status emoji-battle 2>&1 | tail -20",
    "curl -s http://localhost:8090/api/scores",
    "curl -s -X POST http://localhost:8090/api/scores -H 'Content-Type: application/json' -d '{\"name\":\"test\",\"score\":10}'",
    "curl -s http://localhost:8090/api/scores",
    "cat /var/www/emoji-battle/scores.json 2>/dev/null || echo 'no scores file'",
    "cat /var/www/emoji-battle/server.py | head -20",
    "tail -20 /var/log/syslog 2>/dev/null | grep emoji || journalctl -u emoji-battle --no-pager -n 20",
]

for cmd in commands:
    print(f"\n> {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out[:500])
    if err: print(f"ERR: {err[:300]}")

ssh.close()
print("\nDone!")
