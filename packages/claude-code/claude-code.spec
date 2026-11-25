Name:           claude-code
Version:        2.1.332
Release:        1%{?dist}
Summary:        Claude Code - Agentic coding assistant for your terminal

License:        Proprietary
URL:            https://claude.ai/code
Source0:        https://downloads.claude.ai/claude-code-releases/%{version}/linux-x64/claude.zst#/claude-code-%{version}-x86_64.zst
Source1:        https://downloads.claude.ai/claude-code-releases/%{version}/linux-arm64/claude.zst#/claude-code-%{version}-aarch64.zst

ExclusiveArch:  x86_64 aarch64

BuildRequires:  zstd

Provides:       claude = %{version}-%{release}
Provides:       claude-code = %{version}-%{release}

# Disable debuginfo package generation and stripping for pre-built binaries
%global debug_package %{nil}
%define __strip /bin/true
%define _build_id_links none

%description
Claude Code is Anthropic's agentic coding assistant for your terminal. It explores
codebases, edits files across projects, executes tests, resolves errors, and
automates git workflows directly from the command line.

%prep
%setup -q -c -T -n claude-code-%{version}
%ifarch x86_64
zstd -d -c %{SOURCE0} > claude
%elifarch aarch64
zstd -d -c %{SOURCE1} > claude
%endif
chmod 755 claude

%build
# Pre-compiled standalone binary; no compilation needed

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
install -m 755 claude %{buildroot}%{_bindir}/claude
ln -sf claude %{buildroot}%{_bindir}/claude-code

%check
./claude --version

%files
%{_bindir}/claude
%{_bindir}/claude-code

%changelog
* Wed Nov 25 2026 Azhar Momin <azhar-momin@outlook.com> - 2.1.332-1
- Upstream release update to 2.1.332

* Mon Nov 23 2026 Azhar Momin <azhar-momin@outlook.com> - 2.1.331-1
- Upstream release update to 2.1.331

* Sat Nov 21 2026 Azhar Momin <azhar-momin@outlook.com> - 2.1.330-1
- Upstream release update to 2.1.330

* Fri Nov 20 2026 Azhar Momin <azhar-momin@outlook.com> - 2.1.329-1
- Upstream release update to 2.1.329

* Thu Nov 19 2026 Azhar Momin <azhar-momin@outlook.com> - 2.1.328-1
- Upstream release update to 2.1.328

* Wed Nov 18 2026 Azhar Momin <azhar-momin@outlook.com> - 2.1.327-1
- Initial Fedora RPM packaging for Claude Code 2.1.327
- Standalone native binary release with x86_64 and aarch64 support
