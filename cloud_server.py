# cloud_server.py
"""
This script runs on the cloud server and executes SSH/Ansible tasks directly.
"""
import subprocess
import sys

def run_ansible_playbook(inventory, playbook):
    cmd = [
        "ansible-playbook",
        "-i", inventory,
        playbook
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
        return result.stdout, result.stderr
    except Exception as e:
        print(f"Error running playbook: {e}")
        return None, str(e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cloud_server.py <inventory.ini> <playbook.yml>")
        sys.exit(1)
    run_ansible_playbook(sys.argv[1], sys.argv[2])
