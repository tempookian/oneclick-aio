import configparser

import json5

from clog import CLogger

log = CLogger("client tools")

CLIENT_LINK_TEMPLATES = dict(
    TROJAN_TCP_TEMPLATE="trojan://{password}@{entryaddress}:443?security=tls&type=tcp#Trojan-TCP",
    TROJAN_WS_TEMPLATE="trojan://{password}@{entryaddress}:443?security=tls&type=ws&path=/trojanws?ed=2048#Trojan-WS",
    TROJAN_GRPC_TEMPLATE="trojan://{password}@{entryaddress}:443?security=tls&type=grpc&serviceName=trgrpc#Trojan-gRPC",
    TROJAN_H2_TEMPLATE="trojan://{password}@{entryaddress}:443?sni={sni}&security=tls&type=http&path=/trh2#Trojan-H2",
    VLESS_TCP_TEMPLATE="vless://{uuid}@{entryaddress}:443?security=tls&type=tcp#Vless-TCP",
    VLESS_WS_TEMPLATE="vless://{uuid}@{entryaddress}:443?security=tls&type=ws&path=/vlws?ed%3D204&host={entryaddress}#Vless-WS",
    VLESS_GRPC_TEMPLATE="vless://{uuid}@{entryaddress}:443?security=tls&type=grpc&serviceName=vlgrpc#Vless-gRPC",
    VLESS_H2_TEMPLATE="vless://{uuid}@{entryaddress}:443?sni={sni}&security=tls&type=http&path=/vlh2#Vless-H2",
)
# TODO = vmess


def generate_client_links(
    confidentials_file=".confidential", savepath="./clients.conf"
):
    try:
        # read username and passwords from .confidentials file
        with open(confidentials_file) as infile:
            uuid, password = (l.strip() for l in infile.readlines())
    except FileNotFoundError:
        log.error(f"Error: {confidentials_file} not found.", confidentials_file)
        return None
    except Exception as e:
        log.error(f"Error: {e}", confidentials_file)
        return None

    links = []

    for key, template in CLIENT_LINK_TEMPLATES.items():
        conf = configparser.ConfigParser()
        conf.read("./domains.ini")

        entryaddress = conf["entry-domain"]["address"]
        fields = dict(entryaddress=entryaddress, password=password, uuid=uuid)
        protocol, transport = key.split("_")[:2]

        if "h2" in transport.lower():
            sni = conf[f"{protocol.lower()}-{transport.lower()}"]["address"]
            fields["sni"] = sni
        links.append(template.format(**fields))
    links_str = "\n".join(links)
    with open(savepath, "w") as outfile:
        outfile.write(links_str)
    print(links_str)


if __name__ == "__main__":
    generate_client_links()
