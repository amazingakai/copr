#!/usr/bin/env bash
#
# Antigravity Desktop Launcher Wrapper
#

set -euo pipefail

APP_DIR="/opt/antigravity"
BINARY="${APP_DIR}/antigravity"
CONFIG_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/antigravity-flags.conf"

declare -a FLAGS=(
    # Auto-detect Wayland or X11 for modern Electron runtimes
    "--ozone-platform-hint=auto"
)

# Load user-specified flags if config exists
if [[ -f "${CONFIG_FILE}" ]]; then
    while IFS= read -r line || [[ -n "${line}" ]]; do
        # Ignore comments and blank lines
        if [[ "${line}" =~ ^[[:space:]]*# ]] || [[ -z "${line// }" ]]; then
            continue
        fi
        FLAGS+=("${line}")
    done < "${CONFIG_FILE}"
fi

exec "${BINARY}" "${FLAGS[@]}" "$@"
