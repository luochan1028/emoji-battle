import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('116.63.203.1', port=22, username='root', password='zdmy3n14F', timeout=30)

nginx_conf = r'''server {
    listen 8090;
    server_name _;
    root /var/www/emoji-battle;
    index index.html;
    location / {
        try_files $uri $uri/ =404;
    }
}'''

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/conf.d/emoji-battle.conf', 'w') as f:
    f.write(nginx_conf)
sftp.close()
print('nginx config updated to port 8090')

for cmd in ['nginx -t', 'systemctl reload nginx']:
    print(f'> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode().strip())
    err = stderr.read().decode().strip()
    if err:
        print(f'  err: {err[:200]}')

time.sleep(1)
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8090/")
print(f'HTTP status: {stdout.read().decode().strip()}')

ssh.close()
print('Done! URL: http://116.63.203.1:8090/')
