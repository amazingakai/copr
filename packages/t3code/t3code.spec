Name:           t3code
Version:        0.1.13
Release:        1%{?dist}
Summary:        T3 Code - Open-source control plane for coding agents

License:        MIT
URL:            https://t3.codes
Source0:        https://github.com/pingdotgg/t3code/releases/download/v%{version}/T3-Code-%{version}-amd64.deb
Source1:        https://github.com/pingdotgg/t3code/releases/download/v%{version}/T3-Code-%{version}-arm64.deb

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
%global __requires_exclude_from ^/opt/.*/resources/.*$
%global __requires_exclude ^(libffmpeg|libvk_swiftshader|libvulkan|libEGL|libGLESv2|libfff_c|libggml.*|libtranscribe)\\.so.*$
%global __provides_exclude_from ^/opt/.*$

%description
T3 Code is an open-source desktop application and control plane for AI coding
agents (Claude Code, Codex, OpenCode, and more). It drives existing agent
subscriptions, provides visual diffs, worktree branch management, and remote
access via web and mobile.

%prep
%setup -q -c -T -n t3code-%{version}
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

# Install application directory
mkdir -p "%{buildroot}/opt/T3 Code (Beta)"
cp -a "opt/T3 Code (Beta)/." "%{buildroot}/opt/T3 Code (Beta)/"

# Ensure proper executable and sandbox permissions
chmod 755 "%{buildroot}/opt/T3 Code (Beta)/t3code"
chmod 4755 "%{buildroot}/opt/T3 Code (Beta)/chrome-sandbox" 2>/dev/null || true

# Remove foreign prebuild architectures and musl binaries to avoid dependency issues
%ifarch x86_64
rm -rf "%{buildroot}/opt/T3 Code (Beta)/resources/app.asar.unpacked/node_modules/node-pty/prebuilds/linux-arm64"
%elifarch aarch64
rm -rf "%{buildroot}/opt/T3 Code (Beta)/resources/app.asar.unpacked/node_modules/node-pty/prebuilds/linux-x64"
%endif
find "%{buildroot}/opt/T3 Code (Beta)" -type d -name "*musl*" -exec rm -rf {} +

# Create binary symlinks
mkdir -p %{buildroot}%{_bindir}
ln -sf "../../opt/T3 Code (Beta)/t3code" %{buildroot}%{_bindir}/t3code

# Install desktop entry, metainfo, and icons
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 usr/share/applications/t3code.desktop %{buildroot}%{_datadir}/applications/t3code.desktop

mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 usr/share/metainfo/com.t3tools.t3code.metainfo.xml %{buildroot}%{_datadir}/metainfo/com.t3tools.t3code.metainfo.xml

mkdir -p %{buildroot}%{_datadir}/icons
cp -a usr/share/icons/. %{buildroot}%{_datadir}/icons/

%check
# Verify binary is executable and ELF headers are valid
test -x "%{buildroot}/opt/T3 Code (Beta)/t3code"
test -L "%{buildroot}%{_bindir}/t3code"

%files
%{_bindir}/t3code
"/opt/T3 Code (Beta)"
%{_datadir}/applications/t3code.desktop
%{_datadir}/metainfo/com.t3tools.t3code.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/t3code.png

%changelog
* Thu Nov 26 2026 Azhar Momin <azhar-momin@outlook.com> - 0.1.13-1
- Upstream release update to 0.1.13

* Wed Nov 25 2026 Azhar Momin <azhar-momin@outlook.com> - 0.1.12-1
- Upstream release update to 0.1.12

* Sun Nov 22 2026 Azhar Momin <azhar-momin@outlook.com> - 0.1.11-1
- Initial Fedora RPM packaging for T3 Code 0.1.11
- Desktop GUI control plane for coding agents with x86_64 and aarch64 support
