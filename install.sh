#!/usr/bin/env sh
# docker-compose is verreist om de webapp op te starten
# ik veronderstel dat de dit scriptje wordt uitgevoerd op een systeem met de apt package manager
# ik veronderstel eveneens dat de gebruiker correct gemachtigd is
apt install docker-compose
systemctl enable --now docker.service
