Name:           git-desktop
Version:        0.16.0
Release:        1%{?dist}
Summary:        AI-native, keyboard-first desktop Git client

License:        Apache-2.0
URL:            https://gitdesktop.app
Source0:        https://github.com/theBGuy/GitDesktop/releases/download/v%{version}/GitDesktop-%{version}-1.x86_64.rpm

ExclusiveArch:  x86_64

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# Non-ELF runtime dependencies (ELF shared libraries are automatically detected by RPM)
# 1. Git operations CLI
Requires:       git-core
# 2. System tray indicator loaded via dlopen at runtime (mandatory for startup)
Requires:       libayatana-appindicator-gtk3

# Provide alternative unhyphenated name
Provides:       gitdesktop = %{version}-%{release}

# Disable debuginfo package generation and stripping
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

%description
GitDesktop is an AI-native, keyboard-first Git desktop client combining
GitHub Desktop's ease of use with advanced Git, PR, issue, and discussion
management. Built with Tauri and Rust.

%prep
%setup -q -c -T -n %{name}-%{version}
rpm2cpio %{SOURCE0} | cpio -idmv

%build
# Pre-compiled native release; no compilation needed

%install
rm -rf %{buildroot}

# Install binary
mkdir -p %{buildroot}%{_bindir}
install -m 755 usr/bin/gitdesktop %{buildroot}%{_bindir}/gitdesktop

# Install desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 usr/share/applications/GitDesktop.desktop %{buildroot}%{_datadir}/applications/GitDesktop.desktop

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons
cp -a usr/share/icons/. %{buildroot}%{_datadir}/icons/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/GitDesktop.desktop
test -x %{buildroot}%{_bindir}/gitdesktop

%files
%{_bindir}/gitdesktop
%{_datadir}/applications/GitDesktop.desktop
%{_datadir}/icons/hicolor/*/apps/gitdesktop.png

%changelog
* Tue Nov 24 2026 Azhar Momin <azhar-momin@outlook.com> - 0.16.0-1
- Initial Fedora RPM packaging for GitDesktop 0.16.0
- Native x86_64 build with git-core and libayatana-appindicator-gtk3 dependencies
