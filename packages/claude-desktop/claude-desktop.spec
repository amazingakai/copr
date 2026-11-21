Name:           claude-desktop
Version:        6.28899.2
Release:        1%{?dist}
Summary:        Claude Desktop - Desktop application for Claude with Code agent and MCP

License:        Proprietary
URL:            https://claude.ai
Source0:        https://downloads.claude.ai/claude-desktop/apt/stable/pool/main/c/claude-desktop/claude-desktop_%{version}_amd64.deb
Source1:        com.anthropic.Claude.metainfo.xml
Source2:        patch-titlebar.py

ExclusiveArch:  x86_64

BuildRequires:  python3
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       libsecret
Requires:       xdg-utils

# Disable debuginfo package generation and stripping for pre-built Electron binaries
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

# Filter private bundled libraries from provides and requires
%global __requires_exclude ^(libffmpeg|libvk_swiftshader|libvulkan)\\.so.*$
%global __provides_exclude_from ^/usr/lib/claude-desktop/.*$

%description
Claude Desktop brings the intelligence of Anthropic's Claude models directly
to your desktop. It includes a dedicated Code tab for agentic development with
visual diffs, parallel Git worktrees, terminal execution, live app browser
previews, and Model Context Protocol (MCP) integration.

%prep
%setup -q -c -T -n claude-desktop-%{version}
ar -x %{SOURCE0}
tar -xf data.tar.xz

# Patch app.asar to disable titleBarOverlay on Linux/KDE
python3 %{SOURCE2} usr/lib/claude-desktop/resources/app.asar

%build
# Pre-compiled binary release; no compilation needed

%install
rm -rf %{buildroot}

# Install application directory
mkdir -p %{buildroot}/usr/lib/claude-desktop
cp -a usr/lib/claude-desktop/. %{buildroot}/usr/lib/claude-desktop/

# Ensure executable and chrome-sandbox permissions
chmod 755 %{buildroot}/usr/lib/claude-desktop/claude-desktop
chmod 4755 %{buildroot}/usr/lib/claude-desktop/chrome-sandbox 2>/dev/null || true

# Create binary symlink in /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -sf ../lib/claude-desktop/claude-desktop %{buildroot}%{_bindir}/claude-desktop

# Install desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications usr/share/applications/com.anthropic.Claude.desktop

# Install AppStream metadata
mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/metainfo/com.anthropic.Claude.metainfo.xml

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons
cp -a usr/share/icons/. %{buildroot}%{_datadir}/icons/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.anthropic.Claude.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/com.anthropic.Claude.metainfo.xml

%files
/usr/lib/claude-desktop/
%{_bindir}/claude-desktop
%{_datadir}/applications/com.anthropic.Claude.desktop
%{_datadir}/metainfo/com.anthropic.Claude.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/claude-desktop.png

%changelog
* Sat Nov 21 2026 Azhar Momin <azhar-momin@outlook.com> - 6.28899.2-1
- Upstream release update to 6.28899.2

* Thu Nov 19 2026 Azhar Momin <azhar-momin@outlook.com> - 5.11492.5-2
- Patch app.asar to disable titleBarOverlay on Linux/KDE

* Wed Nov 18 2026 Azhar Momin <azhar-momin@outlook.com> - 5.11492.5-1
- Initial Fedora RPM packaging for Claude Desktop 5.11492.5
- Repackage official Linux x86_64 Debian release from Anthropic
- Add AppStream metainfo metadata for software center discovery
