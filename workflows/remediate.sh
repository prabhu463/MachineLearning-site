#!/usr/bin/env bash
set -euo pipefail

incident_id="${1:-0}"
action="${2:-restart service}"

echo "Simulating remediation for incident ${incident_id}"
echo "Action: ${action}"
echo "Status: simulated"
