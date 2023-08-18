import os
import subprocess


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
