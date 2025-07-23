if __name__ == "__main__":
    # Example usage: run a command on the private server
    cmd = "ls -l"
    print(f"Running command: {cmd}")
    result = run_remote_command(cmd)
    print("Output:")
    print(result)
import paramiko

PRIVATE_SERVER_IP = "192.168.32.243"  # Change to your private server IP
SSH_USER = "ubuntu"                   # Change to your SSH username
SSH_PASSWORD = "Cvbnmjkl@30263"      # Change to your SSH password

def run_remote_command(command: str) -> str:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(PRIVATE_SERVER_IP, username=SSH_USER, password=SSH_PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode() + stderr.read().decode()
        ssh.close()
        return output
    except Exception as e:
        return f"Error running command on private server: {e}"
