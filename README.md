# 🛡️ Automated Compliance & Policy Enforcer

An end-to-end DevSecOps system that continuously monitors infrastructure, enforces strict security policies, and automatically remediates compliance violations in real-time.

## 🏗️ Architecture & Tech Stack

* **Provisioning:** Terraform (Builds compliant and non-compliant Docker containers for testing)
* **Auditing Engine:** Python (Continuous daemon, querying system state via Docker APIs and internal container execution)
* **Remediation & Enforcement:** Ansible (Executes targeted playbooks to quarantine failing infrastructure)

## 📜 Monitored Policies (Full-Stack Auditing)

**Outside-In Checks (API Level):**
* **POL-01 (Root Execution Ban):** Containers must not run under UID 0.
* **POL-02 (SSH Port Closure):** Containers must not expose port 22 externally.
* **POL-05 (No Plaintext Traffic):** Containers must not expose unencrypted HTTP port 80.

**Inside-Out Checks (System Level):**
* **POL-03 (Strict File Permissions):** Sensitive files (e.g., `/etc/shadow`) must enforce strict `400` permissions.
* **POL-04 (Required Auditing Tool):** Mandatory security daemons (e.g., `auditd`) must be actively running inside the container.

## 🚀 How It Works (The Enforcement Loop)

1. The **Python Daemon** fetches all running infrastructure every 5 seconds.
2. It parses both the external API configuration and internal system state of each container against the defined YAML policy rules.
3. If a container violates a policy, the daemon instantly triggers a targeted **Ansible Webhook**.
4. Ansible safely quarantines and destroys the non-compliant container with zero human intervention.
