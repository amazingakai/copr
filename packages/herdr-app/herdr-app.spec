Name:           herdr-app
Version:        0.1.18
%global core_version 0.1.22
Release:        1%{?dist}
Summary:        Desktop workspace manager for AI coding agents

License:        Apache-2.0
URL:            https://herdr.dev
Source0:        https://releases.herdr.dev/app/%{version}/herdr-app-linux-x86_64.tar.gz
Source1:        https://releases.herdr.dev/app/%{version}/herdr-app-linux-aarch64.tar.gz
Source2:        https://releases.herdr.dev/core/%{core_version}/herdr-core-linux-x86_64.tar.gz
Source3:        https://releases.herdr.dev/core/%{core_version}/herdr-core-linux-aarch64.tar.gz
Source4:        herdr-app.desktop

ExclusiveArch:  x86_64 aarch64

BuildRequires:  desktop-file-utils
BuildRequires:  tar

# Herdr uses GPUI for GPU/Vulkan-accelerated desktop rendering
Requires:       vulkan-loader

# Disable debuginfo package generation and stripping
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

%description
Herdr is a native desktop workspace manager and runtime environment built
specifically for running and managing AI coding agents (Claude Code, Codex,
Cursor, OpenCode, and others). It provides visual workspaces, tabs, split
panes, agent state awareness, and persistent background sessions powered by
herdr-core (hc).

%prep
%setup -q -c -T -n herdr-app-%{version}
%ifarch x86_64
tar -xzf %{SOURCE0} --strip-components=1
tar -xzf %{SOURCE2} herdr-core
%elifarch aarch64
tar -xzf %{SOURCE1} --strip-components=1
tar -xzf %{SOURCE3} herdr-core
%endif

%build
# Pre-compiled native binaries; no compilation needed

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir}
install -m 755 herdr-app %{buildroot}%{_bindir}/herdr-app
install -m 755 herdr-core %{buildroot}%{_bindir}/herdr-core
ln -sf herdr-core %{buildroot}%{_bindir}/hc

# Desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE4}

# Icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m 644 herdr-app.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/herdr-app.svg

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/herdr-app.desktop
test -x %{buildroot}%{_bindir}/herdr-app
test -x %{buildroot}%{_bindir}/herdr-core
test -L %{buildroot}%{_bindir}/hc
%{buildroot}%{_bindir}/herdr-app --version
%{buildroot}%{_bindir}/herdr-core --version

%files
%license LICENSE THIRD-PARTY-NOTICES
%{_bindir}/herdr-app
%{_bindir}/herdr-core
%{_bindir}/hc
%{_datadir}/applications/herdr-app.desktop
%{_datadir}/icons/hicolor/scalable/apps/herdr-app.svg

%changelog
* Sat Nov 28 2026 Azhar Momin <azhar-momin@outlook.com> - 0.1.18-1
- Initial Fedora RPM packaging for Herdr Desktop App 0.1.18
- Native GPUI-accelerated desktop workspace interface
- Includes companion herdr-core (hc) 0.1.22 runtime
- Standalone binaries with x86_64 and aarch64 support
