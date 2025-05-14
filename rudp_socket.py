from rudp_simulations import (
    CleanRUDPSocket,
    LossRUDPSocket,
    CorruptRUDPSocket,
    LossCorruptRUDPSocket
)
import os

CONFIG_FILE = "rudp_config.py"

def write_python_config(config_dict):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"config = {repr(config_dict)}\n")

def choose_simulation():
    print("Choose Simulation Type:")
    print("1 - Clean (No loss or corruption)")
    print("2 - Loss only")
    print("3 - Corruption only")
    print("4 - Loss + Corruption")

    choice = input("Enter choice [1-4]: ").strip()
    config = {"type": choice}

    if choice == "2":
        config["drop_rate"] = float(input("Enter drop rate (0 to 1): "))
    elif choice == "3":
        config["corrupt_rate"] = float(input("Enter corruption rate (0 to 1): "))
    elif choice == "4":
        config["drop_rate"] = float(input("Enter drop rate (0 to 1): "))
        config["corrupt_rate"] = float(input("Enter corruption rate (0 to 1): "))

    write_python_config(config)
    return create_socket_from_config(config)

def create_socket_from_config(config):
    if config["type"] == "2":
        return LossRUDPSocket(drop_rate=config["drop_rate"])
    elif config["type"] == "3":
        return CorruptRUDPSocket(corrupt_rate=config["corrupt_rate"])
    elif config["type"] == "4":
        return LossCorruptRUDPSocket(
            drop_rate=config["drop_rate"],
            corrupt_rate=config["corrupt_rate"]
        )
    else:
        return CleanRUDPSocket()

# Only prompt if config doesn't exist
try:
    from rudp_config import config
    rudp_socket = create_socket_from_config(config)
except (ImportError, FileNotFoundError, AttributeError):
    rudp_socket = choose_simulation()
