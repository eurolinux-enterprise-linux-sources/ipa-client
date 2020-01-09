# Define ONLY_CLIENT to only make the ipa-client and ipa-python subpackages
%{!?ONLY_CLIENT:%global ONLY_CLIENT 0}

# Define WITH_RADIUS to build the radius packages
%global WITH_RADIUS 0

%global httpd_conf /etc/httpd/conf.d
%global plugin_dir %{_libdir}/dirsrv/plugins
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%global POLICYCOREUTILSVER 1.33.12-1
%global gettext_domain ipa

Name:           ipa
Version:        1.9.0.pre3
Release:        0%{?dist}
Summary:        The Identity, Policy and Audit system

Group:          System Environment/Base
License:        GPLv2
URL:            http://www.freeipa.org/
Source0:        freeipa-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if ! %{ONLY_CLIENT}
BuildRequires:  fedora-ds-base-devel >= 1.1.3
BuildRequires:  mozldap-devel
BuildRequires:  svrcore-devel
BuildRequires:  nspr-devel
BuildRequires:  openssl-devel
BuildRequires:  openldap-devel
BuildRequires:  e2fsprogs-devel
BuildRequires:  krb5-devel
BuildRequires:  nss-devel
BuildRequires:  libcap-devel
BuildRequires:  python-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  popt-devel
BuildRequires:  /usr/share/selinux/devel/Makefile
BuildRequires:  m4
BuildRequires:  policycoreutils >= %{POLICYCOREUTILSVER}
BuildRequires:  python-setuptools
BuildRequires:  python-krbV
BuildRequires:  xmlrpc-c-devel
BuildRequires:  libcurl-devel
BuildRequires:  gettext
%endif

%description
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof).

%if ! %{ONLY_CLIENT}
%package server
Summary: The IPA authentication server
Group: System Environment/Base
Requires: %{name}-python = %{version}-%{release}
Requires: %{name}-client = %{version}-%{release}
Requires: %{name}-admintools = %{version}-%{release}
Requires(post): %{name}-server-selinux = %{version}-%{release}
Requires: fedora-ds-base >= 1.1.3
Requires: openldap-clients
Requires: nss
Requires: nss-tools
%{?fc8:Requires: krb5-server >= 1.6.2-11}
%if 0%{?fedora} >= 9
Requires: krb5-server
%endif
Requires: krb5-server-ldap
Requires: cyrus-sasl-gssapi
Requires: ntp
Requires: httpd
Requires: mod_python
Requires: mod_wsgi
Requires: mod_auth_kerb
%{?fc8:Requires: mod_nss >= 1.0.7-2}
%{?fc9:Requires: mod_nss >= 1.0.7-5}
%{?fc10:Requires: mod_nss >= 1.0.7-4}
%if 0%{?fedora} >= 10
Requires: mod_nss
%endif
Requires: python-ldap
Requires: python-krbV
Requires: python-assets
Requires: python-wehjit >= 0.2.2
Requires: acl
Requires: python-pyasn1 >= 0.0.9a
Requires: libcap
%{?fc8:Requires: selinux-policy >= 3.0.8-117}
%{?fc9:Requires: selinux-policy >= 3.3.1-99}
%{?fc10:Requires: selinux-policy >= 3.5.13-11}
%if 0%{?fedora} >= 10
Requires: selinux-policy
%endif
Requires(post): selinux-policy-base
Requires: slapi-nis >= 0.15
Requires: pki-ca
Conflicts: mod_ssl

%description server
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof). If you are installing an IPA server you need
to install this package (in other words, most people should NOT install
this package).


%package server-selinux
Summary: SELinux rules for ipa-server daemons
Group: System Environment/Base
Requires: %{name}-server = %{version}-%{release}
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER} libsemanage

%description server-selinux
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof). This package provides SELinux rules for the
daemons included in ipa-server
%endif


%package client
Summary: IPA authentication for use on clients
Group: System Environment/Base
Requires: %{name}-python = %{version}-%{release}
Requires: python-ldap
Requires: python-krbV
Requires: cyrus-sasl-gssapi
Requires: ntp
Requires: krb5-workstation
Requires: krb5-libs
Requires: authconfig
Requires: pam_krb5
Requires: nss_ldap
Requires: wget
Requires: xmlrpc-c
Requires: libcurl
Requires: sssd >= 1.1.1
Requires: certmonger

