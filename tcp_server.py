import socket
import json

def start_tcp_server(listen_ip, listen_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((listen_ip, listen_port))
        server_sock.listen(1)
        print(f"Server listening on {listen_ip}:{listen_port}")
        conn, addr = server_sock.accept()
        with conn:
            print(f"Connected by {addr}")
            # Send SSH details as JSON
            ssh_details = {
                "ip": "192.168.32.243",  # Change as needed
                "username": "ubuntu",  # Change as needed
                "password": "192.168.32.243"
            }
            conn.sendall(json.dumps(ssh_details).encode())
            while True:
                # Input command to send to agent
                command = input("Enter command to run on remote server (or 'exit' to quit): ")
                if command.strip().lower() == 'exit':
                    break
                conn.sendall(command.encode())
                # Receive output from agent
                output = conn.recv(65536).decode()
                print(f"Output from agent:\n{output}")

if __name__ == "__main__":
    # Example usage: listen on 0.0.0.0:9000
    start_tcp_server("0.0.0.0", 9000)
