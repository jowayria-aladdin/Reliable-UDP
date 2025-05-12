import subprocess
import time
from pick_sim import pick_mode  # Import the pick_mode function

def main():
    # Run the pick_mode function to select simulation mode
    pick_mode()

    # Wait for the server to be ready (adjust the wait time if needed)
    time.sleep(2)  # You can adjust the wait time if needed
    
    print("[+] Starting client...")

    # Run the client with the correct simulation mode set by pick_sim
    subprocess.run(["python", "RUDP_test_client.py"])

if __name__ == "__main__":
    main()
