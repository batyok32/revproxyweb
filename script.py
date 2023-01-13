import subprocess


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


print(
    f"""
{bcolors.BOLD}{bcolors.HEADER}
{bcolors.UNDERLINE}Parimatch acmak scripty.\n{bcolors.ENDC}
1. Hiczat etmek gerek dal dine domeinlary beraymeli.
{bcolors.ENDC}
"""
)
inp = input("START >>>")
domain = input("\nDomain (parimatch.i9.ar): ")
domain = domain.strip()
datadomedomain = input("\nDatadome domain (datadome.i9.ar): ")
datadomedomain = datadomedomain.strip()
datadomedomainapi = input("\nDatadome api domain (apidatadome.i9.ar): ")
datadomedomainapi = datadomedomainapi.strip()

if not domain:
    domain = "parimatch.i9.ar"
if not datadomedomain:
    domain = "datadome.i9.ar"
if not datadomedomainapi:
    domain = "apidatadome.i9.ar"

print(
    f"""
-----------------------------------------------------------------------------
{bcolors.WARNING} Process baslady sabyrly bolyn...{bcolors.ENDC}
-----------------------------------------------------------------------------
"""
)
subprocess.run(["apt-get update -y && apt-get upgrade -y"], shell=True)

subprocess.run(
    ["systemctl stop apache2"],
    shell=True,
)
subprocess.run(
    ["apt-get remove nginx -y"],
    shell=True,
)
subprocess.run(
    ["apt-get install python3-certbot-nginx python3-pip pipx python3.8-venv nginx -y"],
    shell=True,
)
subprocess.run(
    ["rm -rf /etc/nginx/sites-available/default && touch  /etc/nginx/sites-available/default"],
    shell=True,
)


# CERTBOT
subprocess.run([f"certbot -n --nginx --redirect -d {domain} -m digitalocean@gmail.com --agree-tos"], shell=True)


# NGINX
f = open("/etc/nginx/sites-available/default", "w")
f.write(
    f"""
server {{
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

server {{ 
    listen 80; 
    server_name {domain};
    return 301 https://{domain}$request_uri; 
}}

server {{
    listen 80;
    server_name {datadomedomain};

    location / {{
        proxy_set_header X-Proxy-Client-IP $remote_addr;
        proxy_set_header X-Proxy-Original-Host js.datadome.co; 
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:82/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}

server {{
    listen 80;
    server_name {datadomedomainapi};

    location / {{
        proxy_set_header X-Proxy-Client-IP $remote_addr;
        proxy_set_header X-Proxy-Original-Host api-js.datadome.co; 
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:83/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}
"""
)
f.close()



subprocess.run([f"certbot -n --nginx --redirect -d {datadomedomain} -m digitalocean@gmail.com --agree-tos"], shell=True)
subprocess.run([f"certbot -n --nginx --redirect -d {datadomedomainapi} -m digitalocean@gmail.com --agree-tos"], shell=True)


# Get domain certificate
subprocess.run(["systemctl daemon-reload"], shell=True)
subprocess.run(["systemctl restart nginx"], shell=True)

# MITM PROXY
subprocess.run(["python3 -m pip install --user pipx"], shell=True)
subprocess.run(["python3 -m pipx ensurepath"], shell=True)
subprocess.run(["pipx install mitmproxy"], shell=True)


f = open("/etc/systemd/system/mit.service", "w")
f.write(
    f"""
[Unit]
Description=MITM PROXY
After=network.target

[Service]
Type=simple
User=root
ExecStart=/root/.local/bin/mitmdump -p 81 --mode reverse:https://pm-a6cd1a28.com --set block_global=false -s /root/filter.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
)
f.close()

f = open("/etc/systemd/system/mit-datadome.service", "w")
f.write(
    f"""
[Unit]
Description=MITM PROXY
After=network.target

[Service]
Type=simple
User=root
ExecStart=/root/.local/bin/mitmdump -p 82 --mode reverse:https://js.datadome.co --set block_global=false -s /root/filter.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
)
f.close()

f = open("/etc/systemd/system/mit-datadome-api.service", "w")
f.write(
    f"""
[Unit]
Description=MITM PROXY
After=network.target

[Service]
Type=simple
User=root
ExecStart=/root/.local/bin/mitmdump -p 83 --mode reverse:https://api-js.datadome.co --set block_global=false -s /root/filter.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
)
f.close()

# Filter py
f = open("/root/filter.py", "w")
f.write(
    f"""
from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    if flow.response and flow.response.content:
        flow.response.content = flow.response.content.replace(
            b"js.datadome.co", b"{datadomedomain}"
        )
        flow.response.content = flow.response.content.replace(
            b"api-js.datadome.co", b"{datadomedomainapi}"
        )
       
"""
)
f.close()

subprocess.run(["systemctl daemon-reload"], shell=True)
subprocess.run(["systemctl enable mit"], shell=True)
subprocess.run(["systemctl restart mit"], shell=True)
subprocess.run(["systemctl enable mit-datadome"], shell=True)
subprocess.run(["systemctl restart mit-datadome"], shell=True)
subprocess.run(["systemctl enable mit-datadome-api"], shell=True)
subprocess.run(["systemctl restart mit-datadome-api"], shell=True)
subprocess.run(["systemctl restart nginx"], shell=True)

print(f"\n\n{bcolors.OKGREEN}Process gutardy!{bcolors.ENDC}")
print(f"\n\nBOLDY WEBSITE TAYYAR - https://{domain}")
