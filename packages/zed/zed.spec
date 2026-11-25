Name:           zed
Version:        1.30.2
Release:        1%{?dist}
Summary:        High-performance, multiplayer code editor

License:        GPL-3.0-or-later AND AGPL-3.0-or-later AND Apache-2.0
URL:            https://zed.dev
Source0:        https://github.com/zed-industries/zed/releases/download/v%{version}/zed-linux-x86_64.tar.gz
Source1:        https://github.com/zed-industries/zed/releases/download/v%{version}/zed-linux-aarch64.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

# Non-ELF runtime dependencies (ELF shared libraries are automatically detected by RPM)
# Zed's GPUI renderer dynamically loads libvulkan.so.1 via dlopen at runtime
Requires:       vulkan-loader

# Disable debuginfo package generation and stripping
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

# Filter private bundled libraries from provides and requires
%global __provides_exclude_from ^/usr/lib/zed/.*$
%global __requires_exclude_from ^/usr/lib/zed/lib/.*$

%description
Zed is a high-performance, multiplayer code editor from the creators of Atom
and Tree-sitter. It is engineered from the ground up to be blazingly fast,
written in Rust, and powered by GPUI for immediate responsiveness.

%prep
%setup -q -c -T -n zed-%{version}
%ifarch x86_64
tar -xzf %{SOURCE0} --strip-components=1
%elifarch aarch64
tar -xzf %{SOURCE1} --strip-components=1
%endif

%build
# Pre-compiled native release; no compilation needed

%install
rm -rf %{buildroot}

# Install application bundle into /usr/lib/zed
mkdir -p %{buildroot}%{_prefix}/lib/zed
cp -a bin libexec lib %{buildroot}%{_prefix}/lib/zed/
chmod 755 %{buildroot}%{_prefix}/lib/zed/bin/zed
chmod 755 %{buildroot}%{_prefix}/lib/zed/libexec/zed-editor

# Create binary symlink in /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -sf ../lib/zed/bin/zed %{buildroot}%{_bindir}/zed

# Install desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 share/applications/dev.zed.Zed.desktop %{buildroot}%{_datadir}/applications/dev.zed.Zed.desktop

# Install icons
mkdir -p %{buildroot}%{_datadir}/icons
cp -a share/icons/. %{buildroot}%{_datadir}/icons/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/dev.zed.Zed.desktop
test -x %{buildroot}%{_prefix}/lib/zed/bin/zed
test -x %{buildroot}%{_prefix}/lib/zed/libexec/zed-editor
test -L %{buildroot}%{_bindir}/zed

%files
%{_bindir}/zed
%{_prefix}/lib/zed/
%{_datadir}/applications/dev.zed.Zed.desktop
%{_datadir}/icons/hicolor/*/apps/zed.png

%changelog
* Wed Nov 25 2026 Azhar Momin <azhar-momin@outlook.com> - 1.30.2-1
- Upstream release update to 1.30.2

* Tue Nov 24 2026 Azhar Momin <azhar-momin@outlook.com> - 1.29.3-1
- Initial Fedora RPM packaging for Zed 1.29.3
- Standalone native binary with x86_64 and aarch64 support
