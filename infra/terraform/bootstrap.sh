#!/bin/bash
set -euo pipefail
umask 027
# Needs approved access to AL2023 repositories and SSM endpoints.
dnf install -y docker python3
systemctl enable --now docker
systemctl enable --now amazon-ssm-agent
install -d -m 0750 /opt/ssdlc-dast-poc
# Does not download this repo, credentials, scanners, targets or run scans.
