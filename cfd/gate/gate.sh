#!/bin/bash
# Forced command of the agent's SSH key (authorized_keys: restrict,command="<this file>").
# OpenSSH runs this script whatever the client requests; the request is passed in SSH_ORIGINAL_COMMAND.
exec /path/to/python-env/bin/python3 /path/to/project/v19_cfd/gated/gate.py
