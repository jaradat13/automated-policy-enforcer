import subprocess
import sys

def trigger_remediation(container_name):
    """Triggers the Ansible playbook to quarantine the specific container."""
    print(f"  [!] Triggering automated remediation for '{container_name}'...")
    try:
        # Suppress Ansible's standard output to keep our terminal clean, 
        # but execute the playbook passing the target container name as an extra var
        subprocess.run([
            'ansible-playbook', 
            'configuration/remediation.yml', 
            '-e', f'target_container={container_name}'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  [SUCCESS] Remediation complete. '{container_name}' has been safely quarantined.")
    except subprocess.CalledProcessError:
        print(f"  [ERROR] Remediation failed for '{container_name}'.")

def check_root_execution(container_name):
    """Checks Docker container user and triggers remediation if non-compliant."""
    try:
        result = subprocess.run(
            ['docker', 'inspect', "--format={{.Config.User}}", container_name],
            capture_output=True, text=True, check=True
        )
        user = result.stdout.strip().strip("'")
        
        if not user or user == '0' or user.lower() == 'root':
            print(f"[FAIL] POL-01 Violation: Container '{container_name}' is running as root.")
            trigger_remediation(container_name)
            return False
        else:
            print(f"[PASS] POL-01 Compliant: Container '{container_name}' is running as user '{user}'.")
            return True
            
    except subprocess.CalledProcessError:
        # If the container doesn't exist, it might have already been quarantined or never spun up
        print(f"[INFO] Container '{container_name}' not found. (It may have been quarantined).")
        return False

if __name__ == "__main__":
    print("--- Auditor Agent Initialized ---")
    print("Running Policy Checks...\n")
    
    check_root_execution('non_compliant_app')
    check_root_execution('compliant_app')
