Release:    1
Summary:    Just a demo test
Group:      A group
License:    A license
Source0:    %{name}-%{version}.tar.gz
Autoreq:    No
%description
description description description description description
%define _rpmfilename %{name}-%{version}.rpm
%prep
%setup -q
%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}/%{DESTDIR}
cp -r * %{buildroot}/%{DESTDIR}
%clean
rm -rf $RPM_BUILD_DIR/*
rm -rf $RPM_BUILD_ROOT
%files
%{DESTDIR}/*
%dir %{DESTDIR}/
