#!/usr/bin/env sh
# docker-compose is verreist om de webapp op te starten
echo ik veronderstel dat de dit scriptje wordt uitgevoerd op een systeem met de apt package manager en de systemd service manager
echo ik veronderstel eveneens dat de gebruiker correct gemachtigd is
apt install docker-compose
systemctl enable --now docker.service
