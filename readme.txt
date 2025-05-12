==============================
         RUDP PROJECT
==============================

1. RUDPsocket_base.py
   - Defines the base RUDP socket class with methods for reliable data transmission over UDP.

2. RUDPsocket_clean.py
   - Extends RUDPsocket_base.py with no packet loss or corruption (clean simulation).

3. RUDPsocket_loss.py
   - Extends RUDPsocket_base.py to simulate packet loss.

4. RUDPsocket_corrupt.py
   - Extends RUDPsocket_base.py to simulate packet corruption.

5. RUDPsocket_loss_corrupt.py
   - Extends RUDPsocket_base.py to simulate both packet loss and corruption.

6. RUDP_test_server.py
   - Implements a test server using the RUDP socket with corruption simulation.

7. RUDP_test_client.py
   - Implements a test client using the RUDP socket with corruption simulation.

8. http_server.py
   - Implements an HTTP server that operates over a reliable UDP connection.

9. http_client.py
   - Implements an HTTP client that communicates with the RUDP server.

10. pick_sim.py
    - A script to pick different RUDP socket simulations for testing (loss, corruption, or both).

11. run_all.py (windows compatible only)
    - Runs the full system: starts the HTTP server, executes the HTTP client, and then shuts down the server.

==============================
