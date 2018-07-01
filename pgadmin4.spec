%global debug_package %{nil}
Name:    pgadmin4
Version: 3.0
Release: 1%{?dist}
Summary: Management tool for PostgreSQL
License: PostgreSQL
URL:     https://www.pgadmin.org
Source0: https://download.postgresql.org/pub/pgadmin/pgadmin4/v%{version}/source/pgadmin4-%{version}.tar.gz
Source1: pgadmin4.conf
Source2: pgadmin4.service.in
Source3: pgadmin4.tmpfiles.d
Source4: pgadmin4.desktop.in
Source6: pgadmin4.qt.conf.in

BuildRequires: systemd
%{?systemd_requires}

BuildRequires: python3-sphinx
BuildRequires: python3-passlib python3-flask-mail python3-flask-migrate
BuildRequires: python3-dateutil python3-flask-gravatar
BuildRequires: python3-simplejson python3-flask-babel python3-flask-babelex
BuildRequires: python3-flask-htmlmin python3-flask-login
BuildRequires: python3-flask-security python3-flask-principal
BuildRequires: python3-flask-wtf python3-flask python3-fixtures
BuildRequires: python3-itsdangerous python3-blinker python3-flask-sqlalchemy
BuildRequires: python3-dateutil python3-flask-paranoid
BuildRequires: python3-devel python3-extras

%description
pgAdmin 4 is a rewrite of the popular pgAdmin3 management tool for the
PostgreSQL (http://www.postgresql.org) database.

pgAdmin 4 is written as a web application in Python, using jQuery and
Bootstrap for the client side processing and UI. On the server side,
Flask is being utilised.

Although developed using web technologies, we intend for pgAdmin 4 to
be usable either on a web server using a browser, or standalone on a
workstation. The runtime/ subdirectory contains a QT based runtime
application intended to allow this - it is essentially a browser and
Python interpretor in one package which will be capable of hosting the
Python application and presenting it to the user as a desktop
application.

Summary: pgAdmin4 web application
Requires: %{name}-docs
Requires: python3-babel python3-flask python3-flask-babelex
Requires: python3-flask-htmlmin
Requires: python3-flask-sqlalchemy
Requires: python3-flask-wtf
Requires: python3-jinja2 python3-markupsafe
Requires: python3-sqlalchemy
Requires: python3-wtforms
Requires: python3-beautifulsoup4
Requires: python3-blinker  python3-html5lib
Requires: python3-itsdangerous
Requires: python3-psycopg2
Requires: python3-six python3-crypto
Requires: python3-simplejson python3-dateutil
Requires: python3-werkzeug python3-sqlparse
Requires: python3-flask-babel python3-passlib
Requires: python3-flask-gravatar
Requires: python3-flask-mail
Requires: python3-flask-security
Requires: python3-flask-login
Requires: python3-flask-paranoid
Requires: python3-flask-principal
Requires: pytz python3-click
Requires: python3-fixtures
Requires: python3-pyrsistent python3-flask-migrate
Requires: python3-mimeparse python3-speaklater
Requires: python3-unittest2
Requires: httpd
Requires: python3
Requires: python3-mod_wsgi
Requires: python3-extras

%package desktop
Summary:  pgAdmin4 desktop application
BuildRequires: gcc-c++
BuildRequires: qt5-qtbase-devel
BuildRequires: qt5-qtwebkit-devel qt5-qtwebengine-devel
Requires: qt
Requires: qt5-qtwebengine

%description desktop
This package contains the required files to run pgAdmin4 as a desktop application

%package docs
Summary:  pgAdmin4 documentation
BuildArch: noarch

%description docs
Documentation of pgadmin4.

%prep
%setup -q -n %{name}-%{version}

%build
pushd runtime
export PYTHON_CONFIG=/usr/bin/python3-config
export PYTHONPATH=%{python3_sitelib}/pgadmin-web/:$PYTHONPATH
%{qmake_qt5} -o Makefile pgAdmin4.pro
make
popd

make PYTHON=/usr/bin/python3 SPHINXBUILD=/usr/bin/sphinx-build-3 docs

%install
%{__install} -d -m 755 %{buildroot}%{_docdir}/%{name}-docs/en_US/html
%{__cp} -pr docs/en_US/_build/html/* %{buildroot}%{_docdir}/%{name}-docs/en_US/html/

%{__install} -Dpm 0755 runtime/pgAdmin4 %{buildroot}%{_bindir}/pgAdmin4

%{__install} -d -m 755 %{buildroot}%{_datadir}/%{name}
%{__cp} -pR web/* %{buildroot}%{_datadir}/%{name}

# Install Apache sample config file
%{__install} -d %{buildroot}%{_sysconfdir}/httpd/conf.d/
%{__sed} -e 's@PYTHONSITELIB@%{python3_sitelib}@g' < %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

# Install desktop file, and its icon
%{__install} -d -m 755  %{buildroot}%{_datadir}/%{name}/pgadmin/static/img/
%{__install} -m 755 runtime/pgAdmin4.ico %{buildroot}%{_datadir}/%{name}/pgadmin/static/img/
%{__install} -d %{buildroot}%{_datadir}/applications/
%{__sed} -e 's@PYTHONDIR@%{__ospython}@g' -e 's@PYTHONSITELIB@%{python3_sitelib}@g' < %{SOURCE4} > %{buildroot}%{_datadir}/applications/%{name}.desktop

# Install QT conf file.
# Directories are different on RHEL 7 and Fedora 24+.
# Fedora 24+
%{__install} -d "%{buildroot}%{_sysconfdir}/xdg/pgadmin/"
%{__sed} -e 's@PYTHONSITELIB@%{python3_sitelib}@g'<%{SOURCE6} > "%{buildroot}%{_sysconfdir}/xdg/pgadmin/%{name}.conf"

# Install systemd service file
%{__install} -Dpm 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service

# ... and make a tmpfiles script to recreate it at reboot.
%{__install} -Dpm 0644 %{SOURCE3} %{buildroot}/%{_tmpfilesdir}/%{name}.conf

pushd %{buildroot}%{_datadir}/%{name}
%{__rm} -f %{name}.db
echo "HELP_PATH = '/usr/share/doc/%{name}-docs/en_US/html'" > config_distro.py
popd

%post
%tmpfiles_create

%files
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %{_datadir}/%{name}
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf
%{_datadir}/%{name}/*

%files desktop
%{_bindir}/pgAdmin4
%{_datadir}/applications/%{name}.desktop
%{_sysconfdir}/xdg/pgadmin/%{name}.conf

%files docs
%doc %{_docdir}/%{name}-docs/*

%changelog

