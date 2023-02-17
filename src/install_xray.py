import configparser
import subprocess
import urllib.request
import uuid
from utils import generate_random_password

import json5

from clog import CLogger

log = CLogger("install_xray", console_log_level=1, file_log_level=1)



def download_base_config():
    """
    This function downloads the base Xray configuration file and saves it to the specified location.
    """
    url = "https://raw.githubusercontent.com/XTLS/Xray-examples/main/All-in-One-fallbacks-Nginx/server.json"
    try:
        response = urllib.request.urlopen(url)
        log.debug("config read from url")
    except urllib.error.URLError as e:
        log.error(f"Error: {e.reason}", url)
        log.exception(str(e), url)

    try:
        config_json = json5.loads(response.read())
    except Exception as e:
        log.error("Config could not be read")
        log.exception(e=e)
        exit(1)

    return config_json


def modify_base_config(base_config: dict):
    domain_config = configparser.ConfigParser()
    domain_config.read("domains.ini")
    config_id = str(uuid.uuid4())
    config_pw = generate_random_password()
    with open(".confidential", "w") as outfile:
        outfile.write(config_id + "\n")
        outfile.write(config_pw + "\n")

    # entry_point
    vless_inbound = next(
        i for i in base_config["inbounds"] if i["tag"].lower() == "Vless-TCP-XTLS".lower())
    for client in vless_inbound["settings"]["clients"]:
        client["id"] = config_id
        
    for inbound in base_config["inbounds"]:
        if "settings" in inbound:
            if "clients" in inbound["settings"]:
                for client in inbound["settings"]["clients"]:
                    if "id" in client:
                        client["id"] = config_id

    tls_domains = [domain_config[s]["address"] for s in domain_config.sections(
    ) if domain_config.get(s, "issue_cert", fallback=False)]
    vless_inbound["streamSettings"]["tlsSettings"]["certificates"] = [
        dict(
            ocspStapling=3600,
            certificateFile=f"/keys/{domain}.pem",
            keyFile=f"/keys/{domain}-key.pem"
        )
        for domain in tls_domains
    ]

    # Fallbacks - trojan vless vmess
    fallbacks = vless_inbound["settings"]["fallbacks"]
    for protocol in ["trojan", "vless", "vmess"]:
        fallback = next(f for f in fallbacks if f"{protocol}-h2" in f["dest"])
        fallback["name"] = domain_config[f"{protocol}-h2"]["address"]

    # Fallbacks - shadowsocks
    fallback = next(f for f in fallbacks if f["dest"] == 4003)
    fallback["name"] = domain_config["shadowsocks-h2"]["address"]

    # Change password
    for inbound in base_config["inbounds"]:
        if inbound.get("settings"):
            if inbound.get("settings").get("clients"):
                clients = inbound.get("settings").get("clients")
                password_clients = [c for c in clients if c.get("password")]
                for client in password_clients:
                    client["password"] = config_pw
            if inbound.get("settings").get("password"):
                inbound["settings"]["password"] = config_pw

    with open("/usr/local/etc/xray/config.json", "w") as fout:
        json5.dump(
            base_config,
            fout,
            indent=2,
            quote_keys=True,
            trailing_commas=False
        )


def load_config_from_file(filepath="base_server.json"):
    with open(filepath) as infile:
        config_json = json5.load(infile)
    return config_json


def install_xray():
    """
    This function installs the Xray using socat and the official Xray install script.
    """
    try:
        subprocess.check_call(["sudo", "apt", "install", "socat", "-y"])
        subprocess.check_call(["curl", "-o", "install-release.sh", "-L",
                              "https://github.com/XTLS/Xray-install/raw/main/install-release.sh"])
        subprocess.check_call(
            ["sudo", "bash", "install-release.sh", "install"])
        print("Xray has been installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)



def restart_service(service_name):
    result = subprocess.run(['systemctl', 'restart', service_name],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        log.info(f"Service '{service_name}' restarted successfully")
    else:
        log.error(
            f"Failed to restart service '{service_name}'. Error: {result.stderr.decode()}")


if __name__ == "__main__":
    install_xray()
