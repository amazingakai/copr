Name:           starship
Version:        1.27.0
Release:        1%{?dist}
Summary:        The cross-shell prompt for astronauts

License:        ISC
URL:            https://starship.rs
Source0:        https://github.com/starship/starship/releases/download/v%{version}/starship-x86_64-unknown-linux-musl.tar.gz
Source1:        https://github.com/starship/starship/releases/download/v%{version}/starship-aarch64-unknown-linux-musl.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  tar

# Disable debuginfo package generation and stripping
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

%description
Starship is the minimal, blazing-fast, and infinitely customizable prompt
for any shell! It supports Bash, Fish, Zsh, PowerShell, and more.

%prep
%setup -q -c -T -n starship-%{version}
%ifarch x86_64
tar -xzf %{SOURCE0}
%elifarch aarch64
tar -xzf %{SOURCE1}
%endif

%build
# Pre-compiled standalone native binary; no compilation needed

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir}
install -m 755 starship %{buildroot}%{_bindir}/starship

# Generate shell completions
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
mkdir -p %{buildroot}%{_datadir}/zsh/site-functions
mkdir -p %{buildroot}%{_datadir}/fish/vendor_completions.d

%{buildroot}%{_bindir}/starship completions bash > %{buildroot}%{_datadir}/bash-completion/completions/starship
%{buildroot}%{_bindir}/starship completions zsh > %{buildroot}%{_datadir}/zsh/site-functions/_starship
%{buildroot}%{_bindir}/starship completions fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/starship.fish

%check
test -x %{buildroot}%{_bindir}/starship
%{buildroot}%{_bindir}/starship --version

%files
%{_bindir}/starship
%{_datadir}/bash-completion/completions/starship
%{_datadir}/zsh/site-functions/_starship
%{_datadir}/fish/vendor_completions.d/starship.fish

%changelog
* Sat Nov 28 2026 Azhar Momin <azhar-momin@outlook.com> - 1.27.0-1
- Initial Fedora RPM packaging for Starship 1.27.0
- Fast, customizable cross-shell prompt with x86_64 and aarch64 support
- Includes bash, zsh, and fish shell completions
