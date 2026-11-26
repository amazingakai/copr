Name:           opencode-desktop
Version:        2.4.2
Release:        1%{?dist}
Summary:        OpenCode Desktop - Graphical interface for the OpenCode AI coding agent

License:        MIT
URL:            https://opencode.ai
Source0:        https://github.com/anomalyco/opencode/releases/download/v%{version}/opencode-desktop-linux-amd64.deb
Source1:        https://github.com/anomalyco/opencode/releases/download/v%{version}/opencode-desktop-linux-arm64.deb

ExclusiveArch:  x86_64 aarch64

BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       libsecret
Requires:       xdg-utils

# Disable debuginfo package generation and stripping
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

# Filter private bundled shared libraries and internal resources
%global __requires_exclude_from ^/opt/OpenCode/resources/.*$
%global __requires_exclude ^(libffmpeg|libvk_swiftshader|libvulkan|libEGL|libGLESv2)\\.so.*$
%global __provides_exclude_from ^/opt/OpenCode/.*$

%description
OpenCode Desktop is the official graphical desktop application for OpenCode,
an open-source autonomous AI coding agent. It provides a visual workspace for
managing coding sessions, switching between plan and build agents, viewing code
diffs, and interacting with project trees.

%prep
%setup -q -c -T -n opencode-desktop-%{version}
%ifarch x86_64
ar -x %{SOURCE0}
%elifarch aarch64
ar -x %{SOURCE1}
%endif
tar -xf data.tar.xz

%build
# Pre-compiled binary release; no compilation needed

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/opt/OpenCode
cp -a opt/OpenCode/. %{buildroot}/opt/OpenCode/

# Ensure proper executable and sandbox permissions
chmod 755 %{buildroot}/opt/OpenCode/ai.opencode
chmod 4755 %{buildroot}/opt/OpenCode/chrome-sandbox 2>/dev/null || true

# Symlink to /usr/bin/opencode-desktop
mkdir -p %{buildroot}%{_bindir}
ln -sf ../../opt/OpenCode/ai.opencode %{buildroot}%{_bindir}/opencode-desktop

# Desktop entries, metainfo, and icons
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 usr/share/applications/ai.opencode.desktop.desktop %{buildroot}%{_datadir}/applications/ai.opencode.desktop.desktop
install -m 644 usr/share/applications/opencode-desktop.desktop %{buildroot}%{_datadir}/applications/opencode-desktop.desktop

mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 usr/share/metainfo/ai.opencode.desktop.metainfo.xml %{buildroot}%{_datadir}/metainfo/ai.opencode.desktop.metainfo.xml

mkdir -p %{buildroot}%{_datadir}/icons
cp -a usr/share/icons/. %{buildroot}%{_datadir}/icons/

%check
test -x %{buildroot}/opt/OpenCode/ai.opencode
test -L %{buildroot}%{_bindir}/opencode-desktop

%files
%{_bindir}/opencode-desktop
/opt/OpenCode
%{_datadir}/applications/ai.opencode.desktop.desktop
%{_datadir}/applications/opencode-desktop.desktop
%{_datadir}/metainfo/ai.opencode.desktop.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/ai.opencode.png

%changelog
* Thu Nov 26 2026 Azhar Momin <azhar-momin@outlook.com> - 2.4.2-1
- Upstream release update to 2.4.2

* Mon Nov 23 2026 Azhar Momin <azhar-momin@outlook.com> - 2.4.1-1
- Upstream release update to 2.4.1

* Mon Nov 23 2026 Azhar Momin <azhar-momin@outlook.com> - 2.4.0-1
- Upstream release update to 2.4.0

* Sun Nov 22 2026 Azhar Momin <azhar-momin@outlook.com> - 2.3.2-1
- Initial Fedora RPM packaging for OpenCode Desktop 2.3.2
- Graphical desktop interface for OpenCode with x86_64 and aarch64 support
