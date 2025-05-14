import subprocess
import time
import os

# Start the HTTP server in a background process
server_process = subprocess.Popen(
    ["python", "http_server.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait a bit to ensure the server has started
time.sleep(2)

# Run the HTTP client (waits until done)
subprocess.run(["python", "http_client.py"])

# Give the client time to finish up
time.sleep(1)

# Terminate the server process (using taskkill on Windows)
server_process.kill()
print("\n[+] Server terminated.")
