Summary:	suck receives/sends news via NNTP
Summary(pl):	suck odbiera i wysy³a newsy przez NNTP
Name:		suck
Version:	4.1.2
Release:	2
Copyright:	Public Domain
Group:		Networking/News
Group(pl):	Sieciowe/News
Source0:	http://home.att.net/~bobyetman/%{name}-%{version}.tar.gz
Source1:	suck.log
Source2:	suck-README.FIRST.gz
Patch0:		suck-makefile.patch
Patch1:		suck-script.patch
Patch2:		suck-config.patch
Patch3:		suck-perl_int.patch
Patch4:		suck-scripts.patch
Provides:	news-sucker
Requires:	inn >= 2.0
Requires:	perl
Requires:	gawk
URL:		http://home.att.net/~bobyetman/index.html
BuildRoot:	/tmp/%{name}-%{version}-root

%description
The primary use for suck is to feed a local INN or CNEWS server, without
the remote NNTP feeding you articles.  It is designed for a small, partial
news feed.  It is NOT designed to feed 10,000 groups and 3 Gigs of articles
a day.

Read /usr/doc/%{name}-%{version}/README.FIRST after installing this package!

%description -l pl
suck dostarcza posty lokalnemu serwerowi newsów, INN-owi albo CNEWS-owi,
przed zdalnym serwerem udaj±c zwyk³y czytnik, a wiêc bez wymagania
konfiguracji feedu z tamtej strony. Jest przeznaczony do ma³ego,
czê¶ciowego feedu. Nie jest przeznaczony dla 10000 grup i 3 GB postów
dziennie.

Przeczytaj /usr/doc/%{name}-%{version}/README.FIRST po zainstalowaniu
tego pakietu!

%prep
%setup -q
cp %{SOURCE2} README.FIRST.gz
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
PERL_CORE_PLD="`perl -MConfig -e 'print $Config{archlib}'`/CORE"
export PERL_CORE_PLD

CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="-s" \
./configure %{_target} \
	--prefix=$RPM_BUILD_ROOT/usr

make

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{etc/logrotate.d,var/lib/suck}

make install prefix=$RPM_BUILD_ROOT/usr

install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/suck
install sample/get.news.inn \
	sample/get.news.generic \
	sample/put.news \
	sample/put.news.sm \
	$RPM_BUILD_ROOT/var/lib/suck
install sample/sucknewsrc.sample \
	$RPM_BUILD_ROOT/var/lib/suck/sucknewsrc

