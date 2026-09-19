import paramiko
import os

GAME_DIR = os.path.dirname(os.path.abspath(__file__))
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('116.63.203.1', port=22, username='root', password='zdmy3n14F', timeout=30)
print("SSH connected!")

sftp = ssh.open_sftp()
sftp.put(os.path.join(GAME_DIR, "index.html"), "/var/www/emoji-battle/index.html")
sftp.close()
print("index.html uploaded!")

stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8090/")
print(f"HTTP: {stdout.read().decode().strip()}")

stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8090/api/scores")
print(f"API: {stdout.read().decode().strip()[:200]}")

ssh.close()
print("Done!")
