# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.21
# 
# >> macros
%define plugins down-root auth-pam
# << macros

Name:       openvpn
Summary:    A full-featured SSL VPN solution
Version:    2.2.0
Release:    1
Group:      Applications/Internet
License:    GPLv2
URL:        http://openvpn.net/
Source0:    http://openvpn.net/release/%{name}-%{version}.tar.gz
Source1:    http://openvpn.net/signatures/%{name}-%{version}.tar.gz.asc
Source2:    roadwarrior-server.conf
Source3:    roadwarrior-client.conf
Source100:  openvpn.yaml
Requires:   iproute
Requires:   net-tools
Requires(pre): /usr/sbin/useradd
BuildRequires:  lzo-devel
BuildRequires:  openssl-devel
BuildRequires:  pam-devel
BuildRequires:  pkcs11-helper-devel
BuildRequires:  iproute


%description
OpenVPN is a robust and highly flexible tunneling application that uses all
of the encryption, authentication, and certification features of the
OpenSSL library to securely tunnel IP networks over a single UDP or TCP
port.  It can use the Marcus Franz Xaver Johannes Oberhumer's LZO library
for compression.




%prep
%setup -q -n %{name}-%{version}

# >> setup
# << setup

%build
# >> build pre
# << build pre

%configure --disable-static \
    --enable-pthread \
    --enable-password-save \
    --enable-iproute2 \
    --with-ifconfig-path=/sbin/ifconfig \
    --with-iproute-path=/sbin/ip \
    --with-route-path=/sbin/route

make %{?jobs:-j%jobs}

# >> build post
for plugin in %{plugins} ; do
%{__make} -C plugin/$plugin
done
# << build post
%install
rm -rf %{buildroot}
# >> install pre
# << install pre
%make_install

# >> install post
rm -rf $RPM_BUILD_ROOT

install -D -m 0644 %{name}.8 $RPM_BUILD_ROOT%{_mandir}/man8/%{name}.8
install -D -m 0755 %{name} $RPM_BUILD_ROOT%{_sbindir}/%{name}
install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -pR easy-rsa $RPM_BUILD_ROOT%{_datadir}/%{name}/
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/easy-rsa/Windows
cp %{SOURCE2} %{SOURCE3} sample-config-files/

chmod -x sample-scripts/*
chmod -x sample-config-files/*

mkdir -p $RPM_BUILD_ROOT%{_libdir}/%{name}/plugin/lib
for plugin in %{plugins} ; do
    install -m 0755 plugin/$plugin/openvpn-$plugin.so \
        $RPM_BUILD_ROOT%{_libdir}/%{name}/plugin/lib/openvpn-$plugin.so
    cp plugin/$plugin/README plugin/$plugin.txt
done

mkdir -m 755 -p $RPM_BUILD_ROOT%{_var}/run/%{name}

# << install post
%check
# >> check
# Test Crypto:
./openvpn --genkey --secret key
./openvpn --test-crypto --secret key

%ifnarch %{arm}
# Randomize ports for tests to avoid conflicts on the build servers.
cport=$[ 50000 + ($RANDOM % 15534) ]
sport=$[ $cport + 1 ]
sed -e 's/^\(rport\) .*$/\1 '$sport'/' \
    -e 's/^\(lport\) .*$/\1 '$cport'/' \
    < sample-config-files/loopback-client \
    > %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-client
sed -e 's/^\(rport\) .*$/\1 '$cport'/' \
    -e 's/^\(lport\) .*$/\1 '$sport'/' \
    < sample-config-files/loopback-server \
    > %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-server

# Test SSL/TLS negotiations (runs for 2 minutes):
./openvpn --config \
    %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-client &
./openvpn --config \
    %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-server
wait

rm -f %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-client \
    %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u})-loopback-server
%endif
# << check

%pre
# >> pre
getent group openvpn &>/dev/null || groupadd -r openvpn
getent passwd openvpn &>/dev/null || \
    /usr/sbin/useradd -r -g openvpn -s /sbin/nologin -c OpenVPN \
        -d /etc/openvpn openvpn
# << pre


%files
%defattr(-,root,root,-)
# >> files
%defattr(-,root,root,0755)
%doc AUTHORS COPYING COPYRIGHT.GPL INSTALL PORTS README
# Add NEWS when it isn't zero-length.
%doc plugin/*.txt
%doc contrib  sample-keys sample-scripts sample-config-files
%{_mandir}/man8/%{name}.8*
%{_sbindir}/%{name}
%{_datadir}/%{name}/
%{_libdir}/%{name}/
%{_var}/run/%{name}/
%config %dir %{_sysconfdir}/%{name}/
# << files


