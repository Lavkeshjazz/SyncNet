import os
import json
import socket
import time
import argparse
from zeroconf import Zeroconf, ServiceInfo
from discovery_ui import ReceiverServiceBrowser, select_receiver

def get_config_path(cli_config_path=None):
    if cli_config_path:
        return cli_config_path
    return os.path.join(os.path.expanduser("~"), ".receiver_service_config.json")

def prompt_user_for_config(config_path):
    print("Welcome! Let's configure your service.\n")

    name = input("Enter service name (e.g., Warehouse Manager): ").strip()
    version = input("Enter service version (e.g., 0.1): ").strip()
    info = input("Enter service info (e.g., Main warehouse scanner): ").strip()
    port = int(input("Enter service port (e.g., 8080): ").strip())
    server = input("Enter hostname (e.g., warehouse.local): ").strip()

    config = {
        "version": version,
        "info": info,
        "port": port,
        "server": server if server.endswith('.') else server + ".",
        "service_type": "_example._udp.local.",
        "name": f"{name}._example._udp.local."
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("\nConfiguration saved to", config_path)
    return config

def load_config(config_path):
    if not os.path.exists(config_path):
        return None
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: Config file is corrupted. Reconfiguring...")
        return None

def main(zeroconf,config):
    cur_ip = socket.gethostbyname(socket.gethostname())
    desc = {
        'version': config["version"],
        'info': config["info"]
    }

    info = ServiceInfo(
        type_=config["service_type"],
        name=config["name"],
        addresses=[socket.inet_aton(cur_ip)],
        port=config["port"],
        properties=desc,
        server=config["server"]
    )

    print("\nRegistering service...")
    zeroconf.register_service(info)

