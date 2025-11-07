%global debug_package %{nil}
Name:           syncthing
Version:        2.0.11
Release:        1
Summary:        Continuous File Synchronisation
# syncthing (MPL-2.0) bundles
# - angular, bootstrap, daterangepicker, fancytree, jQuery, moment (MIT),
# - HumanizeDuration (MIT OR Unlicense),
# - ForkAwesome (MIT, OFL-1.1, CC-BY-3.0), and
# - a number of go packages (Apache-2.0, BSD-2-Clause, BSD-2-Clause-Views, BSD-3-Clause, ISC, MIT, MPL-2.0)
License:        MPL-2.0 AND Apache-2.0 AND BSD-2-Clause AND BSD-2-Clause-Views AND BSD-3-Clause AND CC-BY-3.0 AND ISC AND MIT AND OFL-1.1 AND (Apache-2.0 OR MIT) AND (MIT OR Unlicense)
Group:          Productivity/Networking/File-Sharing
URL:            https://syncthing.net/
Source:         https://github.com/%{name}/%{name}/releases/download/v%{version}/%{name}-source-v%{version}.tar.gz


BuildRequires:  golang
BuildRequires:  desktop-file-utils
BuildRequires:  systemd-rpm-macros

Requires:       hicolor-icon-theme

%description
Syncthing replaces other file synchronization services with something
open, trustworthy and decentralized. Your data is your data alone and
you deserve to choose where it is stored, if it is shared with some
third party and how it's transmitted over the Internet. Using Syncthing,
that control is returned to you.

This package contains the syncthing client binary and systemd services.

%package        tools
Summary:        Continuous File Synchronization (server tools)

%description    tools
Syncthing replaces other file synchronization services with something
open, trustworthy and decentralized. Your data is your data alone and
you deserve to choose where it is stored, if it is shared with some
third party and how it's transmitted over the Internet. Using Syncthing,
that control is returned to you.

This package contains the main syncthing server tools:

* strelaysrv / strelaypoolsrv, the syncthing relay server for indirect
  file transfers between client nodes, and
* stdiscosrv, the syncthing discovery server for discovering nodes
  to connect to indirectly over the internet.


%prep
%autosetup -n %{name} -p1

%build
# move source archive which is extracted as "syncthing" to be "src/github.com/syncthing/syncthing"
pushd ..
install -d "src/github.com/syncthing/"
mv %{name} "src/github.com/syncthing/"%{name}
mkdir syncthing
cd "$PWD/src/github.com/syncthing/"%{name}

# set build environment, in particular use "-mod=vendor" to use the Go modules from the source archive's vendor dir
export BUILD_USER=abf BUILD_HOST=OpenMandriva
export CGO_CPPFLAGS="${CPPFLAGS}" CGO_CFLAGS="${CFLAGS}" CGO_CXXFLAGS="${CXXFLAGS}" CGO_LDFLAGS="${LDFLAGS}"
export GOFLAGS="-trimpath -mod=vendor"

# build and install syncthing without automatic updates
go run build.go -no-upgrade -version v%{version} install
# build and install strelaysrv without automatic updates
go run build.go -no-upgrade -version v%{version} install strelaysrv
# build and install strelaypoolsrv without automatic updates
go run build.go -no-upgrade -version v%{version} install strelaypoolsrv
# build and install stdiscosrv without automatic updates
go run build.go -no-upgrade -version v%{version} install stdiscosrv
popd

%install
st_dir=$PWD
cd ../src/github.com/syncthing/%{name}
mv LICENSE AUTHORS CONDUCT.md CONTRIBUTING.md README.md "$st_dir"
install -Dpm 0755 bin/%{name} %{buildroot}%{_bindir}/%{name}
install -Dpm 0755 bin/stdiscosrv %{buildroot}%{_bindir}/stdiscosrv
install -Dpm 0755 bin/strelaysrv %{buildroot}%{_bindir}/strelaysrv
install -dm 0750 %{buildroot}/%{_localstatedir}/lib/syncthing-relaysrv
install -Dpm 0644 cmd/stdiscosrv/etc/linux-systemd/stdiscosrv.service \
  %{buildroot}%{_unitdir}/stdiscosrv.service
install -Dpm 0644 cmd/strelaysrv/etc/linux-systemd/strelaysrv.service \
  %{buildroot}%{_unitdir}/strelaysrv.service
install -Dpm 0755 bin/strelaypoolsrv %{buildroot}%{_bindir}/strelaypoolsrv
install -Dpm 0644 etc/linux-systemd/system/%{name}@.service        \
  %{buildroot}%{_unitdir}/%{name}@.service
install -Dpm 0644 etc/linux-systemd/user/%{name}.service           \
  %{buildroot}%{_userunitdir}/%{name}.service
# install desktop files and icons
mkdir -p %{buildroot}/%{_datadir}/applications
cp -pav etc/linux-desktop/syncthing-start.desktop %{buildroot}/%{_datadir}/applications/
cp -pav etc/linux-desktop/syncthing-ui.desktop %{buildroot}/%{_datadir}/applications/

for size in 32 64 128 256 512; do
    mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/${size}x${size}/apps
    cp -pav assets/logo-${size}.png %{buildroot}/%{_datadir}/icons/hicolor/${size}x${size}/apps/syncthing.png
done
mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/scalable/apps
cp -pav assets/logo-only.svg %{buildroot}/%{_datadir}/icons/hicolor/scalable/apps/syncthing.svg

mkdir -p %{buildroot}/%{_mandir}/man1
mkdir -p %{buildroot}/%{_mandir}/man5
mkdir -p %{buildroot}/%{_mandir}/man7
cp -pav ./man/syncthing.1 %{buildroot}/%{_mandir}/man1/
cp -pav ./man/*.5 %{buildroot}/%{_mandir}/man5/
cp -pav ./man/*.7 %{buildroot}/%{_mandir}/man7/
cp -pav ./man/stdiscosrv.1 %{buildroot}/%{_mandir}/man1/
cp -pav ./man/strelaysrv.1 %{buildroot}/%{_mandir}/man1/


%post
%systemd_post syncthing@.service
%systemd_user_post syncthing.service

%preun
%systemd_preun syncthing@.service
%systemd_preun syncthing.service

%post tools
%systemd_post strelaysrv.service
%systemd_post stdiscosrv.service

%preun tools
%systemd_preun strelaysrv.service
%systemd_preun stdiscosrv.service

%files
%license LICENSE
%doc README.md AUTHORS

%{_bindir}/syncthing

%{_datadir}/applications/syncthing*.desktop
%{_datadir}/icons/hicolor/*/apps/syncthing.*

%{_mandir}/*/syncthing*

%{_unitdir}/syncthing@.service
%{_userunitdir}/syncthing.service


%files tools
%license LICENSE
%doc README.md AUTHORS

%{_bindir}/stdiscosrv
%{_bindir}/strelaysrv
%{_bindir}/strelaypoolsrv

%{_unitdir}/strelaysrv.service
%{_unitdir}/stdiscosrv.service

%{_mandir}/man1/stdiscosrv*
%{_mandir}/man1/strelaysrv*
%changelog
