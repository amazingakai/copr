Name:           delta
Version:        0.28.4
Release:        1%{?dist}
Summary:        AI-native collaborative code editor by Zed Industries

License:        Proprietary
URL:            https://delta.dev
Source0:        https://releases.delta.dev/releases/stable/%{version}/delta-linux-x86_64.tar.gz
Source1:        https://releases.delta.dev/releases/stable/%{version}/delta-linux-aarch64.tar.gz

ExclusiveArch:  x86_64 aarch64

# git-delta in Fedora official repos provides an unrelated /usr/bin/delta git pager
Conflicts:      git-delta

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# Non-ELF runtime dependencies (ELF shared libraries are automatically detected by RPM)
# Delta's GPUI renderer dynamically loads libvulkan.so.1 via dlopen at runtime
# Delta invokes xdg-open to open browser URLs and web authentications
Requires:       vulkan-loader
Requires:       xdg-utils

# Disable debuginfo package generation and stripping
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

# Filter private bundled libraries from provides and requires
%global __provides_exclude_from ^/usr/lib/delta/.*$
%global __requires_exclude_from ^/usr/lib/delta/lib/.*$

%description
Delta is an AI-native collaborative code editor built by Zed Industries.
It combines Zed's high-performance GPUI engine with deep multiplayer workspaces
and integrated autonomous AI coding agents.

%prep
%setup -q -c -T -n delta-%{version}
%ifarch x86_64
tar -xzf %{SOURCE0} --strip-components=1
%elifarch aarch64
tar -xzf %{SOURCE1} --strip-components=1
%endif

%build
# Pre-compiled native release; no compilation needed

%install
rm -rf %{buildroot}

# Install application bundle into /usr/lib/delta
mkdir -p %{buildroot}%{_prefix}/lib/delta
cp -a bin lib %{buildroot}%{_prefix}/lib/delta/
chmod 755 %{buildroot}%{_prefix}/lib/delta/bin/delta
chmod 755 %{buildroot}%{_prefix}/lib/delta/bin/delta-app

# Create binary symlinks in /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -sf ../lib/delta/bin/delta %{buildroot}%{_bindir}/delta
ln -sf ../lib/delta/bin/delta-app %{buildroot}%{_bindir}/delta-app

# Install desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 share/applications/dev.zed.Delta.desktop %{buildroot}%{_datadir}/applications/dev.zed.Delta.desktop

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons
cp -a share/icons/. %{buildroot}%{_datadir}/icons/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/dev.zed.Delta.desktop
test -x %{buildroot}%{_prefix}/lib/delta/bin/delta
test -x %{buildroot}%{_prefix}/lib/delta/bin/delta-app
test -L %{buildroot}%{_bindir}/delta
test -L %{buildroot}%{_bindir}/delta-app

%files
%{_bindir}/delta
%{_bindir}/delta-app
%{_prefix}/lib/delta/
%{_datadir}/applications/dev.zed.Delta.desktop
%{_datadir}/icons/hicolor/*/apps/dev.zed.Delta.png

%changelog
* Tue Nov 24 2026 Azhar Momin <azhar-momin@outlook.com> - 0.28.4-1
- Initial Fedora RPM packaging for Delta 0.28.4
- Standalone native binary with x86_64 and aarch64 support
