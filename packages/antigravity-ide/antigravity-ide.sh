#!/usr/bin/env bash
#
# Antigravity IDE Launcher Wrapper
#

set -euo pipefail

APP_DIR="/opt/antigravity-ide"
BINARY="${APP_DIR}/bin/antigravity-ide"
CONFIG_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/antigravity-ide-flags.conf"

declare -a FLAGS=()

# Load user-specified flags if config exists
if [[ -f "${CONFIG_FILE}" ]]; then
    while IFS= read -r line || [[ -n "${line}" ]]; do
        if [[ "${line}" =~ ^[[:space:]]*# ]] || [[ -z "${line// }" ]]; then
            continue
        fi
        FLAGS+=("${line}")
    done < "${CONFIG_FILE}"
fi

exec "${BINARY}" "${FLAGS[@]}" "$@"
