from rudp_simulations import (
    CleanRUDPSocket,
    LossRUDPSocket,
    CorruptRUDPSocket,
    LossCorruptRUDPSocket,
    SYN,
    ACK,
    FIN
)
import os

CONFIG_FILE = "rudp_config.py"

def write_python_config(config_dict):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"config = {repr(config_dict)}\n")

def get_rate(prompt):
    while True:
        try:
            rate = float(input(prompt))
            if 0.0 <= rate <= 1.0:
                return rate
            else:
                print("Please enter a number between 0 and 1.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def get_simulation_choice():
    while True:
        print("Choose Simulation Type:")
        print("1 - Clean (No loss or corruption)")
        print("2 - Loss only")
        print("3 - Corruption only")
        print("4 - Loss + Corruption")
        choice = input("Enter choice [1-4]: ").strip()
        if choice in {"1", "2", "3", "4"}:
            return choice
        else:
            print("Invalid choice. Please select a valid option (1-4).")

def choose_simulation():
    choice = get_simulation_choice()
    config = {"type": choice}

    if choice == "2":
        config["drop_rate"] = get_rate("Enter drop rate (0 to 1): ")
    elif choice == "3":
        config["corrupt_rate"] = get_rate("Enter corruption rate (0 to 1): ")
    elif choice == "4":
        config["drop_rate"] = get_rate("Enter drop rate (0 to 1): ")
        config["corrupt_rate"] = get_rate("Enter corruption rate (0 to 1): ")

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

# Load saved simulation config or prompt the user
try:
    from rudp_config import config
    rudp_socket = create_socket_from_config(config)
except (ImportError, FileNotFoundError, AttributeError):
    rudp_socket = choose_simulation()
