# amazingakai/copr

[![Fedora COPR](https://img.shields.io/badge/Fedora%20COPR-amazingakai%2Fcopr-294172?logo=fedora&logoColor=white)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/)
[![Supported Fedora](https://img.shields.io/badge/Fedora-43%20%7C%2044%20%7C%2045-blue?logo=fedora&logoColor=white)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/)
[![Architectures](https://img.shields.io/badge/Arch-x86__64%20%7C%20aarch64-blue)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/)
[![Build and Dispatch to Fedora COPR](https://github.com/amazingakai/copr/actions/workflows/copr-build.yml/badge.svg)](https://github.com/amazingakai/copr/actions/workflows/copr-build.yml)
[![Upstream Version Checker](https://github.com/amazingakai/copr/actions/workflows/version-check.yml/badge.svg)](https://github.com/amazingakai/copr/actions/workflows/version-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Personal Fedora COPR repository for custom, repackaged, and patched RPMs.

**COPR Project Page:** [copr.fedorainfracloud.org/coprs/amazingakai/copr](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/)

---

## Quick Start

### 1. Enable the COPR repository

```bash
sudo dnf copr enable amazingakai/copr
```

### 2. Install packages

```bash
# Antigravity Desktop Client
sudo dnf install -y antigravity

# Antigravity CLI
sudo dnf install -y antigravity-cli

# Antigravity Standalone IDE
sudo dnf install -y antigravity-ide

# Claude Code CLI
sudo dnf install -y claude-code

# Claude Desktop
sudo dnf install -y claude-desktop

# Delta
sudo dnf install -y delta

# OpenCode CLI
sudo dnf install -y opencode

# OpenCode Desktop
sudo dnf install -y opencode-desktop

# Orca IDE
sudo dnf install -y orca-ide

# Slack Desktop Client
sudo dnf install -y slack

# T3 Code
sudo dnf install -y t3code

# Zed Editor
sudo dnf install -y zed

# Zoom Workplace
sudo dnf install -y zoom
```

---

## Available Packages

| Package                | Command            | Version        | Build Status                                                                                                                                                                                                         | Description                               |
| :--------------------- | :----------------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------- |
| **`antigravity`**      | `antigravity`      | `2.35.2-1`     | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/antigravity/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/antigravity/)           | Google Antigravity Desktop Client         |
| **`antigravity-cli`**  | `agy`              | `1.5.18-1`     | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/antigravity-cli/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/antigravity-cli/)   | Google Antigravity CLI terminal interface |
| **`antigravity-ide`**  | `antigravity-ide`  | `2.9.0-1`      | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/antigravity-ide/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/antigravity-ide/)   | Google Antigravity Standalone IDE         |
| **`claude-code`**      | `claude`           | `2.1.332-1`    | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/claude-code/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/claude-code/)           | Claude Code Terminal Agent CLI            |
| **`claude-desktop`**   | `claude-desktop`   | `6.28899.6-1`  | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/claude-desktop/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/claude-desktop/)     | Claude Desktop Application & Code Agent   |
| **`delta`**            | `delta`            | `0.29.0-1`     | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/delta/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/delta/)                       | AI-native Collaborative Code Editor       |
| **`opencode`**         | `opencode`         | `2.4.1-1`      | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/opencode/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/opencode/)                 | Open-source AI Coding Agent for Terminal  |
| **`opencode-desktop`** | `opencode-desktop` | `2.4.1-1`      | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/opencode-desktop/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/opencode-desktop/) | OpenCode Desktop GUI Application          |
| **`orca-ide`**         | `orca-ide`         | `1.4.274-1`    | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/orca-ide/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/orca-ide/)                 | Next-gen IDE for Parallel Agentic Dev     |
| **`slack`**            | `slack`            | `4.53.287-1`   | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/slack/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/slack/)                       | Slack Desktop Client                      |
| **`t3code`**           | `t3code`           | `0.1.12-1`     | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/t3code/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/t3code/)                     | Open-source Control Plane for AI Agents   |
| **`zed`**              | `zed`              | `1.30.2-1`     | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/zed/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/zed/)                           | High-performance, Multiplayer Code Editor |
| **`zoom`**             | `zoom`             | `7.2.5.6661-1` | [![Build Status](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/zoom/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/amazingakai/copr/package/zoom/)                         | Zoom Workplace Video Conferencing         |

---

## License

This packaging repository and automation scripts are licensed under the [MIT License](LICENSE). Google Antigravity, Antigravity IDE, `agy`, Slack, Zoom, Claude Desktop, Claude Code, Orca, OpenCode, T3 Code, Zed, and Delta binaries are subject to their respective terms of service and software licenses.
