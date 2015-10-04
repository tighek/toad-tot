# config.py
#
# Configuration file for Toad Trunk-or-Treat
#
#
# If running in Local mode, the following ACTION items are ignored.  If running
# in Action or Sensor mode, set the following:
#
#   ACTION_IP is the IP address of the RPi controlling actions.
#   ACTION_PORT is the TCP port the Action server will listen on.
#

ACTION_IP="172.16.10.14"
ACTION_PORT=30303

SOUND_RESET="sounds/reset.wav"
SOUND_SUCCESS="sounds/success.wasv"
SOUND_RELOAD="sounds/reload.wav"
SOUND_FAIL="sounds/fail.wav"

#
# Define the RPi board channels for the inputs and outputs.
#
# Raspberry Pi Mod A and Mod B GPIO Pinout
# GG = Ground, 5v = +5 volt, 3v = +3 volt
#
# [5v] [5v] [GG] [14] [15] [18] [GG] [23] [24] [GG] [25] [ 8] [ 7]
# [3v] [ 2] [ 3] [ 4] [GG] [17] [27] [22] [3v] [10] [ 9] [11] [GG]
#

tubes = {'tube1': 2, 'tube2': 3, 'tube3': 4, 'tube4': 17, 'tube5': 27, 'tube6': 22}
doors = {'door1': 14, 'door2': 15, 'door3': 18, 'door4': 23, 'door5': 24, 'door6': 25}
sprayers = {'spray1': 10}
bells = {'bell1': 9}
buttons = {'reset': 8, 'water_only': 7, 'candy_only': 11}

