
#
# Trunk or Treat Automation
# Copyright 2015 Tighe Kuykendall
# All rights reserved under the Apache 2.0 License
#
# See http://github.com/tighek/toad-tot
#
#
#  Version 1.1
#  - 
#
#  Version 1.0
#  - All 6 doors create an action
#  - Doors will be randomized so that 4 doors deliver candy and 2 doors deliver water.
#  - If 2 water doors are opened consecutively the next door will be candy.
#  - If 2 candy doors are opened consecutively the next door will be water.
#  - When the 6th candy tube is used, ring a bell so we know to reload.
#  - There are 3 switches concealed beside the automation gear:
#    + Switch #1 resets the counters, randomizes the doors, and effectively starts the
#      game for a new player.
#    + Switch #2 sets all doors to dispense candy.  This is for the little kids.
#    + Switch #3 sets all doors to dispense water.  This is for the older kids that
#      coming back for candy...
#

import RPi.GPIO as GPIO
import time
import random
import sys
import optparse
import os


def setup_channels():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(doors.get('door1'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(doors.get('door2'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(doors.get('door3'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(doors.get('door4'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(doors.get('door5'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(doors.get('door6'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(buttons.get('reset'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(buttons.get('candy_only'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(buttons.get('water_only'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(tubes.get('tube1'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube2'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube3'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube4'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube5'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube6'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(sprayers.get('spray1'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(bells.get('bell1'), GPIO.OUT, initial=GPIO.HIGH)
    return


def ring_bell(bell_num):
    GPIO.output(bell_num, 0)
    time.sleep(1)
    GPIO.output(bell_num, 1)
    return


def fire_tube(tb):
    GPIO.output(tb, 0)
    time.sleep(.5)
    GPIO.output(tb, 1)
    return


def spray_water(tb):
    GPIO.output(tb, 0)
    time.sleep(.5)
    GPIO.output(tb, 1)
    return


def randomize_tubes():
    rand_water = random.sample(range(1, 7), 2)
    w1 = rand_water[0]
    w2 = rand_water[1]
    rand_candy = list(range(1, 7))
    rand_candy.remove(w1)
    rand_candy.remove(w2)
    return rand_water, rand_candy


def fire_candy(w_cnt, c_cnt, w_tb, c_tb, n_tubes, n_sprayers):
    if candy_tube_only == 1 and c_tb < n_tubes:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        c_cnt = 0
        fire_tube(tubes.get("tube"+str(c_tb)))
        c_tb += 1
    elif candy_tube_only == 1 and c_tb == n_tubes:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        c_cnt = 0
        fire_tube(tubes.get("tube"+str(c_tb)))
        ring_bell(bells.get('bell1'))
        c_tb = 1
    if 1 <= c_tb <= n_tubes-1 and c_cnt < 2:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        c_cnt += 1
        fire_tube(tubes.get("tube"+str(c_tb)))
        c_tb += 1
    elif c_tb == n_tubes and c_cnt < 2:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        c_cnt += 1
        fire_tube(tubes.get("tube"+str(c_tb)))
        ring_bell(bells.get('bell1'))
        c_tb = 1
        w_cnt = 0
    else:
        c_cnt = 0
        w_cnt, c_cnt, w_tb, c_tb = fire_water(w_cnt, c_cnt, w_tb, c_tb, n_tubes, n_sprayers)
    return w_cnt, c_cnt, w_tb, c_tb


def fire_water(w_cnt, c_cnt, w_tb, c_tb, n_tubes, n_sprayers):
    if water_spray_only == 1:
        tot_water_metrics = open('tot_water_metrics', 'a')
        tot_water_metrics.write('1')
        tot_water_metrics.close()
        spray_water(sprayers.get("spray"+str(w_tb)))
        w_tb = 1
    elif w_tb == 1 and w_cnt <= 2:
        tot_water_metrics = open('tot_water_metrics', 'a')
        tot_water_metrics.write('1')
        tot_water_metrics.close()
        w_cnt += 1
        spray_water(sprayers.get("spray"+str(w_tb)))
        w_tb = 1
    else:
        w_cnt = 0
        w_cnt, c_cnt, w_tb, c_tb = fire_candy(w_cnt, c_cnt, w_tb, c_tb, n_tubes, n_sprayers)
    return w_cnt, c_cnt, w_tb, c_tb


def reset_counters(w_cnt, c_cnt, w_tb, c_tb):
    w_cnt = 0
    c_cnt = 0
    w_tb = 0
    c_tb = 0
    return w_cnt, c_cnt, w_tb, c_tb


def startup():
    print ("Setup Channels")
    setup_channels()
    check_tube = 1
    while check_tube < num_tubes+1:
        fire_tube(tubes.get("tube"+str(check_tube)))
        check_tube += 1
    check_spray = 1
    while check_spray < num_sprayers+1:
        spray_water(sprayers.get("spray"+str(check_spray)))
        check_spray += 1
    check_bell = 1
    while check_bell < num_bells+1:
        ring_bell(bells.get("bell"+str(check_bell)))
        check_bell += 1
    return


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

num_tubes = len(tubes)
num_doors = len(doors)
num_sprayers = len(sprayers)
num_bells = len(bells)
num_buttons = len(buttons)


#
# Startup and initialize everything.
#

print ("Startup Routine")
startup()


if __name__ == "__main__":

  try:

      parser = optparse.OptionParser()
      parser.add_option('-l', '--local', action="store_const", const="local", dest="run_mode")
      parser.add_option('-s', '--sensor', action="store_const", const="sensor", dest="run_mode")
      parser.add_option('-a', '--action', action="store_const", const="action", dest="run_mode")
      (options, args) = parser.parse_args()

      water, candy = randomize_tubes()

      print ("Water Tubes: %s" % water)
      print ("Candy Tubes: %s" % candy)

      water_spray_only = 0
      candy_tube_only = 0

      w_count = 0
      c_count = 0
      w_tube = 1
      c_tube = 1

      while True:

          if GPIO.input(buttons.get('water_only')) == False and GPIO.input(buttons.get('candy_only')) == False:
              ring_bell(bells.get('bell1'))
              time.sleep (60)
          elif GPIO.input(doors.get('door1')) == False:
              if water_spray_only == 1:
                  w_cnt = 0
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
              elif candy_tube_only == 1:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 1 in candy:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 1 in water:
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
          elif GPIO.input(doors.get('door2')) == False:
              if water_spray_only == 1:
                  w_cnt = 0
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
              elif candy_tube_only == 1:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 2 in candy:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 2 in water:
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
          elif GPIO.input(doors.get('door3')) == False:
              if water_spray_only == 1:
                  w_cnt = 0
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
              elif candy_tube_only == 1:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 3 in candy:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 3 in water:
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
          elif GPIO.input(doors.get('door4')) == False:
              if water_spray_only == 1:
                  w_cnt = 0
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
              elif candy_tube_only == 1:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 4 in candy:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 4 in water:
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
          elif GPIO.input(doors.get('door5')) == False:
              if water_spray_only == 1:
                  w_cnt = 0
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
              elif candy_tube_only == 1:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 5 in candy:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 5 in water:
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
          elif GPIO.input(doors.get('door6')) == False:
              if water_spray_only == 1:
                  w_cnt = 0
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
              elif candy_tube_only == 1:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 6 in candy:
                  w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
              elif 6 in water:
                  w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
          elif GPIO.input(buttons.get('reset')) == False:
              reset_counters(w_count, c_count, w_tube, c_tube)
          elif GPIO.input(buttons.get('water_only')) == False:
              water_spray_only = 1
          elif GPIO.input(buttons.get('water_only')) == True:
              water_spray_only = 0
          elif GPIO.input(buttons.get('candy_only')) == False:
              candy_tube_only = 1
          elif GPIO.input(buttons.get('candy_only')) == True:
              candy_tube_only = 0


  except Exception, err:
      print "Exception:", str(err)
      import traceback, sys
      print '-'*60
      traceback.print_exc(file=sys.stdout)
      print '-'*60


#except ValueError:
#    print('Sample size exceeded population size.')
