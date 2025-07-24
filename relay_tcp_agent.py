import socket
import threading

CLOUD_SERVER_IP = '13.58.212.239'  # Cloud server public IP
CLOUD_SERVER_PORT = 9000           # Cloud server port

def handle_cloud_conn(cloud_conn):
    # Receive target info from cloud (format: "ip:port\n")
    target = cloud_conn.recv(128).decode().strip()
    target_ip, target_port = target.split(':')
    target_port = int(target_port)
    try:
        # Connect to target inside private network
        target_sock = socket.create_connection((target_ip, target_port))
    except Exception as e:
        cloud_conn.sendall(f"ERROR: {e}\n".encode())
        cloud_conn.close()
        return

    # Relay traffic between cloud and target
    def forward(src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except:
            pass
        finally:
            src.close()
            dst.close()

    threading.Thread(target=forward, args=(cloud_conn, target_sock)).start()
    threading.Thread(target=forward, args=(target_sock, cloud_conn)).start()

def main():
    s = socket.socket()
    s.connect((CLOUD_SERVER_IP, CLOUD_SERVER_PORT))
    while True:
        handle_cloud_conn(s)

if __name__ == "__main__":
    main()
