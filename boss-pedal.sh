#!/usr/bin/env bash

# Really simple startup script to start the Boss-Pedal
# Just make it executable and run it on startup
# Whilst this will probably meet most users requirements, I recommend using Supervisor for better resilience

# Adjust this directory depending on your install directory
cd /home/doggy/src/prog/

/home/doggy/src/env/bin/python app.py
