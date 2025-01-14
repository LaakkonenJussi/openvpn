Name:       openvpn
Summary:    A full-featured SSL VPN solution
Version:    2.5.2
Release:    1
License:    GPLv2
URL:        http://openvpn.net/
Source0:    http://swupdate.openvpn.org/community/releases/%{name}-%{version}.tar.xz
Patch1:     tls-verify-command-disable.diff
Requires:   iproute
Requires:   net-tools
Requires(pre): /usr/sbin/useradd

# %license requires reasonably fresh rpm
BuildRequires:  rpm >= 4.11
BuildRequires:  pkgconfig(openssl) >= 0.9.6
BuildRequires:  pkgconfig(libpkcs11-helper-1)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  lzo-devel
BuildRequires:  pam-devel
BuildRequires:  iproute
BuildRequires:  libtool
BuildRequires:  python3-docutils

%description
OpenVPN is a robust and highly flexible tunneling application that uses all
of the encryption, authentication, and certification features of the
OpenSSL library to securely tunnel IP networks over a single UDP or TCP
port.  It can use the Marcus Franz Xaver Johannes Oberhumer's LZO library
for compression.

%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}

%description doc
Man page for %{name}.

%package devel
Summary:   Development headers for %{name}
Requires:  %{name} = %{version}-%{release}

%description devel
%{summary}.

%prep
%setup -q -n %{name}-%{version}/%{name}
%patch1 -p1

%build

autoreconf -vfi

%configure --disable-static \
    --enable-password-save \
    --enable-iproute2 \
    --enable-plugins \
    --enable-plugin-down-root \
    --enable-plugin-auth-pam \
    --enable-x509-alt-username \
    --enable-systemd \
    --docdir=%{_docdir}/%{name}-%{version}

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

rm -rf $RPM_BUILD_ROOT

install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}

%{__make} install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -name '*.la' | xargs rm -f

rm $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/{COPYING,COPYRIGHT.GPL}
ln -s ../../licenses/%{name}-%{version}/COPYING \
   $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/COPYING
ln -s ../../licenses/%{name}-%{version}/COPYRIGHT.GPL \
   $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/COPYRIGHT.GPL

%check
# Test Crypto:
./src/openvpn/openvpn --genkey --secret key
./src/openvpn/openvpn --test-crypto --secret key
# Randomize ports for tests to avoid conflicts on the build servers.
cport=$[ 50000 + ($RANDOM % 15534) ]
sport=$[ $cport + 1 ]
sed -e 's/^\(rport\) .*$/\1 '$sport'/' \
-e 's/^\(lport\) .*$/\1 '$cport'/' \
< sample/sample-config-files/loopback-client \
> %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-client
sed -e 's/^\(rport\) .*$/\1 '$cport'/' \
-e 's/^\(lport\) .*$/\1 '$sport'/' \
< sample/sample-config-files/loopback-server \
> %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-server

pushd sample
# Test SSL/TLS negotiations (runs for 2 minutes):
../src/openvpn/openvpn --config \
%{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-client &
../src/openvpn/openvpn --config \
%{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-server
wait
popd

rm -f %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-client \
%{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-server

%pre
getent group openvpn >/dev/null 2>&1 || groupadd -r openvpn || :
getent passwd openvpn >/dev/null 2>&1 || /usr/sbin/useradd -r -g openvpn -s /sbin/nologin -c OpenVPN -d /etc/openvpn openvpn || :

%files
%defattr(-,root,root,0755)
%license COPYING COPYRIGHT.GPL
%{_sbindir}/%{name}
%{_libdir}/%{name}/
%config %dir %{_sysconfdir}/%{name}/
# We are not presently using the systemd system configuration but want the feature enabled for
# password prompts
%exclude %{_libdir}/tmpfiles.d/openvpn.conf
%exclude %{_libdir}/systemd/system/openvpn-client@.service
%exclude %{_libdir}/systemd/system/openvpn-server@.service

%files doc
%defattr(-,root,root,0755)
%{_mandir}/man8/%{name}.*
%{_docdir}/%{name}-%{version}
%exclude %{_docdir}/%{name}-%{version}/README.IPv6
%exclude %{_docdir}/%{name}-%{version}/README.mbedtls
%exclude %{_docdir}/%{name}-%{version}/management-notes.txt

%files devel
%{_includedir}/openvpn-plugin.h
%{_includedir}/openvpn-msg.h
