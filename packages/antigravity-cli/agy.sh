#!/usr/bin/env bash
#
# Antigravity CLI Launcher Wrapper
#

set -euo pipefail

# Ensure DNF/RPM manages CLI updates, not internal self-updater
export AGY_CLI_DISABLE_AUTO_UPDATE=true

exec /usr/libexec/antigravity-cli/agy "$@"
