#!/usr/bin/python
#
# Trunk or Treat Automation
# Copyright 2015 Tighe Kuykendall
# All rights reserved under the Apache 2.0 License
#
# See http://github.com/tighek/toad-tot
#

import RPi.GPIO as GPIO
import time
import random
import sys
import optparse
import config as cfg
import socket
import select
import pygame


def setup_action():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    if cfg.tubes:
        for tube_name, tube_value in cfg.tubes.iteritems():
            GPIO.setup(tube_value, GPIO.OUT, initial=GPIO.HIGH)
    if cfg.sprayers:
        for sprayer_name, sprayer_value in cfg.sprayers.iteritems():
            GPIO.setup(sprayer_value, GPIO.OUT, initial=GPIO.HIGH)
    if cfg.bells:
        for bell_name, bell_value in cfg.bells.iteritems():
            GPIO.setup(bell_value, GPIO.OUT, initial=GPIO.HIGH)
    pygame.mixer.init()
    return


def setup_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    if cfg.doors:
        for door_name, door_value in cfg.doors.iteritems():
            GPIO.setup(door_value, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    if cfg.buttons:
        for button_name, button_value in cfg.buttons.iteritems():
            GPIO.setup(button_value, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    return


def sensor_send(item):
    sensor_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sensor_client.connect((cfg.ACTION_IP, cfg.ACTION_PORT))
    sensor_client.send(item)
    sensor_client.close()
    return


def ring_bell(b):
    global run_mode
    if run_mode == "local" or run_mode == "action":
        print ("Mode: " + run_mode + " Ring Bell %s" % b)
        GPIO.output(cfg.bells.get(b), 0)
        time.sleep(1)
        GPIO.output(cfg.bells.get(b), 1)
        sound_play("reload")
    elif run_mode == "sensor":
        print ("Mode: " + run_mode + "Ring Bell %s" % b)
        sensor_send(b)
    return


def fire_tube(tb):
    global run_mode
    if run_mode == "local" or run_mode == "action":
        print ("Mode: " + run_mode + " Fire Candy %s" % tb)
        GPIO.output(cfg.tubes.get(tb), 0)
        time.sleep(.5)
        GPIO.output(cfg.tubes.get(tb), 1)
        sound_play("success")
    elif run_mode == "sensor":
        print ("Mode: " + run_mode + "Fire Candy %s" % tb)
        sensor_send(tb)
    return


def spray_water(tb):
    global run_mode
    if run_mode == "local" or run_mode == "action":
        print ("Mode: " + run_mode + "Fire Water %s" % tb)
        GPIO.output(cfg.sprayers.get(tb), 0)
        time.sleep(.5)
        GPIO.output(cfg.sprayers.get(tb), 1)
        sound_play("fail")
    elif run_mode == "sensor":
        print ("Mode: " + run_mode + "Fire Water %s" % tb)
        sensor_send(tb)
    return


def sound_pygame(sound):
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    return


def sound_play(type):
    if type == "reset":
        sound_pygame(cfg.SOUND_RESET)
    elif type == "fail":
        sound_pygame(cfg.SOUND_FAIL)
    elif type == "success":
        sound_pygame(cfg.SOUND_SUCCESS)
    elif type == "reload":
        sound_pygame(cfg.SOUND_RELOAD)
    return


def randomize_tubes():
    rand_water = random.sample(range(1, 7), 2)
    w1 = rand_water[0]
    w2 = rand_water[1]
    rand_candy = list(range(1, 7))
    rand_candy.remove(w1)
    rand_candy.remove(w2)
    print ("Water Tubes: %s" % rand_water)
    print ("Candy Tubes: %s" % rand_candy)
    time.sleep(1)
    return rand_water, rand_candy


def fire_candy():
    global candy_tube
    global candy_tube_only
    global candy_count
    global water_count
    if candy_tube_only == 1 and candy_tube < num_tubes:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        candy_count = 0
        fire_tube("tube"+str(candy_tube))
        candy_tube += 1
    elif candy_tube_only == 1 and candy_tube == num_tubes:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        candy_count = 0
        fire_tube("tube"+str(candy_tube))
        ring_bell("bell1")
        candy_tube = 1
    elif 1 <= candy_tube <= num_tubes-1 and candy_count < 2:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        candy_count += 1
        fire_tube("tube"+str(candy_tube))
        candy_tube += 1
    elif candy_tube == num_tubes and candy_count < 2:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        candy_count += 1
        fire_tube("tube"+str(candy_tube))
        ring_bell("bell1")
        candy_tube = 1
        water_count = 0
    else:
        candy_count = 0
        fire_water()
    time.sleep(.3)
    return


def fire_water():
    global water_spray_only
    global water_tube
    global water_count
    if water_spray_only == 1:
        tot_water_metrics = open('tot_water_metrics', 'a')
        tot_water_metrics.write('1')
        tot_water_metrics.close()
        spray_water("spray"+str(water_tube))
        water_tube = 1
    elif water_tube == 1 and water_count <= 2:
        tot_water_metrics = open('tot_water_metrics', 'a')
        tot_water_metrics.write('1')
        tot_water_metrics.close()
        water_count += 1
        spray_water("spray"+str(water_tube))
        water_tube = 1
    else:
        water_count = 0
        fire_candy()
    time.sleep(.3)
    return


def reset_counters():
    global water_count
    global candy_count
    global water_tube
    global candy_tube
    water_count = 0
    candy_count = 0
    water_tube = 1
    candy_tube = 1
    return


def test_action():
    if cfg.tubes:
        for tube_name, tube_value in cfg.tubes.iteritems():
            fire_tube(tube_name)
    if cfg.sprayers:
        for sprayer_name, sprayer_value in cfg.sprayers.iteritems():
            spray_water(sprayer_name)
    if cfg.bells:
        for bell_name, bell_value in cfg.bells.iteritems():
            ring_bell(bell_name)
    return


def startup():
    global run_mode
    if run_mode == "local":
        print ("Setup Local Mode")
        setup_sensor()
        setup_action()
        test_action()
    elif run_mode == "action":
        print ("Setup Action Mode")
        setup_action()
        test_action()
    elif run_mode == "sensor":
        print ("Setup Sensor Mode")
        setup_sensor()
    return


def sensomatic():
    global water_spray_only
    global candy_tube_only
    global water_count
    global water
    global candy
    lockout_timer = 0
    while True:
        if GPIO.input(cfg.buttons.get('water_only')) == False and GPIO.input(cfg.buttons.get('candy_only')) == False:
            if lockout_timer == 0:
                ring_bell("bell1")
                lockout_timer += 1
                time.sleep(.5)
            elif lockout_timer == 20:
                lockout_timer = 0
                time.sleep(.5)
            else:
                lockout_timer += 1
                time.sleep(.5)

        if GPIO.input(cfg.buttons.get('water_only')) == False:
            water_spray_only = 1
        elif GPIO.input(cfg.buttons.get('water_only')) == True:
            water_spray_only = 0

        if GPIO.input(cfg.buttons.get('candy_only')) == False:
            candy_tube_only = 1
        elif GPIO.input(cfg.buttons.get('candy_only')) == True:
            candy_tube_only = 0

        if GPIO.input(cfg.doors.get('door1')) == False:
            if water_spray_only == 1:
                water_count = 0
                fire_water()
            elif candy_tube_only == 1 or 1 in candy:
                fire_candy()
            elif 1 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door2')) == False:
            if water_spray_only == 1:
                water_count = 0
                fire_water()
            elif candy_tube_only == 1 or 2 in candy:
                fire_candy()
            elif 2 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door3')) == False:
            if water_spray_only == 1:
                water_count = 0
                fire_water()
            elif candy_tube_only == 1 or 3 in candy:
                fire_candy()
            elif 3 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door4')) == False:
            if water_spray_only == 1:
                water_count = 0
                fire_water()
            elif candy_tube_only == 1 or 4 in candy:
                fire_candy()
            elif 4 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door5')) == False:
            if water_spray_only == 1:
                water_count = 0
                fire_water()
            elif candy_tube_only == 1 or 5 in candy:
                fire_candy()
            elif 5 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door6')) == False:
            if water_spray_only == 1:
                water_count = 0
                fire_water()
            elif candy_tube_only == 1 or 6 in candy:
                fire_candy()
            elif 6 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.buttons.get('reset')) == False:
            reset_counters()
            water, candy = randomize_tubes()
    return


def action_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((cfg.ACTION_IP, cfg.ACTION_PORT))
    print ("Listening on port {h} {p}...".format(h=cfg.ACTION_IP, p=cfg.ACTION_PORT))
    s.listen(5)

    while True:
        try:
            client, addr = s.accept()
            ready = select.select([client, ], [], [], 1)
            if ready[0]:
                data = client.recv(500)
                action_server_process(data)
            if not data:
                sys.stdout.write('.')
                sys.stdout.flush()
        except KeyboardInterrupt:
            print ()
            print ("Stop.")
            break
        except socket.error, msg:
            print ("Socket error! %s" % msg)
            break
    client.close()
    print ("end of action server")
    return


def action_server_process(value):
    if value in cfg.tubes:
        fire_tube(value)
    elif value in cfg.sprayers:
        spray_water(value)
    elif value in cfg.bells:
        ring_bell(value)
    return

if __name__ == "__main__":
    global num_tubes
    num_tubes = len(cfg.tubes)
    global num_doors
    num_doors = len(cfg.doors)
    global num_sprayers
    num_sprayers = len(cfg.sprayers)
    global num_bells
    num_bells = len(cfg.bells)
    global num_buttons
    num_buttons = len(cfg.buttons)
    global water_spray_only
    water_spray_only = 0
    global candy_tube_only
    candy_tube_only = 0
    global water_count
    water_count = 0
    global candy_count
    candy_count = 0
    global water_tube
    water_tube = 1
    global candy_tube
    candy_tube = 1
    global run_mode
    run_mode = "local"


    try:
        parser = optparse.OptionParser()
        parser.add_option('-l', '--local', action="store_const", const="local", dest="run_mode", default="local", help="Run in Local Mode")
        parser.add_option('-s', '--sensor', action="store_const", const="sensor", dest="run_mode", help="Run in Sensor Mode")
        parser.add_option('-a', '--action', action="store_const", const="action", dest="run_mode", help="Run in Action Mode")
        (options, args) = parser.parse_args()
        if options.run_mode:
            run_mode = options.run_mode

        print ("Startup Routine")
        startup()

        if run_mode == "local" or not run_mode:
            print ("Running in mode: " + options.run_mode)
            water, candy = randomize_tubes()
            sensomatic()
        elif run_mode == "sensor":
            print ("Running in mode: " + options.run_mode)
            water, candy = randomize_tubes()
            sensomatic()
        elif run_mode == "action":
            print ("Running in mode: " + options.run_mode)
            action_server()
        else:
            print ("Whoops, something went wrong!")

    except Exception, err:
        print ("Exception:", str(err))
        import traceback, sys
        print ('-'*60)
        traceback.print_exc(file=sys.stdout)
        print ('-'*60)

# End