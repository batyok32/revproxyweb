import subprocess


# filename = "mit"
# foreign = "pm-a6cd1a28.com"
# port = "81"
# our = "pmm.bailon.ga"

filename = "mit-datadome"
foreign = "js.datadome.co"
port = "82"
our = "datadome.i9.ar"

# filename = "mit-datadome-api"
# foreign = "api-js.datadome.co"
# port = "83"
# our = "apidatadome.i9.ar"

# filename = "mit-programmatic"
# foreign = "parimatch-dk1.pragmaticplay.net"
# port = "84"
# our = "pragrammatic.bailon.ga"

# filename = "Oaks"
# foreign = "alfred.c2.3oaks.com"
# port = "85"
# our = "oaks.bailon.ga"

# filename = "mit-betmap"
# foreign = "betman.c2.3oaks.com"
# port = "86"
# our = "betman.bailon.ga"

# filename = "mit-oackstatic"
# foreign = "static.3oaks.com"
# port = "87"
# our = "staticoaks.bailon.ga"

# SYSTEMD
f = open(f"/etc/systemd/system/{filename}.service", "w")
text = f"""
[Unit]
Description={filename.upper()}
After=network.target

[Service]
Type=simple
User=root
ExecStart=/root/.local/bin/mitmdump -p {port} --mode reverse:https://{foreign} --set block_global=false -s /root/filter.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
f.write(text)
f.close()

print("\nSYSTEMD WROTE")
# FILTER PY
f = open(f"/root/filter.py", "a+")
text = f"""
        flow.response.content = flow.response.content.replace(
            b"{foreign}", b"{our}"
        )
"""

f.write(text)
f.close

print("\nFILTER.pY WROTE")
# NGINX
f = open(f"/etc/nginx/sites-available/default", "a+")

text = f"""
server {{
    listen 80;
    server_name {our};

    location / {{
        proxy_set_header X-Proxy-Client-IP $remote_addr;
        proxy_set_header X-Proxy-Original-Host {foreign}; 
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:{port}/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}
"""

f.write(text)
f.close

print("\nNGINX WROTE")


# CERTBOT
subprocess.run([f"certbot --nginx --redirect -d {our}"], shell=True)

print("\nCERTBOT WROTE")

# RESTART EVERYTHING
subprocess.run(["systemctl daemon-reload"], shell=True)
subprocess.run(["systemctl restart nginx"], shell=True)
subprocess.run(["systemctl restart mit"], shell=True)
subprocess.run([f"systemctl restart {filename}"], shell=True)

print("\nRESTARTED DONE")

print("\nWRITE THIS TO /etc/nginx/sites-available/default removing old one")
print(
    f"""
server {{
    listen 443 ssl;
    server_name {our};

    ssl on;
    ssl_certificate /etc/letsencrypt/live/{our}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{our}/privkey.pem;
    ssl_session_timeout 5m;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols SSLv3 SSLv2 TLSv1 TLSv1.1 TLSv1.2; 
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_prefer_server_ciphers on;

    location / {{
        proxy_set_header X-Proxy-Client-IP $remote_addr;
        proxy_set_header X-Proxy-Original-Host {foreign}; 
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:{port}/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}

server {{
    listen 80; 
    server_name {our};
    return 301 https://{our}$request_uri; 
}}
"""
)
