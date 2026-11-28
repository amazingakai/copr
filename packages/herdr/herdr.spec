Name:           herdr
Version:        0.9.5
Release:        1%{?dist}
Summary:        Terminal workspace manager for AI coding agents

License:        Apache-2.0
URL:            https://herdr.dev
Source0:        https://github.com/herdrdev/herdr/releases/download/v%{version}/herdr-linux-x86_64
Source1:        https://github.com/herdrdev/herdr/releases/download/v%{version}/herdr-linux-aarch64

ExclusiveArch:  x86_64 aarch64

# Disable debuginfo package generation and stripping
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

%description
Herdr is a terminal workspace manager and runtime environment built
specifically for running and managing AI coding agents (Claude Code,
Codex, Cursor, OpenCode, and others). It provides persistent background
sessions, agent status awareness, multi-machine remote management, and
an agent-native socket API.

%prep
# Nothing to unpack; raw pre-compiled binary source

%build
# Pre-compiled standalone native binary; no compilation needed

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir}
%ifarch x86_64
install -m 755 %{SOURCE0} %{buildroot}%{_bindir}/herdr
%elifarch aarch64
install -m 755 %{SOURCE1} %{buildroot}%{_bindir}/herdr
%endif

# Generate shell completions
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
mkdir -p %{buildroot}%{_datadir}/zsh/site-functions
mkdir -p %{buildroot}%{_datadir}/fish/vendor_completions.d

%{buildroot}%{_bindir}/herdr completion bash > %{buildroot}%{_datadir}/bash-completion/completions/herdr
%{buildroot}%{_bindir}/herdr completion zsh > %{buildroot}%{_datadir}/zsh/site-functions/_herdr
%{buildroot}%{_bindir}/herdr completion fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/herdr.fish

%check
test -x %{buildroot}%{_bindir}/herdr
%{buildroot}%{_bindir}/herdr --version

%files
%{_bindir}/herdr
%{_datadir}/bash-completion/completions/herdr
%{_datadir}/zsh/site-functions/_herdr
%{_datadir}/fish/vendor_completions.d/herdr.fish

%changelog
* Sat Nov 28 2026 Azhar Momin <azhar-momin@outlook.com> - 0.9.5-1
- Initial Fedora RPM packaging for Herdr 0.9.5
- Standalone static binary with x86_64 and aarch64 support
- Include bash, zsh, and fish shell completions
