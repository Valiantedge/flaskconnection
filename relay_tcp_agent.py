import socket
import threading

CLOUD_SERVER_IP = '13.58.212.239'  # Cloud server public IP
CLOUD_SERVER_PORT = 9000           # Cloud server port

def main():
    while True:
        try:
            s = socket.socket()
            s.connect((CLOUD_SERVER_IP, CLOUD_SERVER_PORT))
            handle_cloud_conn(s)
            s.close()
        except Exception as e:
            print(f"[Agent] Main loop error: {e}")

def handle_cloud_conn(cloud_conn):
    print("[Agent] Waiting for target info from cloud...")
    target_bytes = b''
    try:
        while not target_bytes.endswith(b'\n'):
            chunk = cloud_conn.recv(1)
            if not chunk:
                print("[Agent] Connection closed before target info received.")
                cloud_conn.close()
                return
            target_bytes += chunk
        print(f"[Agent] Received target info: {target_bytes}")
        target = target_bytes.decode(errors='replace').strip()
        print(f"[Agent] Decoded target: {target}")
        target_ip, target_port = target.split(':')
        target_port = int(target_port)
        print(f"[Agent] Connecting to target {target_ip}:{target_port}...")
        try:
            # Connect to target inside private network
            target_sock = socket.create_connection((target_ip, target_port))
            print(f"[Agent] Connected to target {target_ip}:{target_port}")
        except Exception as e:
            print(f"[Agent] ERROR connecting to target: {e}")
            cloud_conn.sendall(f"ERROR: {e}\n".encode())
            cloud_conn.close()
            return

        # Relay traffic between cloud and target (raw bytes)
        def forward(src, dst, direction):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        print(f"[Agent] Connection closed: {direction}")
                        break
                    dst.sendall(data)
            except Exception as e:
                print(f"[Agent] Forward error ({direction}): {e}")
            finally:
                src.close()
                dst.close()

        threading.Thread(target=forward, args=(cloud_conn, target_sock, 'cloud->target')).start()
        threading.Thread(target=forward, args=(target_sock, cloud_conn, 'target->cloud')).start()
    except Exception as e:
        print(f"[Agent] Unexpected error: {e}")
        cloud_conn.close()

def main():
    s = socket.socket()
    s.connect((CLOUD_SERVER_IP, CLOUD_SERVER_PORT))
    while True:
        handle_cloud_conn(s)

if __name__ == "__main__":
    main()
