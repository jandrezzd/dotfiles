#!/bin/bash

# Opciones del menú:
options="Lock\n Suspend\n Reboot\n Power off"

# Mostrar el menú con tofi y guardar la selección
choice=$(echo -e "$options" | tofi --prompt "Power Menu: ")

case "$choice" in
	"Lock")
	hyprlock
	;;
	"Suspend")
	systemctl suspend
	;;
	"Reboot")
	systemctl reboot
	;;
	"Power off")
	systemctl poweroff
	;;
esac