gzip -9nf $RPM_BUILD_ROOT/usr/man/man1/* \
	CHANGELOG CONTENTS README README.Gui README.Xover

%post 
if [ "$1" = 1 ]; then
  # Create initial log files so that logrotate doesn't complain
  touch /var/log/suck.errlog
  chown news.news /var/log/suck.errlog
  chmod 644 /var/log/suck.errlog
  touch /var/lib/suck/suck.killlog
  chown news.news /var/lib/suck/suck.killlog
  chmod 644 /var/lib/suck/suck.killlog
fi

%preun
if [ "$1" = 0 ]; then
  # Remove current killfile log, or rpm -e will complain dir isn't empty
  rm -f /var/lib/suck/suck.killlog*
fi

%postun
if [ "$1" = 0 ]; then
  # Remove suck error logs
  rm -f /var/log/suck.errlog*
  # Remove any old killfile logs rotated to /var/log
  rm -f /var/log/suck.killlog*
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc {CHANGELOG,CONTENTS,README,README.Gui,README.Xover,README.FIRST}.gz
%doc sample

%attr(755,root,root) /usr/bin/*
%config /etc/logrotate.d/suck

%attr(775,news,news) %dir /var/lib/suck

%config %attr(740,news,news) /var/lib/suck/get.news.inn
%config %attr(740,news,news) /var/lib/suck/get.news.generic
%config %attr(740,news,news) /var/lib/suck/put.news
%config %attr(740,news,news) /var/lib/suck/put.news.sm
%config %attr(644,news,news) /var/lib/suck/sucknewsrc

/usr/man/man1/*

%changelog
* Mon Apr 19 1999 Piotr Czerwiñski <pius@pld.org.pl>
  [4.1.2-2]
- recompiled on new rpm.

* Thu Apr 15 1999 Piotr Czerwiñski <pius@pld.org.pl>
  [4.1.2-1]
- updated to 4.1.2,
- added Group(pl),
- changed Buildroot to /tmp/%{name}-%{version}-root,
- removed man group from man pages,
- patches rewritten for new version,
- added detection of PERL_CORE directory,
- many changes in %build, %install and %files,
- added gzipping documentation,
- added Requires: inn >= 2.0,
- added some %requires_pkg macros,
- added new README.FIRST file,
- cosmetics.

* Sat Nov 28 1998 Marcin 'Qrczak' Kowalczyk <qrczak@knm.org.pl>
  [3.10.2-1]
- PERL_CORE path changed to /usr/lib/perl5/5.00502/i386-linux-thread/CORE,
- -lpthread added to PERL_LIB,
- suck-perl_int.patch fixes a bug,
- /usr/lib/suck moved into /var/lib/suck,
- added pl translation,
- `mkdir -p' replaced with more standard `install -d',
- suck-scripts.patch fixes a bug in put.news and makes get.news.innxmit,
  downloading and uploading simultaneously,
- added full %attr description in %files,
- added %setup -q parameter,
- don't install sample/suckkillfile.sample as /var/lib/suck/suckkillfile.

* Wed Oct 15 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.10.1

* Wed Oct 7 1998  Ian Macdonald <ianmacd@xs4all.nl>
- compiled in Perl filter support

* Mon Oct 5 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.10.0

* Mon Jul 27 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.4
- Now requires inn < 2.0

* Sat May 23 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.4A

* Fri Apr 24 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.3

* Mon Mar 30 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.2
- Removed reference to README.killfiles (it's gone - a mistake?)

* Wed Mar 4 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.2D

* Mon Mar 2 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.2C

* Sun Feb 22 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.2B
- Split patch into make, script and config patches to ease upgrading

* Sun Feb 15 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Moved the package back to /usr from /usr/local

* Fri Feb 13 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.1

* Fri Feb 6 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.9.0
- Removed '-D_POSIX_SOURCE -D_BSD_SOURCE' from CFLAGS (no longer required)
- Changed 'nocompress' parameter for logrotate to 'delaycompress'
- Virtual package provision changed to 'news-puller'
- Post-uninstall script will now only run on package erasure (not upgrade)

* Thu Jan 15 1998  Ian Macdonald <ianmacd@xs4all.nl>
- Upgraded to 3.8.0
- Changed root for binaries from /usr to /usr/local
- Changed paths in sample scripts to be Red Hat INN compliant
- Added package dependencies
- Added missing doc file README.killfiles
- Changed dir for temp files to /tmp
- Changed dir for suck.errlog to /var/log
- Extended logrotate script to cover suck.killlog
- Removed lpost man page (obsolete)

* Mon Sep 15 1997  Jani Hakala <jahakala@cc.jyu.fi>
- Upgraded to v3.6.0

* Sun Sep 7 1997  Jani Hakala <jahakala@cc.jyu.fi>
- Built against glibc
- Added '-D_POSIX_SOURCE -D_BSD_SOURCE' to CFLAGS because of glibc.
- Can be built as ordinary user.

* Mon Sep 1 1997 Karsten Weiss <karsten@addx.au.s.shuttle.de>
- Ugraded package to suck-3.5.2.

* Fri Jun 20 1997 Karsten Weiss <karsten@addx.au.s.shuttle.de>
- Ugraded package to suck-3.5.1.

* Sat Jun 7 1997 Karsten Weiss <karsten@addx.au.s.shuttle.de>
- Decided to install the sample config files by default as this is
  no problem anymore thanks to Builroot.
- Forgot to kill the .orig files... Fixed!
- Fixed a mistake in the path of the description text below.

* Fri Jun 6 1997 Karsten Weiss <karsten@addx.au.s.shuttle.de>
- Buildrooted.
- logrotate support
- Included README.FIRST text.

* Wed Jun 4 1997 Karsten Weiss <karsten@addx.au.s.shuttle.de>
- Created this spec file.
