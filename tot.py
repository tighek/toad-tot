
#
# Trunk or Treat Automation
# Copyright 2015 Tighe Kuykendall
#
# We are going to automate a bean bag toss game so that:
#  - It has 6 doors.
#  - Doors will be randomized so that 3 doors shoot candy and 3 doors shoot water.
#  - If 2 water doors are opened the next door will be candy.
#
# There is a web interface for:
#  - Reseting the sensors for a new person
#  - Making all doors shoot candy for the little kids.
#  - Making all doors shoot water for kids that keep coming back.
#  - Lock-out to stop all candy and water activities.
#
# This toad house originally debuted at the Pinewood Preparatory School Trunk or Treat
# in 2014.  That version had 2 doors which where wired directly to the candy cannons.
# It was a pretty simple game and the kids learned which doors would fire candy.  Some
# of the older kids also learned that if they stood in the right spot they could catch
# candy from the smaller kids which had to stand closer to the game.
#
# We are back in 2015 with this new and improved version!
#

import RPi.GPIO as GPIO
import time
import random
import sys


def setup_channels():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(doors.get('door1'), GPIO.IN)
    GPIO.setup(doors.get('door2'), GPIO.IN)
    GPIO.setup(doors.get('door3'), GPIO.IN)
    GPIO.setup(doors.get('door4'), GPIO.IN)
    GPIO.setup(doors.get('door5'), GPIO.IN)
    GPIO.setup(doors.get('door6'), GPIO.IN)
    GPIO.setup(tubes.get('tube1'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube2'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube3'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube4'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube5'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tubes.get('tube6'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(sprayers.get('spray1'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(bells.get('bell1'), GPIO.OUT, initial=GPIO.HIGH)
#    GPIO.setup(right_button, GPIO.IN, GPIO.PUD_UP)
#    GPIO.setup(left_button, GPIO.IN, GPIO.PUD_UP)
    return


def ring_bell(bell_num):
    print ("Ring")
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


def fire_candy(w_cnt, c_cnt, w_tb, c_tb):

    if 1 <= c_tb <= 5 and c_cnt < 2:
        c_cnt += 1
        fire_tube(tubes.get("tube"+str(c_tb)))
        print ("Candy"),
        print ("w_cnt: %s" % w_cnt),
        print ("c_cnt: %s" % c_cnt),
        print ("c_tb: %s" % c_tb),
        c_tb += 1
    elif c_tb == 6 and c_cnt < 2:
        c_cnt += 1
        fire_tube(tubes.get("tube"+str(c_tb)))
        print ("Candy"),
        print ("w_cnt: %s" % w_cnt),
        print ("c_cnt: %s" % c_cnt),
        print ("c_tb: %s" % c_tb),
        ring_bell(bells.get('bell1'))
        c_tb = 1
        w_cnt = 0
    else:
        c_cnt = 0
        print ("Candy Else"),
        print ("w_cnt: %s" % w_cnt),
        print ("c_cnt: %s" % c_cnt),
        print ("c_tb: %s" % c_tb),
        w_cnt, c_cnt, w_tb, c_tb = fire_water(w_cnt, c_cnt, w_tb, c_tb)
    return w_cnt, c_cnt, w_tb, c_tb


def fire_water(w_cnt, c_cnt, w_tb, c_tb):
    if w_tb == 1 and w_cnt <= 2:
        w_cnt += 1
        spray_water(sprayers.get("spray"+str(w_tb)))
        print ("Water"),
        print ("w_cnt: %s" % w_cnt),
        print ("c_cnt: %s" % c_cnt),
        print ("c_tb: %s" % c_tb)
        w_tb = 1
    else:
        w_cnt = 0
        print ("Water Else"),
        w_cnt, c_cnt, w_tb, c_tb = fire_candy(w_cnt, c_cnt, w_tb, c_tb)
    return w_cnt, c_cnt, w_tb, c_tb


def startup():
    print ("Setup Channels")
    setup_channels()
    check_tube = 1
    while check_tube < 7:
        fire_tube(tubes.get("tube"+str(check_tube)))
        check_tube += 1
    check_spray = 1
    while check_spray < 2:
        spray_water(sprayers.get("spray"+str(check_spray)))
        check_spray += 1
    check_bell = 1
    while check_bell < 2:
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


#door1 = 14
#door2 = 15
#door3 = 18
#door4 = 23
#door5 = 24
#door6 = 25
#tube1 = 2
#tube2 = 3
#tube3 = 4
#tube4 = 17
#tube5 = 27
#tube6 = 22
#spray1 = 10
#bell = 9

tubes = {'tube1': 2, 'tube2': 3, 'tube3': 4, 'tube4': 17, 'tube5': 27, 'tube6': 22}
doors = {'door1': 14, 'door2': 15, 'door3': 18, 'door4': 24, 'door5': 24, 'door6': 25}
sprayers = {'spray1': 10}
bells = {'bell1': 9}

#
# Startup and initialize everything.
#

print ("Startup Routine")
startup()


try:

    water, candy = randomize_tubes()

    print ("Water Tubes: %s" % water)
    print ("Candy Tubes: %s" % candy)

    w_count = 0
    c_count = 0
    w_tube = 1
    c_tube = 1

    while True:

        n = int(input("\n\n1,2,3,4,5,6?: "))
        if n == 1:
            if 1 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 1 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
#        elif GPIO.input(door1) == True:
#            if 1 in candy:
#                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
#            elif 1 in water:
#                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif n == 2:
            if 2 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 2 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif n == 3:
            if 3 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 3 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif n == 4:
            if 4 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 4 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif n == 5:
            if 5 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 5 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif n == 6:
            if 6 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 6 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif n == 0:
            print ("Else")
            break



#	while True:
#
#		if GPIO.input(door1) == False:
#			if 1 in candy:
#				fire_tube1()
#			elif 1 in water:
#				fire_tube2()
#		elif GPIO.input(door2) == False:
#			if 2 in candy:
#				fire_tube3()
#			elif 2 in water:
#				fire_tube2()
#			else:
#				flash_led()
#				randomize_tubes()


# while True:
#    if GPIO.input(left_button) == False:
#            print("Left button pressed")
#            break
#        if GPIO.input(right_button) == False:
#            print("Right button pressed")
#            break

except Exception, err:
    print "Exception:", str(err)
    import traceback, sys
    print '-'*60
    traceback.print_exc(file=sys.stdout)
    print '-'*60

#except ValueError:
#    print('Sample size exceeded population size.')







