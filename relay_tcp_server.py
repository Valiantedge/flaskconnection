import socket
import threading

LISTEN_PORT = 9000

def handle_client(client_sock):
    # Ask for target IP/port
    target = input("Enter target (ip:port): ")
    client_sock.sendall((target + "\n").encode())

    # Relay traffic between cloud and agent
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

    threading.Thread(target=forward, args=(client_sock, client_sock)).start()


def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', LISTEN_PORT))
    s.listen(1)
    print(f"Listening on port {LISTEN_PORT}...")
    while True:
        client_sock, addr = s.accept()
        print(f"Agent connected from {addr}")
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    main()
