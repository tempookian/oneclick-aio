import configparser
import json
import subprocess

from clog import CLogger
from utils import change_ownership, generate_random_email

log = CLogger("install_cert", file_log_level=1, console_log_level=1)


def read_domains(filename: str) -> list:
    """Reads the domain from file to issue cert. The domains with issue_cert=False will not be included

    Args:
        filename (str): the filename in which the domains are stored ini `ini` format

    Returns:
        list: list of domains for which the cert needs to be issued
    """
    conf = configparser.ConfigParser()
    conf.read(filename)
    domains = [conf[s]["address"]
               for s in conf.sections() if conf.get(s, "issue_cert", fallback=False)]

    return domains


def get_account_email():
    """
    Retrieves the email address associated with an account stored in acme files.

    Returns:
    -------
    str or None: The email address if the file exists and can be parsed, otherwise None.
    """
    try:
        with open("/root/.acme.sh/ca/acme.zerossl.com/v2/DV90/account.json", "r") as infile:
            # Load the contents of the file into a dictionary
            content = json.load(infile)

            # Extract the email address from the 'contact' key
            account_email = content["contact"][0].split("mailto:")[1]
    except FileNotFoundError:
        # If the file does not exist, return None
        log.debug("No account could be found. File does not exist")
        account_email = None
    except Exception as e:
        # If any other error occurs, log the error message and traceback
        log.exception("Unknown error occured!")
        log.exception(e)

    return account_email


def install_acme():
    """
    Installs the ACME client and sets it up for use.

    Installs curl, socat, and cron using apt, sets cap to give access to ports for non-root users,
    installs acme client, sets default ca to letsencrypt, creates a /keys/ folder, sets ownership
    of /keys/ to nobody, and sets access level to 444 for /keys/.

    Returns:
        None
    """
    log.debug("Installing curl, socat, and cron...")
    process = subprocess.Popen(["sudo", "apt", "install", "curl", "socat",
                               "cron", "-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()

    log.debug("set cap to give access to ports for non-root users...")
    process = subprocess.Popen(["sudo", "setcap", "'cap_net_bind_service=+ep'",
                               "/usr/bin/socat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()

    
    log.debug("Installing acme")
    process = subprocess.Popen(
        ["curl", "https://get.acme.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = subprocess.Popen(
        ["bash"], stdin=process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()

    log.debug("Setting default ca to letsencrypt")
    process = subprocess.Popen(["/root/.acme.sh/acme.sh", "--set-default-ca" "--server letsencrypt"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()

    log.debug("Creating /keys/ folder")
    process = subprocess.Popen(
        ["mkdir", "-p", "/keys/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()

    log.debug("Setting ownership of /keys/ to nobody")
    process = subprocess.Popen(
        ["chown", "nobody", "/keys/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()

    log.debug("Setting access level to 444 for /keys/")
    process = subprocess.Popen(
        ["chmod", "444", "/keys/*"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()


def register_account(account_email):
    """Registers an account with the `acme.sh` command line tool.

    Args:
    account_email (str): The email address associated with the account to be registered.

    Returns:
    None
    """
    log.debug("Registering account")

    # Use the subprocess library to run the acme.sh tool with the given options
    process = subprocess.Popen(
        ["/root/.acme.sh/acme.sh", "--register-account", "-m", account_email])
    stdout, stderr = process.communicate()

    # Log the standard error if it is not empty
    if stderr:
        log.error(stderr.decode("utf8"))


def issue_cert(domain):
    log.debug("Issuing cert for domain", domain)
    process = subprocess.Popen(["/root/.acme.sh/acme.sh", "--issue", "-d",
                               domain, "--standalone"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # log.debug(stdout.decode("utf8"))
    if stderr:
        log.error(stderr.decode("utf8"), domain)
        log.error("Please make sure the domain is properly configured in your nameserver!", domain)
        exit(0)


def install_cert(domain: str):
    """Installs a certificate for a given domain using the `acme.sh` command line tool.

    Args:
    domain (str): The domain name to be used to generate the certificate.

    Returns:
    None
    """
    # Use the subprocess library to run the acme.sh tool with the given options
    process = subprocess.Popen([
        "/root/.acme.sh/acme.sh",
        "--installcert",
        "-d", domain,
        "--key-file", f"/keys/{domain}-key.pem",
        "--fullchain-file", f"/keys/{domain}.pem"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Print the standard error if it is not empty
    if stderr:
        print(stderr.decode("utf8"))
        exit(0)



def install_certs(dom_file: str = "domains.ini"):
    """Installs certificates for all domains listed in a file.

    Args:
    dom_file (str, optional): The file name containing a list of domains, one per line.
        Defaults to "domains.ini".

    Returns:
    None
    """
    log.debug("Getting account email...")
    account_email = get_account_email()

    if account_email is None:
        log.debug("Generating new random account email...")
        account_email = generate_random_email()
        log.debug("Account email generated", account_email)
        register_account(account_email)
    else:
        log.debug("Account email found", account_email)

    log.info("Reading domains...")
    domains = read_domains(dom_file)

    for domain in domains:
        issue_cert(domain)
        install_cert(domain)

    log.debug("Setting ownership of /keys/ to noboyd")
    change_ownership(
        path="/keys/",
        user="nobody"
    )

