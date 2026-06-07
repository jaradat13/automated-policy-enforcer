import subprocess
import json
import sys

def trigger_remediation(container_name):
    print(f"  [!] Triggering automated remediation for '{container_name}'...")
    try:
        result = subprocess.run([
            'ansible-playbook', 'configuration/remediation.yml', 
            '-e', f'target_container={container_name}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and "changed=0" not in result.stdout:
            print(f"  [SUCCESS] '{container_name}' safely quarantined.")
        else:
            print(f"  [WARNING/ERROR] Remediation failed or made no changes.")
    except Exception as e:
        print(f"  [FATAL ERROR] {str(e)}")

def check_root_execution(container_name):
    try:
        result = subprocess.run(['docker', 'inspect', "--format={{.Config.User}}", container_name], capture_output=True, text=True, check=True)
        user = result.stdout.strip().strip("'")
        if not user or user == '0' or user.lower() == 'root':
            print(f"[FAIL] POL-01: Container '{container_name}' running as root.")
            trigger_remediation(container_name)
            return False
    except subprocess.CalledProcessError: pass
    return True

def check_forbidden_ports(container_name, policy_id, forbidden_port):
    try:
        result = subprocess.run(['docker', 'inspect', "--format={{json .NetworkSettings.Ports}}", container_name], capture_output=True, text=True, check=True)
        if result.stdout.strip() == "null": return True
        ports_dict = json.loads(result.stdout)
        if forbidden_port in ports_dict and ports_dict[forbidden_port] is not None:
            print(f"[FAIL] {policy_id}: Container '{container_name}' exposes forbidden port {forbidden_port}.")
            trigger_remediation(container_name)
            return False
    except subprocess.CalledProcessError: pass
    return True

def check_file_permissions(container_name, target_file="/etc/shadow", expected_mask="400"):
    try:
        result = subprocess.run(['docker', 'exec', container_name, 'stat', '-c', '%a', target_file], capture_output=True, text=True)
        if result.returncode == 0:
            mask = result.stdout.strip()
            if mask != expected_mask:
                print(f"[FAIL] POL-03: '{container_name}' has weak permissions ({mask}) on {target_file}.")
                trigger_remediation(container_name)
                return False
    except subprocess.CalledProcessError: pass
    return True

def check_required_process(container_name, required_process="auditd"):
    try:
        result = subprocess.run(['docker', 'exec', container_name, 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            if required_process not in result.stdout:
                print(f"[FAIL] POL-04: '{container_name}' is missing required auditing tool '{required_process}'.")
                trigger_remediation(container_name)
                return False
    except subprocess.CalledProcessError: pass
    return True

def listen_to_events():
    """V2.0: Subscribes directly to the Docker event stream for zero-latency monitoring."""
    print("\n--- V2.0 Event-Driven Security Daemon Started ---")
    print("Listening for live container 'start' events. Press Ctrl+C to stop.\n")
    
    try:
        # Open a persistent connection to the Docker event socket
        process = subprocess.Popen(
            ['docker', 'events', '--filter', 'event=start', '--format', '{{.Actor.Attributes.name}}'],
            stdout=subprocess.PIPE,
            text=True
        )
        
        # Iterates infinitely, blocking until a new line is printed to stdout by the docker daemon
        for line in iter(process.stdout.readline, ''):
            container_name = line.strip()
            if container_name:
                print(f"\n[EVENT] New container deployed: '{container_name}'. Initiating real-time audit...")
                
                # Execute the enforcement loop
                if not check_root_execution(container_name): continue
                if not check_forbidden_ports(container_name, "POL-02", "22/tcp"): continue
                if not check_forbidden_ports(container_name, "POL-05", "80/tcp"): continue
                if not check_file_permissions(container_name): continue
                if not check_required_process(container_name): continue
                
                print(f"[PASS] Container '{container_name}' is fully compliant.")
                
    except KeyboardInterrupt:
        process.terminate()
        print("\n[INFO] Security Daemon gracefully stopped.")

if __name__ == "__main__":
    listen_to_events()
