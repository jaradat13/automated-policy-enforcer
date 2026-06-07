# 🛡️ Automated Compliance & Policy Enforcer (V2.1)

An enterprise-grade, event-driven DevSecOps system that continuously monitors infrastructure, enforces strict security policies, and automatically remediates compliance violations with zero latency.

## 🏗️ Architecture & Tech Stack

* **Provisioning:** Terraform (Builds compliant and non-compliant Docker containers for testing)
* **Auditing Engine:** Python (Event-driven daemon utilizing the Docker Event Stream)
* **Remediation & Enforcement:** Ansible (Executes targeted playbooks to quarantine failing infrastructure)

## ⚡ Key Enterprise Features

1. **Zero-Latency Event Monitoring:** Subscribes directly to the `docker events` socket. Instead of resource-heavy polling, it intercepts container `start` events to catch rogue deployments the exact millisecond they spin up.
2. **Pre-Flight Baseline Sweep:** Upon initialization, the engine audits the entire existing state of the infrastructure to neutralize legacy threats before transitioning to live monitoring.
3. **Idempotent Test Harness:** Includes automated setup and teardown scripts to prevent state pollution and port collisions during CI/CD testing.

## 📜 Monitored Policies (Full-Stack Auditing)

**Outside-In Checks (API Level):**
* **POL-01 (Root Execution Ban):** Containers must not run under UID 0.
* **POL-02 (SSH Port Closure):** Containers must not expose port 22 externally.
* **POL-05 (No Plaintext Traffic):** Containers must not expose unencrypted HTTP port 80.

**Inside-Out Checks (System Level):**
* **POL-03 (Strict File Permissions):** Sensitive files (e.g., `/etc/shadow`) must enforce strict `400` permissions.
* **POL-04 (Required Auditing Tool):** Mandatory security daemons (e.g., `auditd`) must be actively running inside the container.

## 🚀 How to Run the Live Demo

We have included an automated test harness that provisions the infrastructure, handles state cleanup, starts the daemon, and simulates a live attack to demonstrate the zero-latency reaction time.

```bash
# 1. Ensure the test harness is executable
chmod +x test_v2.sh

# 2. Execute the live demo
./test_v2.sh 