%description client
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof). If your network uses IPA for authentication,
this package should be installed on every client machine.


%if ! %{ONLY_CLIENT}
%package admintools
Summary: IPA administrative tools
Group: System Environment/Base
Requires: %{name}-python = %{version}-%{release}
Requires: python-krbV
Requires: python-ldap
Requires: python-configobj

%description admintools
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof). This package provides command-line tools for
IPA administrators.
%endif

%package python
Summary: Python libraries used by IPA
Group: System Environment/Libraries
%{?fc8:Requires: python-kerberos >= 1.0}
%if 0%{?fedora} >= 9
Requires: python-kerberos >= 1.1-3
%endif
Requires: authconfig
Requires: gnupg
Requires: pyOpenSSL
Requires: python-nss >= 0.8
Requires: python-lxml

%description python
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof). If you are using IPA you need to install this
package.

%if %{WITH_RADIUS}
%package radius-server
Summary: IPA authentication server - radius plugin
Group: System Environment/Base
Requires: freeradius
Requires: freeradius-ldap
Requires: %{name}-python = %{version}-%{release}

%description radius-server
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof). This plugin enables radius support.

%package radius-admintools
Summary: IPA authentication server - radius administration tools
Group: System Environment/Base
Requires: %{name}-python = %{version}-%{release}
Requires: %{name}-admintools = %{version}-%{release}
Requires: python-krbV

%description radius-admintools
IPA is an integrated solution to provide centrally managed Identity (machine,
user, virtual machines, groups, authentication credentials), Policy
(configuration settings, access control information) and Audit (events,
logs, analysis thereof). This package provides command-line tools for
administering radius authentication settings in IPA.
%endif


%prep
%setup -n freeipa-%{version} -q

%build
export CFLAGS="$CFLAGS %{optflags}"
export CPPFLAGS="$CPPFLAGS %{optflags}"
make version-update
%if ! %{ONLY_CLIENT}
touch daemons/NEWS daemons/README daemons/AUTHORS daemons/ChangeLog
touch install/NEWS install/README install/AUTHORS install/ChangeLog
%endif
cd ipa-client; ../autogen.sh --prefix=%{_usr} --sysconfdir=%{_sysconfdir} --localstatedir=%{_localstatedir} --libdir=%{_libdir} --mandir=%{_mandir} --with-openldap; cd ..
%if ! %{ONLY_CLIENT}
cd daemons; ../autogen.sh --prefix=%{_usr} --sysconfdir=%{_sysconfdir} --localstatedir=%{_localstatedir} --libdir=%{_libdir} --mandir=%{_mandir}; cd ..
cd install; ../autogen.sh --prefix=%{_usr} --sysconfdir=%{_sysconfdir} --localstatedir=%{_localstatedir} --libdir=%{_libdir} --mandir=%{_mandir}; cd ..
%endif

%if ! %{ONLY_CLIENT}
make IPA_VERSION_IS_GIT_SNAPSHOT=no %{?_smp_mflags} version-update all
cd selinux
# This isn't multi-process make capable yet
make all
%else
make IPA_VERSION_IS_GIT_SNAPSHOT=no %{?_smp_mflags} version-update client
%endif

%install
rm -rf %{buildroot}
%if ! %{ONLY_CLIENT}
make install DESTDIR=%{buildroot}
cd selinux
make install DESTDIR=%{buildroot}
cd ..
%else
make client-install DESTDIR=%{buildroot}
%endif
%find_lang %{gettext_domain}


%if ! %{ONLY_CLIENT}
# Remove .la files from libtool - we don't want to package
# these files
rm %{buildroot}/%{plugin_dir}/libipa_pwd_extop.la
rm %{buildroot}/%{plugin_dir}/libipa_enrollment_extop.la
rm %{buildroot}/%{plugin_dir}/libipa_winsync.la

# Some user-modifiable HTML files are provided. Move these to /etc
# and link back.
mkdir -p %{buildroot}/%{_sysconfdir}/ipa/html
mkdir -p %{buildroot}/%{_localstatedir}/cache/ipa/sysrestore
mkdir %{buildroot}%{_usr}/share/ipa/html/
ln -s ../../../..%{_sysconfdir}/ipa/html/ssbrowser.html \
    %{buildroot}%{_usr}/share/ipa/html/ssbrowser.html
ln -s ../../../..%{_sysconfdir}/ipa/html/unauthorized.html \
    %{buildroot}%{_usr}/share/ipa/html/unauthorized.html

