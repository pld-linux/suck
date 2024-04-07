Summary:	suck receives/sends news via NNTP
Summary(pl.UTF-8):	suck odbiera i wysyła newsy przez NNTP
Name:		suck
Version:	4.3.5
Release:	1
License:	Public Domain
Group:		Networking/News
#Source0Download: https://github.com/lazarus-pkgs/suck/tags
Source0:	https://github.com/lazarus-pkgs/suck/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	ab13545ad364cb77959e71509638665e
Source1:	%{name}.logrotate
Source2:	%{name}-get-news.sh
Source3:	%{name}-get-news-etc-example
Patch0:		%{name}-PLD.patch
Patch1:		%{name}-perl-5.6.patch
Patch2:		%{name}-gets.patch
# additional IPv6 features from older patch: http://www.bacza.net/files/suck-4.3.2-ipv6.patch
Patch3:		%{name}-ipv6.patch
# temporary workaround for messed headers in inn 2.7.0 (fixed on 2.8 branch)
Patch4:		%{name}-inn.patch
URL:		https://github.com/lazarus-pkgs/suck
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
BuildRequires:	inn-devel >= 2.0
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 4.1-13
Requires:	inn-libs >= 2.0
Provides:	news-sucker
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir	/var/lib/suck

%description
The primary use for suck is to feed a local INN or CNEWS server,
without the remote NNTP feeding you articles. It is designed for a
small, partial news feed. It is NOT designed to feed 10,000 groups and
3 Gigs of articles a day.

Read %{_docdir}/%{name}-%{version}/README.FIRST* after
installing this package!

%description -l pl.UTF-8
suck dostarcza posty lokalnemu serwerowi newsów, INN-owi albo
CNEWS-owi, przed zdalnym serwerem udając zwykły czytnik, a więc bez
wymagania konfiguracji feedu z tamtej strony. Jest przeznaczony do
małego, częściowego feedu. Nie jest przeznaczony dla 10000 grup i 3 GB
postów dziennie.

Przeczytaj %{_docdir}/%{name}-%{version}/README.FIRST* po
zainstalowaniu tego pakietu!

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
CPPFLAGS="%{rpmcppflags} -D_GNU_SOURCE"
%configure \
	--with-inn-lib=%{_libdir}

%{__make} -j1 \
	PERL_LIB="-lperl -lm -lcrypt -lpthread"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir},/etc/{logrotate.d,news/suck}} \
	$RPM_BUILD_ROOT/var/log

%{__make} installall \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install sample/put.news \
	sample/put.news.sm \
	sample/get.news.* \
	sample/*.pl \
	$RPM_BUILD_ROOT%{_localstatedir}

ln -s %{_localstatedir}/get.news.inn $RPM_BUILD_ROOT%{_bindir}/
install sample/sucknewsrc.sample \
	$RPM_BUILD_ROOT%{_localstatedir}/sucknewsrc

install %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/news/suck/news.mimuw.edu.pl-example

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
%attr(755,root,root) %{_bindir}/get.news.inn
%attr(755,root,root) %{_bindir}/lmove
%attr(755,root,root) %{_bindir}/lpost
%attr(755,root,root) %{_bindir}/rpost
%attr(755,root,root) %{_bindir}/suck
%attr(755,root,root) %{_bindir}/suck-get-news.sh
%attr(755,root,root) %{_bindir}/testhost

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/suck
%dir %{_localstatedir}
%attr(750,root,root) %config(noreplace) %{_localstatedir}/get.news.inn
%attr(750,root,root) %config(noreplace) %{_localstatedir}/get.news.generic
%attr(750,root,root) %config(noreplace) %{_localstatedir}/perl_kill.pl
%attr(750,root,root) %config(noreplace) %{_localstatedir}/perl_xover.pl
%attr(750,root,root) %config(noreplace) %{_localstatedir}/post_filter.pl
%attr(750,root,root) %config(noreplace) %{_localstatedir}/put.news
%attr(750,root,root) %config(noreplace) %{_localstatedir}/put.news.pl
%attr(750,root,root) %config(noreplace) %{_localstatedir}/put.news.sm
%attr(750,root,root) %config(noreplace) %{_localstatedir}/put.news.sm.pl
%attr(640,root,root) %config(noreplace) %{_localstatedir}/sucknewsrc
%attr(640,root,root) %config(noreplace) %{_localstatedir}/active-ignore
%dir %{_sysconfdir}/news/suck
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/news/suck/news.mimuw.edu.pl-example
%{_mandir}/man1/lmove.1*
%{_mandir}/man1/lpost.1*
%{_mandir}/man1/rpost.1*
%{_mandir}/man1/suck.1*
%{_mandir}/man1/testhost.1*

%attr(640,root,root) %ghost %{_localstatedir}/suck.killlog
%attr(640,root,root) %ghost /var/log/suck.errlog

%{_examplesdir}/%{name}-%{version}
