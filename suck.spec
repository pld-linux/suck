%include	/usr/lib/rpm/macros.perl
Summary:	suck receives/sends news via NNTP
Summary(pl):	suck odbiera i wysy³a newsy przez NNTP
Name:		suck
Version:	4.2.4
Release:	2
LIcense:	Public Domain
Group:		Networking/News
Group(pl):	Sieciowe/News
Source0:	http://home.att.net/~bobyetman/%{name}-%{version}.tar.gz
Source1:	%{name}.logrotate
Patch0:		%{name}-PLD.patch
Patch1:		%{name}-DESTDIR.patch
Patch2:		%{name}-perl-5.6.patch
URL:		http://home.att.net/~bobyetman/index.html
BuildRequires:	perl
BuildRequires:	inn-devel >= 2.0
Requires:	inn-libs >= 2.0
Requires:	%{perl_archlib}
%requires_eq    perl
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
suck dostarcza posty lokalnemu serwerowi newsów, INN-owi albo
CNEWS-owi, przed zdalnym serwerem udaj±c zwyk³y czytnik, a wiêc bez
wymagania konfiguracji feedu z tamtej strony. Jest przeznaczony do
ma³ego, czê¶ciowego feedu. Nie jest przeznaczony dla 10000 grup i 3 GB
postów dziennie.

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
CFLAGS="$RPM_OPT_FLAGS"
LDFLAGS="-s"
export PERL_CORE_PLD PERL_LIB_PLD CFLAGS LDFLAGS
%configure

# workaround for stupid inn 2.3 headers
echo -e '#define HAVE_STRDUP\n#define HAVE_STRSPN' >> config.h
echo -e '#define BOOL int\n#define OFFSET_T off_t' >> config.h
echo '#define DO_TAGGED_HASH 1' >> config.h

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir},%{_sysconfdir}/logrotate.d} \
	$RPM_BUILD_ROOT/var/log

%{__make} installall DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install sample/put.news \
	sample/put.news.sm \
	sample/*.pl \
	$RPM_BUILD_ROOT%{_localstatedir}
install sample/sucknewsrc.sample \
	$RPM_BUILD_ROOT%{_localstatedir}/sucknewsrc

# default to put.news.sm (required for inn 2.3)
for f in get.news.inn get.news.generic ; do
  sed 's/^\(SCRIPT.*\)put\.news/\1put.news.sm/' \
    < sample/$f > $RPM_BUILD_ROOT%{_localstatedir}/$f
done

touch $RPM_BUILD_ROOT/var/log/suck.errlog
touch $RPM_BUILD_ROOT%{_localstatedir}/suck.killlog

cat > $RPM_BUILD_ROOT%{_localstatedir}/active-ignore <<EOF
control
junk
to
test
EOF

gzip -9nf $RPM_BUILD_ROOT%{_mandir}/man1/* \
	CHANGELOG CONTENTS README README.Gui README.Xover README.FIRST \
	perl/README

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc {CHANGELOG,CONTENTS,README,README.Gui,README.Xover,README.FIRST}.gz
%doc sample perl

%attr(755,root,root) %{_bindir}/*

%config %{_sysconfdir}/logrotate.d/suck

%attr(755,root,root) %dir %{_localstatedir}
%config %attr(750,root,root) %{_localstatedir}/get.news.inn
%config %attr(750,root,root) %{_localstatedir}/get.news.generic
%config %attr(750,root,root) %{_localstatedir}/put.news
%config %attr(750,root,root) %{_localstatedir}/put.news.sm
%config %attr(750,root,root) %{_localstatedir}/*.pl
%config %attr(640,root,root) %{_localstatedir}/sucknewsrc
%config %attr(640,root,root) %{_localstatedir}/active-ignore

%attr(640,root,root) %ghost %{_localstatedir}/suck.killlog*
%attr(640,root,root) %ghost /var/log/*

%{_mandir}/man1/*