# So we can own our Apache configuration
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/
/bin/touch $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/ipa.conf
/bin/touch $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/ipa-rewrite.conf
%endif
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ipa/
/bin/touch $RPM_BUILD_ROOT%{_sysconfdir}/ipa/default.conf
mkdir -p %{buildroot}/%{_localstatedir}/lib/ipa-client/sysrestore

%if ! %{ONLY_CLIENT}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
install -pm 644 contrib/completion/ipa.bash_completion $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/ipa
%endif

%clean
rm -rf %{buildroot}

%if ! %{ONLY_CLIENT}
%post server
if [ $1 = 1 ]; then
    /sbin/chkconfig --add ipa_kpasswd
fi
if [ -e /usr/share/ipa/serial ]; then
    mv /usr/share/ipa/serial /var/lib/ipa/ca_serialno
fi
/usr/sbin/ipa-upgradeconfig || :
if [ -e /etc/httpd/conf.d/ipa.conf ]; then
    echo ""
    echo "Run /usr/sbin/ipa-ldap-updater to complete the upgrade process."
    echo ""
fi

%preun server
if [ $1 = 0 ]; then
    /sbin/chkconfig --del ipa_kpasswd
    /sbin/service ipa_kpasswd stop >/dev/null 2>&1 || :
fi

%postun server
if [ "$1" -ge "1" ]; then
    /sbin/service ipa_kpasswd condrestart >/dev/null 2>&1 || :
    /sbin/service httpd condrestart >/dev/null 2>&1 || :
    /sbin/service dirsrv condrestart >/dev/null 2>&1 || :
fi

%pre server-selinux
if [ -s /etc/selinux/config ]; then
       . %{_sysconfdir}/selinux/config
       FILE_CONTEXT=%{_sysconfdir}/selinux/targeted/contexts/files/file_contexts
       if [ "${SELINUXTYPE}" == targeted -a -f ${FILE_CONTEXT} ]; then \
               cp -f ${FILE_CONTEXT} ${FILE_CONTEXT}.%{name}
       fi
fi

%post server-selinux
semodule -s targeted -i /usr/share/selinux/targeted/ipa_kpasswd.pp /usr/share/selinux/targeted/ipa_httpd.pp
. %{_sysconfdir}/selinux/config
FILE_CONTEXT=%{_sysconfdir}/selinux/targeted/contexts/files/file_contexts
selinuxenabled
if [ $? == 0  -a "${SELINUXTYPE}" == targeted -a -f ${FILE_CONTEXT}.%{name} ]; then
       fixfiles -C ${FILE_CONTEXT}.%{name} restore
       rm -f ${FILE_CONTEXT}.%name
fi

%preun server-selinux
if [ $1 = 0 ]; then
if [ -s /etc/selinux/config ]; then
       . %{_sysconfdir}/selinux/config
       FILE_CONTEXT=%{_sysconfdir}/selinux/targeted/contexts/files/file_contexts
       if [ "${SELINUXTYPE}" == targeted -a -f ${FILE_CONTEXT} ]; then \
               cp -f ${FILE_CONTEXT} ${FILE_CONTEXT}.%{name}
       fi
fi
fi

%postun server-selinux
if [ $1 = 0 ]; then
semodule -s targeted -r ipa_kpasswd ipa_httpd
. %{_sysconfdir}/selinux/config
FILE_CONTEXT=%{_sysconfdir}/selinux/targeted/contexts/files/file_contexts
selinuxenabled
if [ $? == 0  -a "${SELINUXTYPE}" == targeted -a -f ${FILE_CONTEXT}.%{name} ]; then
       fixfiles -C ${FILE_CONTEXT}.%{name} restore
       rm -f ${FILE_CONTEXT}.%name
fi
fi
%endif


