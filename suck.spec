%include	/usr/lib/rpm/macros.perl
Summary:	suck receives/sends news via NNTP
Summary(pl):	suck odbiera i wysy�a newsy przez NNTP
Name:		suck
Version:	4.2.5
Release:	3
LIcense:	Public Domain
Group:		Networking/News
Group(de):	Netzwerkwesen/News
Group(pl):	Sieciowe/News
Source0:	ftp://sunsite.unc.edu/pub/Linux/system/news/transport/%{name}-%{version}.tar.gz
#http://home.att.net/~bobyetman/%{name}-%{version}.tar.gz
Source1:	%{name}.logrotate
Patch0:		%{name}-PLD.patch
Patch1:		%{name}-DESTDIR.patch
Patch2:		%{name}-perl-5.6.patch
URL:		http://home.att.net/~bobyetman/
BuildRequires:	perl-devel >= 5.6.1
BuildRequires:	inn-devel >= 2.0
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

Read %{_defaultdocdir}/%{name}-%{version}/README.FIRST.gz after
installing this package!

%description -l pl
suck dostarcza posty lokalnemu serwerowi news�w, INN-owi albo
CNEWS-owi, przed zdalnym serwerem udaj�c zwyk�y czytnik, a wi�c bez
wymagania konfiguracji feedu z tamtej strony. Jest przeznaczony do
ma�ego, cz�ciowego feedu. Nie jest przeznaczony dla 10000 grup i 3 GB
post�w dziennie.

Przeczytaj %{_defaultdocdir}/%{name}-%{version}/README.FIRST.gz po
zainstalowaniu tego pakietu!

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
PERL_CORE_PLD="`perl -MConfig -e 'print $Config{archlib}'`/CORE"
PERL_LIB_PLD="`perl -MExtUtils::Embed -e ldopts | tail -1`"
export PERL_CORE_PLD PERL_LIB_PLD
aclocal
autoconf
%configure

# workaround for stupid inn 2.3 headers
#echo -e '#define HAVE_STRDUP\n#define HAVE_STRSPN' >> config.h
echo -e '#define BOOL int\n#define OFFSET_T off_t' >> config.h

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

gzip -9nf CHANGELOG CONTENTS README README.Gui README.Xover README.FIRST \
	perl/README

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc *.gz sample perl
%attr(755,root,root) %{_bindir}/*

%config %{_sysconfdir}/logrotate.d/suck
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
