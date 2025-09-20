#!/bin/sh
set -ex
rpm-ostree upgrade
sudo dbus-launch flatpak uninstall --unused
sudo dbus-launch flatpak update