%if ! %{ONLY_CLIENT}
%files server
%doc LICENSE README Contributors.txt
%defattr(-,root,root,-)
%{_sbindir}/ipa-dns-install
%{_sbindir}/ipa-server-install
%{_sbindir}/ipa-replica-install
%{_sbindir}/ipa-replica-prepare
%{_sbindir}/ipa-replica-manage
%{_sbindir}/ipa-server-certinstall
%{_sbindir}/ipa_kpasswd
%{_sbindir}/ipactl
%{_sbindir}/ipa-upgradeconfig
%attr(755,root,root) %{_initrddir}/ipa_kpasswd
%{python_sitelib}/ipaserver/*
%{python_sitelib}/ipawebui/*
%dir %{_usr}/share/ipa
%{_usr}/share/ipa/wsgi.py*
%{_usr}/share/ipa/*.ldif
%{_usr}/share/ipa/*.uldif
%{_usr}/share/ipa/*.template
%dir %{_usr}/share/ipa/html
%{_usr}/share/ipa/html/ssbrowser.html
%{_usr}/share/ipa/html/unauthorized.html
%dir %{_usr}/share/ipa/migration
%{_usr}/share/ipa/migration/error.html
%{_usr}/share/ipa/migration/index.html
%{_usr}/share/ipa/migration/invalid.html
%{_usr}/share/ipa/migration/migration.css
%{_usr}/share/ipa/migration/migration.py*
%dir %{_sysconfdir}/ipa
%dir %{_sysconfdir}/ipa/html
%config(noreplace) %{_sysconfdir}/ipa/html/ssbrowser.html
%config(noreplace) %{_sysconfdir}/ipa/html/unauthorized.html
%ghost %attr(0644,root,apache) %config(noreplace) %{_sysconfdir}/ipa/default.conf
%ghost %attr(0644,root,apache) %config(noreplace) %{_sysconfdir}/httpd/conf.d/ipa-rewrite.conf
%ghost %attr(0644,root,apache) %config(noreplace) %{_sysconfdir}/httpd/conf.d/ipa.conf
%{_usr}/share/ipa/ipa.conf
%{_usr}/share/ipa/ipa-rewrite.conf
#%dir %{_usr}/share/ipa/ipaserver
#%{_usr}/share/ipa/ipaserver/*
%dir %{_usr}/share/ipa/updates/
%{_usr}/share/ipa/updates/*
%attr(755,root,root) %{plugin_dir}/libipa_pwd_extop.so
%attr(755,root,root) %{plugin_dir}/libipa_enrollment_extop.so
%attr(755,root,root) %{plugin_dir}/libipa_winsync.so
%dir %{_localstatedir}/lib/ipa
%attr(700,root,root) %dir %{_localstatedir}/lib/ipa/sysrestore
%dir %{_localstatedir}/cache/ipa
%attr(700,apache,apache) %dir %{_localstatedir}/cache/ipa/sessions
%attr(700,apache,apache) %dir %{_localstatedir}/cache/ipa/assets
%attr(700,root,root) %dir %{_localstatedir}/cache/ipa/kpasswd
%{_mandir}/man1/ipa-replica-install.1.gz
%{_mandir}/man1/ipa-replica-manage.1.gz
%{_mandir}/man1/ipa-replica-prepare.1.gz
%{_mandir}/man1/ipa-server-certinstall.1.gz
%{_mandir}/man1/ipa-server-install.1.gz
%{_mandir}/man8/ipa_kpasswd.8.gz
%{_mandir}/man8/ipactl.8.gz
%{_mandir}/man1/ipa-compat-manage.1.gz
%{_mandir}/man1/ipa-nis-manage.1.gz
%{_mandir}/man1/ipa-ldap-updater.1.gz

%files server-selinux
%{_usr}/share/selinux/targeted/ipa_kpasswd.pp
%{_usr}/share/selinux/targeted/ipa_httpd.pp
%{_usr}/share/selinux/targeted/ipa_dogtag.pp
%endif

%files client
%doc LICENSE README Contributors.txt
%{_sbindir}/ipa-client-install
%{_sbindir}/ipa-getkeytab
%{_sbindir}/ipa-rmkeytab
%{_sbindir}/ipa-join
%dir %{_usr}/share/ipa
%dir %{_usr}/share/ipa/ipaclient
%dir %{_localstatedir}/lib/ipa-client
%dir %{_localstatedir}/lib/ipa-client/sysrestore
%{_usr}/share/ipa/ipaclient/ipa.cfg
%{_usr}/share/ipa/ipaclient/ipa.js
%dir %{python_sitelib}/ipaclient
%{python_sitelib}/ipaclient/*.py*
%{_mandir}/man1/ipa-getkeytab.1.gz
%{_mandir}/man1/ipa-rmkeytab.1.gz
%{_mandir}/man1/ipa-client-install.1.gz
%{_mandir}/man1/ipa-join.1.gz

%if ! %{ONLY_CLIENT}
%files admintools
%doc LICENSE README Contributors.txt
%defattr(-,root,root,-)
%{_bindir}/ipa
%{_sbindir}/ipa-fix-CVE-2008-3274
%{_sbindir}/ipa-ldap-updater
%{_sbindir}/ipa-compat-manage
%{_sbindir}/ipa-nis-manage
%{_sysconfdir}/bash_completion.d
%{_mandir}/man1/ipa.1.gz
%endif

%files python -f %{gettext_domain}.lang
%doc LICENSE README Contributors.txt
%defattr(-,root,root,-)
%dir %{python_sitelib}/ipapython
%{python_sitelib}/ipapython/*.py*
%{python_sitelib}/ipalib/*
%if 0%{?fedora} >= 9
%{python_sitelib}/ipapython-*.egg-info
%{python_sitelib}/freeipa-*.egg-info
%endif
%config(noreplace) %{_sysconfdir}/ipa/default.conf

%if %{WITH_RADIUS}
%files radius-server
%doc LICENSE README Contributors.txt
%{_usr}/share/ipa/ipaserver/plugins/*
%dir %{_usr}/share/ipa/plugins
%{_usr}/share/ipa/plugins/radius.radiusd.conf.template

%files radius-admintools
%doc LICENSE README Contributors.txt
%{_sbindir}/ipa-addradiusclient
%{_sbindir}/ipa-addradiusprofile
%{_sbindir}/ipa-delradiusclient
%{_sbindir}/ipa-delradiusprofile
%{_sbindir}/ipa-findradiusclient
%{_sbindir}/ipa-findradiusprofile
%{_sbindir}/ipa-modradiusclient
%{_sbindir}/ipa-modradiusprofile
%endif

%changelog
* Mon Apr 26 2010 Rob Crittenden <rcritten@redhat.com> - 1.99-20
- Set minimum level of sssd to 1.1.1 to pull in required hbac fixes.

* Thu Mar  4 2010 Rob Crittenden <rcritten@redhat.com> - 1.99-19
- No need to create /var/log/ipa_error.log since we aren't using
  TurboGears any more.

* Mon Mar 1 2010 Jason Gerard DeRose <jderose@redhat.com> - 1.99-18
- Fixed share/ipa/wsgi.py so .pyc, .pyo files are included

* Wed Feb 24 2010 Jason Gerard DeRose <jderose@redhat.com> - 1.99-17
- Added Require mod_wsgi, added share/ipa/wsgi.py

* Thu Feb 11 2010 Jason Gerard DeRose <jderose@redhat.com> - 1.99-16
- Require python-wehjit >= 0.2.2

* Wed Feb  3 2010 Rob Crittenden <rcritten@redhat.com> - 1.99-15
- Add sssd and certmonger as a Requires on ipa-client

* Wed Jan 27 2010 Jason Gerard DeRose <jderose@redhat.com> - 1.99-14
- Require python-wehjit >= 0.2.0

* Fri Dec  4 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-13
- Add ipa-rmkeytab tool

* Tue Dec  1 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-12
- Set minimum of python-pyasn1 to 0.0.9a so we have support for the ASN.1
  Any type

* Wed Nov 25 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-11
- Remove v1-style /etc/ipa/ipa.conf, replacing with /etc/ipa/default.conf

* Fri Nov 13 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-10
- Add bash completion script and own /etc/bash_completion.d in case it
  doesn't already exist

* Tue Nov  3 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-9
- Remove ipa_webgui, its functions rolled into ipa_httpd

* Mon Oct 12 2009 Jason Gerard DeRose <jderose@redhat.com> - 1.99-8
- Removed python-cherrypy from BuildRequires and Requires
- Added Requires python-assets, python-wehjit

* Mon Aug 24 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-7
- Added httpd SELinux policy so CRLs can be read

* Thu May 21 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-6
- Move ipalib to ipa-python subpackage
- Bump minimum version of slapi-nis to 0.15

* Thu May  6 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-5
- Set 0.14 as minimum version for slapi-nis

* Wed Apr 22 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-4
- Add Requires: python-nss to ipa-python sub-package

* Thu Mar  5 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-3
- Remove the IPA DNA plugin, use the DS one

* Wed Mar  4 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-2
- Build radius separately
- Fix a few minor issues

* Tue Feb  3 2009 Rob Crittenden <rcritten@redhat.com> - 1.99-1
- Replace TurboGears requirement with python-cherrypy

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 1.2.1-3
- rebuild with new openssl

* Fri Dec 19 2008 Dan Walsh <dwalsh@redhat.com> - 1.2.1-2
- Fix SELinux code

* Mon Dec 15 2008 Simo Sorce <ssorce@redhat.com> - 1.2.1-1
- Fix breakage caused by python-kerberos update to 1.1

* Fri Dec 5 2008 Simo Sorce <ssorce@redhat.com> - 1.2.1-0
- New upstream release 1.2.1

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.2.0-4
- Rebuild for Python 2.6

* Fri Nov 14 2008 Simo Sorce <ssorce@redhat.com> - 1.2.0-3
- Respin after the tarball has been re-released upstream
  New hash is 506c9c92dcaf9f227cba5030e999f177

* Thu Nov 13 2008 Simo Sorce <ssorce@redhat.com> - 1.2.0-2
- Conditionally restart also dirsrv and httpd when upgrading

* Wed Oct 29 2008 Rob Crittenden <rcritten@redhat.com> - 1.2.0-1
- Update to upstream version 1.2.0
- Set fedora-ds-base minimum version to 1.1.3 for winsync header
- Set the minimum version for SELinux policy
- Remove references to Fedora 7

* Wed Jul 23 2008 Simo Sorce <ssorce@redhat.com> - 1.1.0-3
- Fix for CVE-2008-3274
- Fix segfault in ipa-kpasswd in case getifaddrs returns a NULL interface
- Add fix for bug #453185
- Rebuild against openldap libraries, mozldap ones do not work properly
- TurboGears is currently broken in rawhide. Added patch to not build
  the UI locales and removed them from the ipa-server files section.

* Wed Jun 18 2008 Rob Crittenden <rcritten@redhat.com> - 1.1.0-2
- Add call to /usr/sbin/upgradeconfig to post install

* Wed Jun 11 2008 Rob Crittenden <rcritten@redhat.com> - 1.1.0-1
- Update to upstream version 1.1.0
- Patch for indexing memberof attribute
- Patch for indexing uidnumber and gidnumber
- Patch to change DNA default values for replicas
- Patch to fix uninitialized variable in ipa-getkeytab

* Fri May 16 2008 Rob Crittenden <rcritten@redhat.com> - 1.0.0-5
- Set fedora-ds-base minimum version to 1.1.0.1-4 and mod_nss minimum
  version to 1.0.7-4 so we pick up the NSS fixes.
- Add selinux-policy-base(post) to Requires (446496)

* Tue Apr 29 2008 Rob Crittenden <rcritten@redhat.com> - 1.0.0-4
- Add missing entry for /var/cache/ipa/kpasswd (444624)
- Added patch to fix permissions problems with the Apache NSS database.
- Added patch to fix problem with DNS querying where the query could be
  returned as the answer.
- Fix spec error where patch1 was in the wrong section

* Fri Apr 25 2008 Rob Crittenden <rcritten@redhat.com> - 1.0.0-3
- Added patch to fix problem reported by ldapmodify

* Fri Apr 25 2008 Rob Crittenden <rcritten@redhat.com> - 1.0.0-2
- Fix Requires for krb5-server that was missing for Fedora versions > 9
- Remove quotes around test for fedora version to package egg-info

* Fri Apr 18 2008 Rob Crittenden <rcritten@redhat.com> - 1.0.0-1
- Update to upstream version 1.0.0

* Tue Mar 18 2008 Rob Crittenden <rcritten@redhat.com> 0.99-12
- Pull upstream changelog 722
- Add Conflicts mod_ssl (435360)

* Thu Feb 29 2008 Rob Crittenden <rcritten@redhat.com> 0.99-11
- Pull upstream changelog 698
- Fix ownership of /var/log/ipa_error.log during install (435119)
- Add pwpolicy command and man page

* Thu Feb 21 2008 Rob Crittenden <rcritten@redhat.com> 0.99-10
- Pull upstream changelog 678
- Add new subpackage, ipa-server-selinux
- Add Requires: authconfig to ipa-python (bz #433747)
- Package i18n files

* Mon Feb 18 2008 Rob Crittenden <rcritten@redhat.com> 0.99-9
- Pull upstream changelog 641
- Require minimum version of krb5-server on F-7 and F-8
- Package some new files

* Thu Jan 31 2008 Rob Crittenden <rcritten@redhat.com> 0.99-8
- Marked with wrong license. IPA is GPLv2.

* Tue Jan 29 2008 Rob Crittenden <rcritten@redhat.com> 0.99-7
- Ensure that /etc/ipa exists before moving user-modifiable html files there
- Put html files into /etc/ipa/html instead of /etc/ipa

* Tue Jan 29 2008 Rob Crittenden <rcritten@redhat.com> 0.99-6
- Pull upstream changelog 608 which renamed several files

* Thu Jan 24 2008 Rob Crittenden <rcritten@redhat.com> 0.99-5
- package the sessions dir /var/cache/ipa/sessions
- Pull upstream changelog 597

* Thu Jan 24 2008 Rob Crittenden <rcritten@redhat.com> 0.99-4
- Updated upstream pull (596) to fix bug in ipa_webgui that was causing the
  UI to not start.

* Thu Jan 24 2008 Rob Crittenden <rcritten@redhat.com> 0.99-3
- Included LICENSE and README in all packages for documentation
- Move user-modifiable content to /etc/ipa and linked back to
  /usr/share/ipa/html
- Changed some references to /usr to the {_usr} macro and /etc
  to {_sysconfdir}
- Added popt-devel to BuildRequires for Fedora 8 and higher and
  popt for Fedora 7
- Package the egg-info for Fedora 9 and higher for ipa-python

* Tue Jan 22 2008 Rob Crittenden <rcritten@redhat.com> 0.99-2
- Added auto* BuildRequires

* Mon Jan 21 2008 Rob Crittenden <rcritten@redhat.com> 0.99-1
- Unified spec file

* Thu Jan 17 2008 Rob Crittenden <rcritten@redhat.com> - 0.6.0-2
- Fixed License in specfile
- Include files from /usr/lib/python*/site-packages/ipaserver

