#!/bin/bash
# Run by the approver before the gated execution.
# 1. Saves the current authorized_keys to authorized_keys.before_gate.
# 2. Disables (comments out) every existing key, so that no unrestricted key is usable during the execution.
# 3. Adds the agent's forced-command key, whose only possible command is the gate.
# Password login of the account holder is not affected. restore_keys.sh undoes all three steps.
set -euo pipefail
AK=$HOME/.ssh/authorized_keys
[ -f "$AK.before_gate" ] && { echo "backup already exists; run restore_keys.sh first"; exit 1; }
cp -p "$AK" "$AK.before_gate"
sed -i 's/^\(ssh-\|ecdsa-\|sk-\)/# disabled during gated execution: &/' "$AK"
echo 'restrict,command="/path/to/project/v19_cfd/gated/gate.sh" ssh-ed25519 <agent-public-key> gated-agent' >> "$AK"
echo "Active keys now (first 70 characters):"
grep -v '^#' "$AK" | grep -v '^\s*$' | cut -c1-70
