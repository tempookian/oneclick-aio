import subprocess

from client_tools import generate_client_links
from clog import CLogger
from install_certs import install_acme, install_certs
from install_nginx import install_nginx
from install_xray import (
    download_base_config,
    install_xray,
    modify_base_config,
    restart_service,
)

log = CLogger("main", file_log_level=1, console_log_level=1)


def main():
    with subprocess.Popen(
        ["install_nginx.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as process:
        stdout, stderr = process.communicate()
        if stderr:
            log.error(stderr.decode())


if __name__ == "__main__":
    install_acme()
    install_certs("domains.ini")
    install_nginx()
    install_xray()
    base_config = download_base_config()
    modify_base_config(base_config=base_config)
    restart_service("xray")
    generate_client_links()
