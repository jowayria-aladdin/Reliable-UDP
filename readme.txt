==============================
         RUDP PROJECT
==============================

1. RUDPsocket_base.py  
   - Defines the base RUDP socket class that provides reliable data transmission over UDP, including retransmission, checksums, and ordering.

2. RUDPsocket_clean.py  
   - Inherits from the base socket class and simulates a clean environment with no packet loss or corruption.

3. RUDPsocket_loss.py  
   - Inherits from the base class and introduces artificial packet loss for testing reliability.

4. RUDPsocket_corrupt.py  
   - Inherits from the base class and introduces packet corruption for testing error detection.

5. RUDPsocket_loss_corrupt.py  
   - Inherits from the base class and simulates both packet loss and corruption.

6. RUDP_test_server.py  
   - Auto-generated server script for testing RUDP communication using the selected simulation mode.

7. RUDP_test_client.py  
   - Auto-generated client script for testing RUDP communication using the selected simulation mode.

8. http_server.py  
   - An HTTP server built on top of the RUDP socket layer, demonstrating reliable HTTP functionality over UDP.

9. http_client.py  
   - An HTTP client built on top of the RUDP socket layer to test HTTP request/response over simulated unreliable transport.

10. pick_sim.py  
    - CLI tool to select a simulation mode and dynamically generate test client/server files using templates.

11. run_all.py (Windows-compatible only)  
    - Launches `pick_sim.py` to let the user choose a simulation mode and then runs the generated client/server automatically.

12. RUDP_test_server_template.py  
    - Template file used by `pick_sim.py` to generate the actual `RUDP_test_server.py` based on the selected simulation.

13. RUDP_test_client_template.py  
    - Template file used by `pick_sim.py` to generate the actual `RUDP_test_client.py` based on the selected simulation.

==============================
