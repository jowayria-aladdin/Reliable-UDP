import subprocess

def pick_mode():
    print("Choose simulation mode:")
    print("1 - Clean (no loss/corruption)")
    print("2 - Loss only")
    print("3 - Corruption only")
    print("4 - Loss + Corruption")
    choice = input("Enter choice (1-4): ").strip()

    if choice == '1':
        server_module = 'RUDPsocket_clean'
        client_module = 'RUDPsocket_clean'
    elif choice == '2':
        server_module = 'RUDPsocket_loss'
        client_module = 'RUDPsocket_loss'
    elif choice == '3':
        server_module = 'RUDPsocket_corrupt'
        client_module = 'RUDPsocket_corrupt'
    elif choice == '4':
        server_module = 'RUDPsocket_loss_corrupt'
        client_module = 'RUDPsocket_loss_corrupt'
    else:
        print("Invalid choice.")
        return

    # Create temp versions of server and client with selected module
    with open("RUDP_test_server_template.py") as f:
        server_code = f.read().replace("{{RUDP_MODULE}}", server_module)
    with open("RUDP_test_server.py", "w") as f:
        f.write(server_code)

    with open("RUDP_test_client_template.py") as f:
        client_code = f.read().replace("{{RUDP_MODULE}}", client_module)
    with open("RUDP_test_client.py", "w") as f:
        f.write(client_code)

    print(f"\n[+] Simulation set to: {choice} ({server_module})")
    print("[+] Starting server...\n")

    # Run server in new terminal
    subprocess.Popen(["python", "RUDP_test_server.py"])

    input("\n[+] Press Enter to start client...")
    subprocess.run(["python", "RUDP_test_client.py"])

if __name__ == "__main__":
    pick_mode()
