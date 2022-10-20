import subprocess

print(
    """
WELCOME TO SCRIPT!
JEMI 7 ADIM.
BIR DINE 3 ADIMDE DOMAINY YAZMALY.
"""
)

# NEED TO DO
# CLEAN 80, 81, 443 port
# GET DOMAIN CERTIFICATE AUTOMATICALLY

inp = input("START >>>")

subprocess.run(
    ["apt-get update -y && apt-get upgrade -y"], stdout=subprocess.PIPE, shell=True
)
print("\n1. UPDATED")
subprocess.run(
    ["apt-get install python3-certbot-nginx python3-pip pipx python3.8-venv nginx -y"],
    stdout=subprocess.PIPE,
    shell=True,
)
subprocess.run(
    ["systemctl stop apache2"],
    stdout=subprocess.PIPE,
    shell=True,
)

print("\n2. INSTALLED EVERYTHING")
subprocess.run(
    ["apt-get install python3-certbot-nginx python3-pip pipx python3.8-venv nginx -y"],
    stdout=subprocess.PIPE,
    shell=True,
)
print("\n3. GETTING DOMAIN CERTIFICATE")
domain = input("\n\nDomain: ")
domain = domain.strip()
subprocess.run([f"certbot --nginx -d {domain}"], stdout=subprocess.PIPE, shell=True)
# Get domain certificate

# NGINX
print("\n4. INSTALLING NGINX")
f = open("/etc/nginx/sites-available/default", "w")
f.write(
    f"""
server {{
    listen 80;
    listen 443 ssl;
    server_name {domain};

    ssl on;
    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem; # Проверьте точные пути к сертификату, ключу  и их права
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem; # на чтение для пользователя под которым запущен nginx
    ssl_session_timeout 5m;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols SSLv3 SSLv2 TLSv1 TLSv1.1 TLSv1.2; # Настроить по этому протоколу
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_prefer_server_ciphers on;

    location / {{
        proxy_set_header X-Proxy-Token doih302id1hd9g7639d8h23198dj09dwd;
        proxy_set_header X-Proxy-Client-IP $remote_addr;
        proxy_set_header X-Proxy-Original-Host pm-a6cd1a28.com; 
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:81/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

    }}
 
}}
"""
)
f.close()
print("WROTE TO FILE")

subprocess.run(["systemctl daemon-reload"], stdout=subprocess.PIPE, shell=True)
subprocess.run(["systemctl restart nginx"], stdout=subprocess.PIPE, shell=True)
print("\n5. RESTARTED NGINX")

# MITM PROXY
subprocess.run(
    ["python3 -m pip install --user pipx"], stdout=subprocess.PIPE, shell=True
)
subprocess.run(["python3 -m pipx ensurepath"], stdout=subprocess.PIPE, shell=True)
subprocess.run(["pipx install mitmproxy"], stdout=subprocess.PIPE, shell=True)
print("\n6. INSTALLED MITMPROXY")


f = open("/etc/systemd/system/mit.service", "w")
f.write(
    f"""
[Unit]
Description=MITM PROXY
After=network.target

[Service]
Type=simple
User=root
ExecStart=/root/.local/bin/mitmdump -p 81 --mode reverse:https://pm-a6cd1a28.com --set block_global=false
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
)
f.close()
print("WROTE MITMPROXY")

subprocess.run(["systemctl daemon-reload"], stdout=subprocess.PIPE, shell=True)
subprocess.run(["systemctl enable mit"], stdout=subprocess.PIPE, shell=True)
subprocess.run(["systemctl restart mit"], stdout=subprocess.PIPE, shell=True)
subprocess.run(["systemctl restart nginx"], stdout=subprocess.PIPE, shell=True)
print("\n7. RESTARTED EVERYTHING")

print(f"\n\nBOLDY WEBSITE TAYYAR - https://{domain}")
