import socket
import threading

LISTEN_PORT = 9000
AGENT_IP = '49.207.243.218'  # Change to your relay agent's IP
AGENT_PORT = 9000            # Port agent is listening on

def handle_client(client_sock):
    target = input("Enter target (ip:port): ")
    try:
        # Connect to agent
        agent_sock = socket.socket()
        agent_sock.connect((AGENT_IP, AGENT_PORT))
        # Send target info to agent
        agent_sock.sendall((target + "\n").encode())
    except Exception as e:
        print(f"[Server] Error connecting to agent: {e}")
        client_sock.close()
        return

    # Relay traffic between cloud client and agent
    def forward(src, dst, direction):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    print(f"[Server] Connection closed: {direction}")
                    break
                dst.sendall(data)
        except Exception as e:
            print(f"[Server] Forward error ({direction}): {e}")
        finally:
            src.close()
            dst.close()

    threading.Thread(target=forward, args=(client_sock, agent_sock, 'client->agent')).start()
    threading.Thread(target=forward, args=(agent_sock, client_sock, 'agent->client')).start()

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', LISTEN_PORT))
    s.listen(5)
    print(f"Listening on port {LISTEN_PORT}...")
    while True:
        client_sock, addr = s.accept()
        print(f"Cloud client connected from {addr}")
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    main()
