from RUDP_Socket import RUDPsocket
import threading
import time

def rudp_server():
    server = RUDPsocket()
    server.bind(('localhost', 9000))
    print("Server: waiting for connection...")
    conn = server.accept()
    print("Server: connected.")
    while True:
        try:
            data = conn.receive_data()
            print("Server received:", data.decode())
            conn.send_data(b"ACK: " + data)
        except Exception as e:
            print("Server error:", e)
            break
    conn.close()
    print("Server closed.")

def rudp_client():
    time.sleep(1)
    client = RUDPsocket(loss_rate=0.1, corruption_rate=0.1)
    client.connect(('localhost', 9000))
    print("Client: connected.")
    client.send_data(b"Hello, RUDP!")
    response = client.receive_data()
    print("Client received:", response.decode())
    client.close()
    print("Client closed.")

if __name__ == "__main__":
    t1 = threading.Thread(target=rudp_server)
    t2 = threading.Thread(target=rudp_client)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
