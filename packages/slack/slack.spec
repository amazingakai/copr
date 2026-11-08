Name:           slack
Version:        4.53.276
Release:        1%{?dist}
Summary:        Slack Desktop Client for Linux

License:        Proprietary
URL:            https://slack.com
Source0:        https://downloads.slack-edge.com/desktop-releases/linux/x64/%{version}/slack-%{version}-0.1.el8.x86_64.rpm

ExclusiveArch:  x86_64

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
%global __provides_exclude_from ^/usr/lib/slack/.*$

%description
Slack is a new way to communicate with your team. It is faster, better organized,
and more secure than email.
This package repackages the official Slack RPM for Fedora.

%prep
%setup -q -c -T -n slack-%{version}
rpm2cpio %{SOURCE0} | cpio -idmv

# Fix upstream AppStream metadata specification compliance in-place
sed -i 's|www.slack.com|https://slack.com|g' usr/share/metainfo/slack.metainfo.xml
sed -i '/<component/a \ \ \ \ <metadata_license>CC0-1.0</metadata_license>' usr/share/metainfo/slack.metainfo.xml

%build
# Pre-compiled binary release; no compilation needed

%install
rm -rf %{buildroot}

# Install application directory
mkdir -p %{buildroot}/usr/lib/slack
cp -a usr/lib/slack/. %{buildroot}/usr/lib/slack/

# Set executable and chrome-sandbox permissions
chmod 755 %{buildroot}/usr/lib/slack/slack
chmod 4755 %{buildroot}/usr/lib/slack/chrome-sandbox 2>/dev/null || true

# Create binary symlink in /usr/bin
mkdir -p %{buildroot}%{_bindir}
ln -sf ../lib/slack/slack %{buildroot}%{_bindir}/slack

# Install desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications usr/share/applications/slack.desktop

# Install validated AppStream metadata
mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 usr/share/metainfo/slack.metainfo.xml %{buildroot}%{_datadir}/metainfo/slack.metainfo.xml

# Install icons
mkdir -p %{buildroot}%{_datadir}/pixmaps
install -m 644 usr/share/pixmaps/slack.png %{buildroot}%{_datadir}/pixmaps/slack.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
install -m 644 usr/share/pixmaps/slack.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/slack.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/slack.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/slack.metainfo.xml

%files
%license usr/lib/slack/LICENSE usr/lib/slack/LICENSES-linux.json
%{_bindir}/slack
/usr/lib/slack/
%{_datadir}/applications/slack.desktop
%{_datadir}/metainfo/slack.metainfo.xml
%{_datadir}/pixmaps/slack.png
%{_datadir}/icons/hicolor/512x512/apps/slack.png

%changelog
* Sun Nov 08 2026 Azhar Momin <azhar-momin@outlook.com> - 4.53.276-1
- Initial Fedora RPM packaging for Slack 4.53.276
- Repackage official Linux x86_64 RPM
- Fix AppStream metadata specification compliance
