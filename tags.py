filename = "mit-betman"
foreign = "betman.c2.3oaks.com"
port = "86"
our = "oaks.bailon.ga"

x = f"""
nano /etc/systemd/system/{filename}.service

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


nano /root/filter.py

from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    if flow.response and flow.response.content:
        flow.response.content = flow.response.content.replace(
            b"{foreign}", b"{our}"
        )
       
nano /etc/nginx/sites-available/default 

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


certbot --nginx -d {our}


nano /etc/nginx/sites-available/default 
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

systemctl daemon-reload
systemctl restart nginx 
systemctl restart mit   
systemctl restart {filename} 
"""
f = open(
    f"/home/batyr/projects/SSR/proxywebsite-script/instructions/{filename}.txt", "w"
)
f.write(x)
f.close()
