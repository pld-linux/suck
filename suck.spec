Summary:	suck receives/sends news via NNTP
Summary(pl):	suck odbiera i wysy³a newsy przez NNTP
Name:		suck
Version:	4.2.1
Release:	1
Copyright:	Public Domain
Group:		Networking/News
Group(pl):	Sieciowe/News
Source0:	http://home.att.net/~bobyetman/%{name}-%{version}.tar.gz
Source1:	suck.log
Patch0:		suck-config.patch
Patch1:		suck-script.patch
Patch2:		suck-perl_int.patch
Patch3:		suck-scripts.patch
Patch4:		suck-readme.patch
Provides:	news-sucker
Requires:	inn >= 2.0
Requires:	gawk
%requires_eq    perl
BuildPrereq:	perl
BuildPrereq:	inn-devel >= 2.0
URL:		http://home.att.net/~bobyetman/index.html
BuildRoot:	/tmp/%{name}-%{version}-root

%description
The primary use for suck is to feed a local INN or CNEWS server, without
the remote NNTP feeding you articles.  It is designed for a small, partial
news feed.  It is NOT designed to feed 10,000 groups and 3 Gigs of articles
a day.

Read /usr/share/doc/%{name}-%{version}/README.FIRST after installing 
this package!

%description -l pl
suck dostarcza posty lokalnemu serwerowi newsów, INN-owi albo CNEWS-owi,
przed zdalnym serwerem udaj±c zwyk³y czytnik, a wiêc bez wymagania
konfiguracji feedu z tamtej strony. Jest przeznaczony do ma³ego,
czê¶ciowego feedu. Nie jest przeznaczony dla 10000 grup i 3 GB postów
dziennie.

Przeczytaj /usr/share/doc/%{name}-%{version}/README.FIRST po zainstalowaniu
tego pakietu!

%prep
%setup -q
%patch0 -p0
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
PERL_CORE_PLD="`perl -MConfig -e 'print $Config{archlib}'`/CORE"
export PERL_CORE_PLD

CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="-s" \
./configure %{_target_platform} \
	--prefix=$RPM_BUILD_ROOT%{_prefix} \
	--mandir=$RPM_BUILD_ROOT%{_mandir}
make

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{etc/logrotate.d,var/state/%{name}}

make installall prefix=$RPM_BUILD_ROOT%{_prefix}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install sample/get.news.inn \
	sample/get.news.generic \
	sample/put.news \
	sample/put.news.sm \
	sample/*.pl \
	$RPM_BUILD_ROOT/var/state/%{name}
install sample/sucknewsrc.sample \
	$RPM_BUILD_ROOT/var/state/%{name}/sucknewsrc

gzip -9nf $RPM_BUILD_ROOT%{_mandir}/man1/* \
	CHANGELOG CONTENTS README README.Gui README.Xover README.FIRST \
	perl/README

%post 
if [ "$1" = 1 ]; then
  # Create initial log files so that logrotate doesn't complain
  touch /var/log/%{name}.errlog
  chown news.news /var/log/%{name}.errlog
  chmod 644 /var/log/%{name}.errlog
  touch /var/state/%{name}/%{name}.killlog
  chown news.news /var/state/%{name}/%{name}.killlog
  chmod 644 /var/state/%{name}/%{name}.killlog
fi

%preun
if [ "$1" = 0 ]; then
  # Remove current killfile log, or rpm -e will complain dir isn't empty
  rm -f /var/state/%{name}/%{name}.killlog*
fi

%postun
if [ "$1" = 0 ]; then
  # Remove suck error logs
  rm -f /var/log/%{name}.errlog*
  # Remove any old killfile logs rotated to /var/log
  rm -f /var/log/%{name}.killlog*
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc {CHANGELOG,CONTENTS,README,README.Gui,README.Xover,README.FIRST}.gz
%doc sample perl

%attr(755,root,root) %{_bindir}/*
%config /etc/logrotate.d/%{name}

%attr(775,news,news) %dir /var/state/%{name}

%config %attr(740,news,news) /var/state/%{name}/get.news.inn
%config %attr(740,news,news) /var/state/%{name}/get.news.generic
%config %attr(740,news,news) /var/state/%{name}/put.news
%config %attr(740,news,news) /var/state/%{name}/put.news.sm
%config %attr(740,news,news) /var/state/%{name}/*.pl
%config %attr(644,news,news) /var/state/%{name}/sucknewsrc

%{_mandir}/man1/*
