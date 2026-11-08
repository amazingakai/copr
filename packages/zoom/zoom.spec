Name:           zoom
Version:        7.2.5.6661
Release:        1%{?dist}
Summary:        Zoom Workplace Video Conferencing

License:        Proprietary
URL:            https://zoom.us
Source0:        https://cdn.zoom.us/prod/%{version}/zoom_x86_64.rpm
Source1:        zoom.metainfo.xml

ExclusiveArch:  x86_64

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       xdg-utils

# Disable debuginfo package generation and stripping for pre-built binaries
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

# Disable RPM QA rpath check for proprietary binaries with vendor runpaths
%global __brp_check_rpaths %{nil}

# Filter private bundled libraries from provides and requires
%global __provides_exclude_from ^/opt/zoom/.*$
%global __requires_exclude_from ^/opt/zoom/.*$

%description
Zoom Workplace is an AI-first collaboration platform that combines video
meetings, team chat, phone, whiteboard, and docs into one platform.
This package repackages the official Zoom RPM for Fedora with clean desktop
and protocol integration.

%prep
%setup -q -c -T -n zoom-%{version}
rpm2cpio %{SOURCE0} | cpio -idmv

# Clean up deprecated keys from upstream desktop entry
desktop-file-edit --remove-key=Encoding usr/share/applications/Zoom.desktop
desktop-file-edit --remove-category=Application usr/share/applications/Zoom.desktop

%build
# Pre-compiled binary release; no compilation needed

%install
rm -rf %{buildroot}

# Install application directory
mkdir -p %{buildroot}/opt/zoom
cp -a opt/zoom/. %{buildroot}/opt/zoom/

# Ensure executable and chrome-sandbox permissions
chmod 755 %{buildroot}/opt/zoom/ZoomLauncher %{buildroot}/opt/zoom/zoom
chmod 4755 %{buildroot}/opt/zoom/cef/chrome-sandbox 2>/dev/null || true

# Create binary symlink in /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -sf ../../opt/zoom/ZoomLauncher %{buildroot}%{_bindir}/zoom

# Install desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications usr/share/applications/Zoom.desktop

# Install AppStream metadata
mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/metainfo/zoom.metainfo.xml

# Install icons
mkdir -p %{buildroot}%{_datadir}/pixmaps
install -m 644 usr/share/pixmaps/Zoom.png %{buildroot}%{_datadir}/pixmaps/Zoom.png
install -m 644 usr/share/pixmaps/application-x-zoom.png %{buildroot}%{_datadir}/pixmaps/application-x-zoom.png

mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
install -m 644 usr/share/pixmaps/Zoom.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/Zoom.png

# Install MIME type definition
mkdir -p %{buildroot}%{_datadir}/mime/packages
install -m 644 usr/share/mime/packages/zoom.xml %{buildroot}%{_datadir}/mime/packages/zoom.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/Zoom.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/zoom.metainfo.xml

%files
/opt/zoom/
%{_bindir}/zoom
%{_datadir}/applications/Zoom.desktop
%{_datadir}/metainfo/zoom.metainfo.xml
%{_datadir}/mime/packages/zoom.xml
%{_datadir}/pixmaps/Zoom.png
%{_datadir}/pixmaps/application-x-zoom.png
%{_datadir}/icons/hicolor/256x256/apps/Zoom.png

%changelog
* Sun Nov 08 2026 Azhar Momin <azhar-momin@outlook.com> - 7.2.5.6661-1
- Initial Fedora RPM packaging for Zoom 7.2.5.6661
- Repackage official Linux x86_64 RPM
- Fix desktop entry specification compliance and drop vendor scriptlet warnings
- Add AppStream metainfo metadata for software center discovery
