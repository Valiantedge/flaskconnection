import socket
import paramiko
import json

def run_remote_command(command: str, ip: str, username: str, password: str) -> str:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode() + stderr.read().decode()
        ssh.close()
        return output
    except Exception as e:
        return f"Error running command on private server: {e}"

def run_agent_tcp(server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        print(f"Connected to server {server_ip}:{server_port}")
        # Receive SSH details as JSON
        ssh_details_msg = s.recv(4096).decode()
        try:
            ssh_details = json.loads(ssh_details_msg)
            ip = ssh_details["ip"]
            username = ssh_details["username"]
            password = ssh_details["password"]
        except Exception as e:
            print(f"Error parsing SSH details: {e}")
            return
        print(f"Loaded SSH details: {ip}, {username}")
        while True:
            # Wait for command from server
            command = s.recv(4096).decode()
            if not command:
                break
            print(f"Received command from server: {command}")
            # Run the command on the private server via SSH
            output = run_remote_command(command, ip, username, password)
            # Send output back to server
            s.sendall(output.encode())
            print("Output from private server:")
            print(output)

if __name__ == "__main__":
    # Example usage: connect to server at 13.58.212.239:9000
    run_agent_tcp("13.58.212.239", 9000)
