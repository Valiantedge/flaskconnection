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
                "password": "Cvbnmjkl@30263"
            }
            conn.sendall(json.dumps(ssh_details).encode())
            # List of commands to run automatically
            commands = [
                "whoami",
                "uname -a",
                "ls /home/ubuntu",
                # Add more commands as needed
            ]
            for command in commands:
                print(f"Sending command: {command}")
                conn.sendall(command.encode())
                output = conn.recv(65536).decode()
                print(f"Output from agent for '{command}':\n{output}")
            # Optionally, close the connection after running all commands
            print("All commands sent. Closing connection.")

if __name__ == "__main__":
    # Example usage: listen on 0.0.0.0:9000
    start_tcp_server("0.0.0.0", 9000)
