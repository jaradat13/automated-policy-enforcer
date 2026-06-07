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

## 🚧 Production Readiness & Future Enhancements

This architecture serves as a Proof of Concept (PoC). To scale this engine for a live enterprise environment, the following architectural upgrades would be required:

1. **Event-Driven Execution:** Replace the 5-second polling loop with a direct hook into the Docker Event Stream to trigger audits asynchronously on container creation.
2. **Native API Integration:** Refactor the Python agent to utilize the official Docker SDK for Python rather than executing CLI commands via `subprocess`.
3. **Structured Logging:** Implement JSON-structured logging (e.g., Elasticsearch/Kibana) to track remediation events, replacing standard standard output.
4. **Pre-Deployment Blocking:** Shift from reactive termination to proactive blocking using Kubernetes Admission Controllers (e.g., OPA Gatekeeper) to prevent non-compliant infrastructure from deploying initially.
