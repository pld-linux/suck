%include	/usr/lib/rpm/macros.perl
Summary:	suck receives/sends news via NNTP
Summary(pl):	suck odbiera i wysy³a newsy przez NNTP
Name:		suck
Version:	4.3.1
Release:	2
License:	Public Domain
Group:		Networking/News
Source0:	ftp://sunsite.unc.edu/pub/Linux/system/news/transport/%{name}-%{version}.tar.gz
Source1:	%{name}.logrotate
Patch0:		%{name}-PLD.patch
Patch1:		%{name}-DESTDIR.patch
Patch2:		%{name}-perl-5.6.patch
Patch3:		%{name}-gets.patch
URL:		http://www.sucknews.org/index.html
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	inn-devel >= 2.0
BuildRequires:	openssl-devel >= 0.9.7
BuildRequires:	perl-devel >= 5.6.1
Requires:	inn-libs >= 2.0
Provides:	news-sucker
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir	/var/lib/suck
%define		_sysconfdir	/etc

%description
The primary use for suck is to feed a local INN or CNEWS server,
without the remote NNTP feeding you articles. It is designed for a
small, partial news feed. It is NOT designed to feed 10,000 groups and
3 Gigs of articles a day.

Read %{_defaultdocdir}/%{name}-%{version}/README.FIRST* after
installing this package!

%description -l pl
suck dostarcza posty lokalnemu serwerowi newsów, INN-owi albo
CNEWS-owi, przed zdalnym serwerem udaj±c zwyk³y czytnik, a wiêc bez
wymagania konfiguracji feedu z tamtej strony. Jest przeznaczony do
ma³ego, czê¶ciowego feedu. Nie jest przeznaczony dla 10000 grup i 3 GB
postów dziennie.

Przeczytaj %{_defaultdocdir}/%{name}-%{version}/README.FIRST* po
zainstalowaniu tego pakietu!

%prep
%setup -q
#%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__aclocal}
%{__autoconf}
%configure

# workaround for stupid inn 2.3 headers
cat >> config.h <<EOF
#define BOOL int
#define OFFSET_T off_t
EOF

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir},/etc/logrotate.d} \
	$RPM_BUILD_ROOT/var/log

%{__make} installall DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install sample/put.news \
	sample/put.news.sm \
	sample/get.news.* \
	sample/*.pl \
	$RPM_BUILD_ROOT%{_localstatedir}
install sample/sucknewsrc.sample \
	$RPM_BUILD_ROOT%{_localstatedir}/sucknewsrc

touch $RPM_BUILD_ROOT/var/log/suck.errlog
touch $RPM_BUILD_ROOT%{_localstatedir}/suck.killlog

cat > $RPM_BUILD_ROOT%{_localstatedir}/active-ignore <<EOF
control
control.cancel
junk
to
test
EOF

mv perl/README perl/README.perl
install -d	$RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -r sample/*	$RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc  CHANGELOG CONTENTS README README.Gui README.Xover perl
%attr(755,root,root) %{_bindir}/*

%config /etc/logrotate.d/suck
%dir %{_localstatedir}
%attr(750,root,root) %config(noreplace) %{_localstatedir}/get.news.inn
%attr(750,root,root) %config(noreplace) %{_localstatedir}/get.news.generic
%attr(750,root,root) %config(noreplace) %{_localstatedir}/put.news
%attr(750,root,root) %config(noreplace) %{_localstatedir}/put.news.sm
%attr(750,root,root) %config(noreplace) %{_localstatedir}/*.pl
%attr(640,root,root) %config(noreplace) %{_localstatedir}/sucknewsrc
%attr(640,root,root) %config(noreplace) %{_localstatedir}/active-ignore
%{_mandir}/man1/*

%attr(640,root,root) %ghost %{_localstatedir}/suck.killlog*
%attr(640,root,root) %ghost /var/log/*

%{_examplesdir}/%{name}-%{version}