* Fri Dec 21 2007 Karl MacMillan <kmacmill@redhat.com> - 0.6.0-1
- Version bump for release

* Wed Nov 21 2007 Karl MacMillan <kmacmill@mentalrootkit.com> - 0.5.0-1
- Preverse mode on ipa-keytab-util
- Version bump for relase and rpm name change

* Thu Nov 15 2007 Rob Crittenden <rcritten@redhat.com> - 0.4.1-2
- Broke invididual Requires and BuildRequires onto separate lines and
  reordered them
- Added python-tgexpandingformwidget as a dependency
- Require at least fedora-ds-base 1.1

* Thu Nov  1 2007 Karl MacMillan <kmacmill@redhat.com> - 0.4.1-1
- Version bump for release

* Wed Oct 31 2007 Karl MacMillan <kmacmill@redhat.com> - 0.4.0-6
- Add dep for freeipa-admintools and acl

* Wed Oct 24 2007 Rob Crittenden <rcritten@redhat.com> - 0.4.0-5
- Add dependency for python-krbV

* Fri Oct 19 2007 Rob Crittenden <rcritten@redhat.com> - 0.4.0-4
- Require mod_nss-1.0.7-2 for mod_proxy fixes

* Thu Oct 18 2007 Karl MacMillan <kmacmill@redhat.com> - 0.4.0-3
- Convert to autotools-based build

* Tue Sep 25 2007 Karl MacMillan <kmacmill@redhat.com> - 0.4.0-2

* Fri Sep 7 2007 Karl MacMillan <kmacmill@redhat.com> - 0.3.0-1
- Added support for libipa-dna-plugin

* Fri Aug 10 2007 Karl MacMillan <kmacmill@redhat.com> - 0.2.0-1
- Added support for ipa_kpasswd and ipa_pwd_extop

* Mon Aug  5 2007 Rob Crittenden <rcritten@redhat.com> - 0.1.0-3
- Abstracted client class to work directly or over RPC

* Wed Aug  1 2007 Rob Crittenden <rcritten@redhat.com> - 0.1.0-2
- Add mod_auth_kerb and cyrus-sasl-gssapi to Requires
- Remove references to admin server in ipa-server-setupssl
- Generate a client certificate for the XML-RPC server to connect to LDAP with
- Create a keytab for Apache
- Create an ldif with a test user
- Provide a certmap.conf for doing SSL client authentication

* Fri Jul 27 2007 Karl MacMillan <kmacmill@redhat.com> - 0.1.0-1
- Initial rpm version
