#!/bin/bash
# Run by the approver after the gated execution: restores authorized_keys exactly as it was before.
set -euo pipefail
AK=$HOME/.ssh/authorized_keys
cp -p "$AK.before_gate" "$AK" && rm "$AK.before_gate"
echo "authorized_keys restored; active keys:"
grep -v '^#' "$AK" | grep -v '^\s*$' | awk '{print $NF}'
