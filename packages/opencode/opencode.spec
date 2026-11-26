Name:           opencode
Version:        2.4.2
Release:        1%{?dist}
Summary:        OpenCode - Open-source AI coding agent for your terminal

License:        MIT
URL:            https://opencode.ai
Source0:        https://github.com/anomalyco/opencode/releases/download/v%{version}/opencode-linux-x64.tar.gz
Source1:        https://github.com/anomalyco/opencode/releases/download/v%{version}/opencode-linux-arm64.tar.gz

ExclusiveArch:  x86_64 aarch64

%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

%description
OpenCode is an open-source autonomous AI coding agent for the terminal. It
features dual agent modes (plan and build), supports hundreds of LLM providers,
and automates code generation, debugging, refactoring, and git workflows.

%prep
%setup -q -c -T -n opencode-%{version}
%ifarch x86_64
tar -xzf %{SOURCE0}
%elifarch aarch64
tar -xzf %{SOURCE1}
%endif
chmod 755 opencode

%build
# Pre-compiled standalone binary

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
install -m 755 opencode %{buildroot}%{_bindir}/opencode

# Generate shell completions
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
mkdir -p %{buildroot}%{_datadir}/zsh/site-functions
mkdir -p %{buildroot}%{_datadir}/fish/vendor_completions.d

HOME=%{_tmppath} ./opencode --completions bash > %{buildroot}%{_datadir}/bash-completion/completions/opencode || true
HOME=%{_tmppath} ./opencode --completions zsh > %{buildroot}%{_datadir}/zsh/site-functions/_opencode || true
HOME=%{_tmppath} ./opencode --completions fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/opencode.fish || true

%check
HOME=%{_tmppath} %{buildroot}%{_bindir}/opencode --version

%files
%{_bindir}/opencode
%{_datadir}/bash-completion/completions/opencode
%{_datadir}/zsh/site-functions/_opencode
%{_datadir}/fish/vendor_completions.d/opencode.fish

%changelog
* Thu Nov 26 2026 Azhar Momin <azhar-momin@outlook.com> - 2.4.2-1
- Upstream release update to 2.4.2

* Mon Nov 23 2026 Azhar Momin <azhar-momin@outlook.com> - 2.4.1-1
- Upstream release update to 2.4.1

* Mon Nov 23 2026 Azhar Momin <azhar-momin@outlook.com> - 2.4.0-1
- Upstream release update to 2.4.0

* Sun Nov 22 2026 Azhar Momin <azhar-momin@outlook.com> - 2.3.2-1
- Initial Fedora RPM packaging for OpenCode CLI 2.3.2
- Standalone native binary with x86_64 and aarch64 support
- Include bash, zsh, and fish autocompletions
