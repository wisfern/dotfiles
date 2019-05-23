#!/usr/bin/bash

echo ""
date
cd /home/devis/.local/share/shadowsocksr

sudo python3 ssra.py
sudo python3 update_v2ray_config.py
echo "v2ray config update done!"

/usr/bin/v2ray/v2ray -config v2ray_config.json -test

if [ $? -eq 0 ]; then
    echo "v2ray config valid done!"
    sudo systemctl restart v2ray
    echo "v2ray service restart done!"
fi
