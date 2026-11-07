Name:           antigravity-ide
Version:        2.6.0
%global build_id 5526304964083712
Release:        1%{?dist}
Summary:        Google Antigravity Standalone IDE

License:        LicenseRef-Google-Antigravity
URL:            https://antigravity.google
Source0:        https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/%{version}-%{build_id}/linux-x64/Antigravity%%20IDE.tar.gz#/Antigravity-IDE-%{version}.tar.gz
Source1:        antigravity-ide.sh
Source2:        antigravity-ide.desktop
Source3:        antigravity-ide.appdata.xml

ExclusiveArch:  x86_64

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  python3

Requires:       libcurl
Requires:       libsecret
Requires:       xdg-utils

%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

# Filter private bundled shared libraries, Ubuntu/Debian symbol versions, and bundled script shebangs
%global __requires_exclude ^(libffmpeg|libvk_swiftshader|libvulkan|libEGL|libGLESv2|libmsalruntime)\\.so.*$|^libcurl\\.so\\.4\\(CURL_OPENSSL_4\\)|^/usr/bin/(node|perl)$
%global __provides_exclude_from ^/opt/antigravity-ide/.*$

%description
Google Antigravity IDE is an AI-first integrated development environment built
on VS Code that integrates agentic workflows, autocomplete, and code synthesis
directly into your coding environment.

%prep
%setup -q -c -T -n antigravity-ide-%{version}
tar -xzf %{SOURCE0} --strip-components=1

%build
# Pre-compiled binary release; no compilation needed

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/opt/antigravity-ide
cp -a . %{buildroot}/opt/antigravity-ide/

# Disable built-in auto-updater in product.json so updates are handled via DNF
python3 -c '
import json
path = "%{buildroot}/opt/antigravity-ide/resources/app/product.json"
with open(path, "r") as f:
    data = json.load(f)
data["updateUrl"] = ""
with open(path, "w") as f:
    json.dump(data, f, indent=2)
'

# Set proper executable and sandbox permissions
chmod 755 %{buildroot}/opt/antigravity-ide/antigravity-ide
chmod 755 %{buildroot}/opt/antigravity-ide/bin/antigravity-ide
chmod 4755 %{buildroot}/opt/antigravity-ide/chrome-sandbox 2>/dev/null || true

# Install launcher wrapper
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{SOURCE1} %{buildroot}%{_bindir}/antigravity-ide

# Install desktop entry
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE2}

# Install AppStream metadata
mkdir -p %{buildroot}%{_datadir}/metainfo
install -m 644 %{SOURCE3} %{buildroot}%{_datadir}/metainfo/antigravity-ide.appdata.xml

# Install application icons
mkdir -p %{buildroot}%{_datadir}/pixmaps
cp -a resources/app/resources/linux/code.png %{buildroot}%{_datadir}/pixmaps/antigravity-ide.png

mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
cp -a resources/app/resources/linux/code.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/antigravity-ide.png

# Install shell completions
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
install -m 644 resources/completions/bash/antigravity-ide %{buildroot}%{_datadir}/bash-completion/completions/antigravity-ide

mkdir -p %{buildroot}%{_datadir}/zsh/site-functions
install -m 644 resources/completions/zsh/_antigravity-ide %{buildroot}%{_datadir}/zsh/site-functions/_antigravity-ide

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/antigravity-ide.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/antigravity-ide.appdata.xml

%files
/opt/antigravity-ide
%{_bindir}/antigravity-ide
%{_datadir}/applications/antigravity-ide.desktop
%{_datadir}/metainfo/antigravity-ide.appdata.xml
%{_datadir}/pixmaps/antigravity-ide.png
%{_datadir}/icons/hicolor/512x512/apps/antigravity-ide.png
%{_datadir}/bash-completion/completions/antigravity-ide
%{_datadir}/zsh/site-functions/_antigravity-ide

%changelog
* Sat Nov 07 2026 Azhar Momin <azhar-momin@outlook.com> - 2.6.0-1
- Initial Fedora RPM packaging for Antigravity IDE 2.6.0
- Disable in-app auto-updater via product.json in favor of DNF repository management
- Add AppStream metadata, desktop integration, icons, and shell completions
