import configparser
import os
import subprocess

import requests


def install_nginx():
    """
    Installs the nginx package and its dependencies.
    Also,removes the wrong repository and adds the correct one.
    Throws an error if the package is not found or if the user is not root.
    """
    if os.geteuid() != 0:
        raise PermissionError("This script must be run as root.")

    try:
        subprocess.run(["apt-get", "update"], check=True)
        # Installing nginx package
        subprocess.run(["apt-get", "install", "-y", "nginx"], check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to install nginx: {e.stderr.decode()}")


def get_default_conf():
    """
    Downloads the default nginx configuration file and places it as vpn.conf in /etc/nginx/conf.d/
    """
    domains_conf = configparser.ConfigParser()
    domains_conf.read("domains.ini")
    domains = [domains_conf[s]["address"] for s in domains_conf.sections()]
    domains_str = " ".join(domains)
    download_url = "https://raw.githubusercontent.com/XTLS/Xray-examples/main/All-in-One-fallbacks-Nginx/nginx.conf"
    r = requests.get(download_url)
    if r.status_code == 200:
        config = r.content.decode()
        config = config.replace("example.com", domains_str)
        print(config)


if __name__ == "__main__":
    get_default_conf()
