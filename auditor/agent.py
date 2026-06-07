import subprocess
import json
import time

def trigger_remediation(container_name):
    print(f"  [!] Triggering automated remediation for '{container_name}'...")
    try:
        subprocess.run([
            'ansible-playbook', 'configuration/remediation.yml', 
            '-e', f'target_container={container_name}'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  [SUCCESS] '{container_name}' safely quarantined.")
    except subprocess.CalledProcessError:
        print(f"  [ERROR] Remediation failed for '{container_name}'.")

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
    """POL-03: Executes 'stat' inside the container to check file permissions."""
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
    """POL-04: Executes 'ps' inside the container to verify required tools are running."""
    try:
        result = subprocess.run(['docker', 'exec', container_name, 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            if required_process not in result.stdout:
                print(f"[FAIL] POL-04: '{container_name}' is missing required auditing tool '{required_process}'.")
                trigger_remediation(container_name)
                return False
    except subprocess.CalledProcessError: pass
    return True

def get_running_containers():
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], capture_output=True, text=True, check=True)
        return [c for c in result.stdout.strip().split('\n') if c]
    except subprocess.CalledProcessError: return []

if __name__ == "__main__":
    print("\n--- Full-Stack Compliance Daemon Started (5 Policies) ---")
    print("Monitoring infrastructure every 5 seconds. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            running_containers = get_running_containers()
            for container in running_containers:
                # If a container fails and is remediated, we skip the remaining checks for that loop
                if not check_root_execution(container): continue
                if not check_forbidden_ports(container, "POL-02", "22/tcp"): continue
                if not check_forbidden_ports(container, "POL-05", "80/tcp"): continue
                if not check_file_permissions(container): continue
                if not check_required_process(container): continue
                
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[INFO] Security Daemon stopped by user.")
