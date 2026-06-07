# Automated Compliance & Policy Enforcer

An automated security pipeline that audits infrastructure against defined policies and automatically remediates violations.

## Architecture
* **Infrastructure:** Terraform & Docker
* **Configuration / Remediation:** Ansible
* **Auditor Agent:** Python

## Current Capabilities
* **POL-01 (Root Execution Ban):** Actively monitored and enforced. Non-compliant containers are automatically quarantined via Ansible playbooks.
