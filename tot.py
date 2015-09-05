
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
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(door1, GPIO.IN)
    GPIO.setup(door2, GPIO.IN)
    GPIO.setup(door3, GPIO.IN)
    GPIO.setup(door4, GPIO.IN)
    GPIO.setup(door5, GPIO.IN)
    GPIO.setup(tube1, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tube2, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(tube3, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(led, GPIO.OUT, initial=GPIO.HIGH)
#	GPIO.setup(right_button, GPIO.IN, GPIO.PUD_UP)
#	GPIO.setup(left_button, GPIO.IN, GPIO.PUD_UP)
    return


def flash_led():
    flash = 0
    while flash < 2:
        GPIO.output(led, 1)
        time.sleep(1)
        GPIO.output(led, 0)
        flash += 1
    return


def fire_tube1():
    GPIO.output(tube1, 1)
    time.sleep(1)
    GPIO.output(tube1, 0)
    return


def fire_tube2():
    GPIO.output(tube2, 1)
    time.sleep(1)
    GPIO.output(tube2, 0)
    return


def fire_tube3():
    GPIO.output(tube3, 1)
    time.sleep(1)
    GPIO.output(tube3, 0)
    return


def randomize_tubes():
    rand_water = random.sample(range(1, 7), 2)
    w1 = rand_water[0]
    w2 = rand_water[1]
    rand_candy = list(range(1, 7))
    rand_candy.remove(w1)
    rand_candy.remove(w2)
#	c1 = candy[0]
#	c2 = candy[1]
#	c3 = candy[2]
#	c4 = candy[3]
#	return (water, candy, w1, w2, c1, c2, c3, c4)
    return water, candy


def fire_candy(w_cnt, c_cnt, w_tb, c_tb):
    if c_cnt <= 2:
        if c_tb == 1:
            fire_tube1()
            print ("Candy")
            print ("Count: %s" % c_cnt)
            print ("Tube: %s" % c_tb)
            c_tb = 2
            c_cnt += 1
        elif c_tb == 2:
            fire_tube2()
            print ("Candy")
            print ("Count: %s" % c_cnt)
            print ("Tube: %s" % c_tb)
            c_tb = 1
            c_cnt += 1
    else:
        w_cnt, c_cnt, w_tb, c_tb = fire_water(w_cnt, c_cnt, w_tb, c_tb)
    return w_cnt, c_cnt, w_tb, c_tb


def fire_water(w_cnt, c_cnt, w_tb, c_tb):
    if w_cnt <= 2:
        if w_tb == 1:
            fire_tube3()
            print ("Water")
            print ("Count: %s" % w_cnt)
            print ("Tube: %s" % w_tb)
            w_tb = 1
            w_cnt += 1
        elif w_tb == 2:
#			fire_tube4()
            print ("Water")
            print ("Count: %s" % w_cnt)
            print ("Tube: %s" % w_tb)
            w_tb = 1
            w_cnt += 1
    else:
        w_cnt, c_cnt, w_tb, c_tb = fire_candy(w_cnt, c_cnt, w_tb, c_tb)
    return w_cnt, c_cnt, w_tb, c_tb


def startup():
    setup_channels()
#	flash_led()
    time.sleep(2)
    fire_tube1()
    time.sleep(2)
    fire_tube2()
    time.sleep(2)
    fire_tube3()
    time.sleep(2)
#	flash_led()
    return


#
# Define the RPi board channels for the inputs and outputs.
#

door1 = 11
door2 = 12
door3 = 13
door4 = 14
door5 = 15
door6 = 16
tube1 = 20
tube2 = 21
tube3 = 22
led = 4

#
# Startup and initialize everything.
#

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


except ValueError:
    print('Sample size exceeded population size.')







