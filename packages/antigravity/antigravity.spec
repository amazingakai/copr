Name:           antigravity
Version:        2.29.0
%global build_id 5723181030440960
Release:        2%{?dist}
Summary:        Google Antigravity Desktop Client

License:        LicenseRef-Google-Antigravity
URL:            https://antigravity.google
Source0:        https://storage.googleapis.com/antigravity-public/antigravity-hub/%{version}-%{build_id}/linux-x64/Antigravity.tar.gz#/Antigravity-x64-%{version}.tar.gz
Source1:        https://storage.googleapis.com/antigravity-public/antigravity-hub/%{version}-%{build_id}/linux-arm/Antigravity.tar.gz#/Antigravity-arm64-%{version}.tar.gz
Source2:        antigravity.sh
Source3:        antigravity.desktop
Source4:        patch-kdecoration.py
Source5:        antigravity.appdata.xml

ExclusiveArch:  x86_64 aarch64

BuildRequires:  python3
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       libsecret
Requires:       xdg-utils

# Disable debuginfo package generation and stripping for pre-built Electron binaries
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

# Filter private bundled shared libraries and bundled node script shebangs
%global __requires_exclude ^(libffmpeg|libvk_swiftshader|libvulkan|libEGL|libGLESv2)\\.so.*$|^/usr/bin/(node|perl)$
%global __provides_exclude_from ^/opt/antigravity/.*$

%description
Google Antigravity is an AI-first development platform and command center.
This package provides the desktop client with patches for native KDE Plasma 6
window decorations and Wayland support.

%prep
%setup -q -c -T -n antigravity-%{version}
%ifarch x86_64
tar -xzf %{SOURCE0} --strip-components=1
%elifarch aarch64
tar -xzf %{SOURCE1} --strip-components=1
%endif

# Patch app.asar to fix titleBarOverlay collision in KDE Plasma 6
python3 %{SOURCE4} resources/app.asar

# Remove in-app updater configuration so DNF manages application lifecycle
rm -f resources/app-update.yml

%build
# Pre-compiled binary release; no compilation needed

%install
rm -rf %{buildroot}

# Install application to /opt/antigravity
mkdir -p %{buildroot}/opt/antigravity
cp -a . %{buildroot}/opt/antigravity/

# Ensure executable and sandbox permissions
chmod 755 %{buildroot}/opt/antigravity/antigravity
chmod 4755 %{buildroot}/opt/antigravity/chrome-sandbox 2>/dev/null || true

# Install launcher wrapper
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{SOURCE2} %{buildroot}%{_bindir}/antigravity

# Install desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE3}

# Install AppStream metadata
mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 %{SOURCE5} %{buildroot}%{_datadir}/metainfo/antigravity.appdata.xml

# Extract high-resolution application icon from app.asar
mkdir -p %{buildroot}%{_datadir}/pixmaps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
python3 -c '
import struct, json
with open("resources/app.asar", "rb") as f:
    _, total_size, _, json_size = struct.unpack("<IIII", f.read(16))
    tree = json.loads(f.read(json_size).decode("utf-8"))
    icon_info = tree["files"]["icon.png"]
    f.seek(8 + total_size + int(icon_info["offset"]))
    icon_data = f.read(int(icon_info["size"]))
with open("%{buildroot}%{_datadir}/pixmaps/antigravity.png", "wb") as out:
    out.write(icon_data)
with open("%{buildroot}%{_datadir}/icons/hicolor/512x512/apps/antigravity.png", "wb") as out:
    out.write(icon_data)
'

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/antigravity.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/antigravity.appdata.xml

%files
/opt/antigravity
%{_bindir}/antigravity
%{_datadir}/applications/antigravity.desktop
%{_datadir}/metainfo/antigravity.appdata.xml
%{_datadir}/pixmaps/antigravity.png
%{_datadir}/icons/hicolor/512x512/apps/antigravity.png

%changelog
* Sat Nov 07 2026 Azhar Momin <azhar-momin@outlook.com> - 2.29.0-2
- Add support for aarch64 (ARM64) architecture

* Sat Nov 07 2026 Azhar Momin <azhar-momin@outlook.com> - 2.29.0-1
- Initial Fedora RPM packaging for Antigravity Desktop 2.29.0
- Add in-place patch for KDE Plasma 6 left-hand window button decoration fix
- Disable in-app auto-updater in favor of DNF repository management
- Add AppStream metadata, desktop integration, and high-resolution icons
