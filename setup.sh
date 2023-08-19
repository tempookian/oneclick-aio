#!/bin/bash

validate_issue_cert() {
  while true; do
    read -p "Issue cert? (Y/n): " issue_cert
    case $issue_cert in
      [Yy]* ) issue_cert="true"; break;;
      [Nn]* ) issue_cert="false"; break;;
      * ) echo "Please answer Y or N.";;
    esac
  done

  echo $issue_cert
}

sudo apt update;
sudo apt upgrade -y;
sudo apt install -y python3-venv;
git clone https://github.com/tempookian/oneclick-aio;
cd oneclick-aio;
python3 -m venv venv;
source ./venv/bin/activate;
pip install -r requirements.txt;

echo "[entry-domain]" > domains.ini
read -p "Enter address for entry-domain: " entry_domain
echo "address = $entry_domain" >> domains.ini
issue_cert=$(validate_issue_cert)
echo "issue_cert = $issue_cert" >> domains.ini

echo "[trojan-h2]" >> domains.ini
read -p "Enter address for trojan-h2: " trojan_h2
echo "address = $trojan_h2" >> domains.ini
issue_cert=$(validate_issue_cert)
echo "issue_cert = $issue_cert" >> domains.ini

echo "[vmess-h2]" >> domains.ini
read -p "Enter address for vmess-h2: " vmess_h2
echo "address = $vmess_h2" >> domains.ini
issue_cert=$(validate_issue_cert)
echo "issue_cert = $issue_cert" >> domains.ini

echo "[vless-h2]" >> domains.ini 
read -p "Enter address for vless-h2: " vless_h2
echo "address = $vless_h2" >> domains.ini
issue_cert=$(validate_issue_cert)
echo "issue_cert = $issue_cert" >> domains.ini

echo "[shadowsocks-h2]" >> domains.ini
read -p "Enter address for shadowsocks-h2: " shadowsocks_h2  
echo "address = $shadowsocks_h2" >> domains.ini
issue_cert=$(validate_issue_cert)
echo "issue_cert = $issue_cert" >> domains.ini


python3 ./src/main.py;