Name:           antigravity-cli
Version:        1.5.4
Release:        1%{?dist}
Summary:        Command-line interface for Google Antigravity

License:        LicenseRef-Google-Antigravity
URL:            https://antigravity.google
Source0:        https://github.com/google-antigravity/antigravity-cli/releases/download/%{version}/agy_cli_linux_x64.tar.gz
Source1:        https://github.com/google-antigravity/antigravity-cli/releases/download/%{version}/agy_cli_linux_arm64.tar.gz
Source2:        agy.sh

ExclusiveArch:  x86_64 aarch64

Provides:       agy = %{version}-%{release}

%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

%description
The Antigravity CLI (agy) is a lightweight, terminal-based interface for fast
agent interaction, running slash commands, headless prompts, and background tasks.

%prep
%setup -q -c -T -n antigravity-cli-%{version}
%ifarch x86_64
tar -xzf %{SOURCE0}
%elifarch aarch64
tar -xzf %{SOURCE1}
%endif

%build
# Pre-compiled standalone binary

%install
rm -rf %{buildroot}

# Install the actual binary to /usr/libexec/antigravity-cli/agy
mkdir -p %{buildroot}%{_libexecdir}/antigravity-cli
if [ -f "antigravity" ]; then
    install -m 755 antigravity %{buildroot}%{_libexecdir}/antigravity-cli/agy
elif [ -f "agy" ]; then
    install -m 755 agy %{buildroot}%{_libexecdir}/antigravity-cli/agy
elif [ -f "antigravity-cli" ]; then
    install -m 755 antigravity-cli %{buildroot}%{_libexecdir}/antigravity-cli/agy
fi

# Install the launcher wrapper to /usr/bin/agy (disables self-updater)
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{SOURCE2} %{buildroot}%{_bindir}/agy

# Create convenient alias symlink
ln -sf agy %{buildroot}%{_bindir}/antigravity-cli

%check
%{buildroot}%{_bindir}/agy --help >/dev/null 2>&1 || true

%files
%{_bindir}/agy
%{_bindir}/antigravity-cli
%{_libexecdir}/antigravity-cli/agy

%changelog
* Tue Nov 10 2026 Azhar Momin <azhar-momin@outlook.com> - 1.5.4-1
- Upstream release update to 1.5.4

* Sat Nov 07 2026 Azhar Momin <azhar-momin@outlook.com> - 1.5.3-2
- Add support for aarch64 (ARM64) architecture

* Sat Nov 07 2026 Azhar Momin <azhar-momin@outlook.com> - 1.5.3-1
- Initial Fedora RPM packaging for Antigravity CLI (agy) 1.5.3
- Disable internal self-updater in favor of DNF repository management
