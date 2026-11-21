Name:           orca-ide
Version:        1.4.269
Release:        1%{?dist}
Summary:        Next-gen IDE for parallel agentic development

License:        MIT
URL:            https://github.com/stablyai/orca
Source0:        https://github.com/stablyai/orca/releases/download/v%{version}/orca-ide-%{version}.x86_64.rpm
Source1:        https://github.com/stablyai/orca/releases/download/v%{version}/orca-ide-%{version}.aarch64.rpm
Source2:        orca-ide.metainfo.xml

ExclusiveArch:  x86_64 aarch64

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       libsecret
Requires:       xdg-utils

# Disable debuginfo package generation and stripping for pre-built Electron binaries
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

# Filter private bundled shared libraries and internal resources
%global __requires_exclude_from ^/opt/Orca/resources/.*$
%global __requires_exclude ^(libffmpeg|libvk_swiftshader|libvulkan|libEGL|libGLESv2)\.so.*$
%global __provides_exclude_from ^/opt/Orca/.*$

%description
Orca is an agentic development environment designed for running parallel autonomous
coding sessions, managing Git worktrees, and orchestrating AI developer agents.
Features include deep Model Context Protocol (MCP) and agent integration, built-in
browser testing, parallel terminal workflows, and unified review interfaces.

This package repackages the official Stably AI RPM release for Fedora, installing
the IDE and the orca-ide CLI tool.

%prep
%setup -q -c -T -n orca-ide-%{version}
%ifarch x86_64
rpm2cpio %{SOURCE0} | cpio -idmv
%elifarch aarch64
rpm2cpio %{SOURCE1} | cpio -idmv
%endif

%build
# Pre-compiled binary release; no compilation needed

%install
rm -rf %{buildroot}

# Install application directory
mkdir -p %{buildroot}/opt/Orca
cp -a opt/Orca/. %{buildroot}/opt/Orca/

# Remove bundled non-Linux and cross-architecture ripgrep binaries
rm -rf %{buildroot}/opt/Orca/resources/ripgrep/darwin-*
rm -rf %{buildroot}/opt/Orca/resources/ripgrep/win32-*
%ifarch x86_64
rm -rf %{buildroot}/opt/Orca/resources/ripgrep/linux-arm64
%elifarch aarch64
rm -rf %{buildroot}/opt/Orca/resources/ripgrep/linux-x64
%endif

# Set executable and chrome-sandbox permissions
chmod 755 %{buildroot}/opt/Orca/orca-ide
chmod 755 %{buildroot}/opt/Orca/resources/bin/orca-ide
chmod 4755 %{buildroot}/opt/Orca/chrome-sandbox 2>/dev/null || true

# Create binary symlink in /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -sf /opt/Orca/resources/bin/orca-ide %{buildroot}%{_bindir}/orca-ide

# Install desktop entry with normalized MimeType and standard categories
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install \
  --dir=%{buildroot}%{_datadir}/applications \
  --set-key=MimeType --set-value="text/markdown;text/csv;text/tab-separated-values;x-scheme-handler/orca;" \
  --remove-category=Utility \
  --add-category=Development \
  --add-category=IDE \
  usr/share/applications/orca-ide.desktop

# Install AppStream metadata
mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/orca-ide.metainfo.xml

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons
cp -a usr/share/icons/. %{buildroot}%{_datadir}/icons/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/orca-ide.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/orca-ide.metainfo.xml

%files
%license opt/Orca/LICENSE.electron.txt opt/Orca/LICENSES.chromium.html
/opt/Orca/
%{_bindir}/orca-ide
%{_datadir}/applications/orca-ide.desktop
%{_datadir}/metainfo/orca-ide.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/orca-ide.png

%changelog
* Sat Nov 21 2026 Azhar Momin <azhar-momin@outlook.com> - 1.4.269-1
- Upstream release update to 1.4.269

* Sat Nov 21 2026 Azhar Momin <azhar-momin@outlook.com> - 1.4.268-1
- Upstream release update to 1.4.268

* Sat Nov 21 2026 Azhar Momin <azhar-momin@outlook.com> - 1.4.266-2
- Filter internal resources and foreign architecture dependencies (aarch64, musl, glibc symbols)
- Remove bundled non-Linux and cross-architecture ripgrep binaries

* Fri Nov 20 2026 Azhar Momin <azhar-momin@outlook.com> - 1.4.266-1
- Initial Fedora RPM packaging for Orca IDE 1.4.266
- Repackage official Linux x86_64 and aarch64 releases from Stably AI
- Provide orca-ide CLI launcher in /usr/bin and AppStream metadata
