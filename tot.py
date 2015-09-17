
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
# import os
import config as cfg
import socket
import select
import Queue
from threading import Thread


def setup_action():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(cfg.tubes.get('tube1'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube2'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube3'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube4'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube5'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube6'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.sprayers.get('spray1'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.bells.get('bell1'), GPIO.OUT, initial=GPIO.HIGH)
    return


def setup_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(cfg.doors.get('door1'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cfg.doors.get('door2'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cfg.doors.get('door3'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cfg.doors.get('door4'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cfg.doors.get('door5'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cfg.doors.get('door6'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cfg.buttons.get('reset'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cfg.buttons.get('candy_only'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cfg.buttons.get('water_only'), GPIO.IN, pull_up_down = GPIO.PUD_UP)
    return


def sensor_send(item):
    sensor_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sensor_client.connect((cfg.ACTION_IP, cfg.ACTION_PORT))
    sensor_client.send(item)
#    sensor_client.shutdown(socket.SHUT_RDWR)
    sensor_client.close()
    return

def ring_bell(b):
    global run_mode
    if run_mode == "local" or run_mode == "action":
        print ("Mode: " + run_mode + " Ring Bell %s" % b)
        GPIO.output(cfg.bells.get(b), 0)
        time.sleep(1)
        GPIO.output(cfg.bells.get(b), 1)
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
    elif run_mode == "sensor":
        print ("Mode: " + run_mode + "Fire Water %s" % tb)
        sensor_send(tb)
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


def startup():
    global run_mode
    if run_mode == "local" or run_mode == "action":
        print ("Setup Action")
        setup_action()
        check_tube = 1
        while check_tube < num_tubes+1:
            fire_tube("tube"+str(check_tube))
            check_tube += 1
        check_spray = 1
        while check_spray < num_sprayers+1:
            spray_water("spray"+str(check_spray))
            check_spray += 1
        check_bell = 1
        while check_bell < num_bells+1:
            ring_bell("bell"+str(check_bell))
            check_bell += 1
    elif run_mode == "sensor":
        print ("Setup Sensor")
        setup_sensor()
    return


def sensomatic():
    global water_spray_only
    global candy_tube_only
    lockout_timer = 0
    while True:
        if GPIO.input(cfg.buttons.get('water_only')) == False and GPIO.input(cfg.buttons.get('candy_only')) == False:
            if lockout_timer == 0:
                ring_bell(cfg.bells.get('bell1'))
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
                w_cnt = 0
                fire_water()
            elif candy_tube_only == 1 or 2 in candy:
                fire_candy()
            elif 2 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door3')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                fire_water()
            elif candy_tube_only == 1 or 3 in candy:
                fire_candy()
            elif 3 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door4')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                fire_water()
            elif candy_tube_only == 1 or 4 in candy:
                fire_candy()
            elif 4 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door5')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                fire_water()
            elif candy_tube_only == 1 or 5 in candy:
                fire_candy()
            elif 5 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.doors.get('door6')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                fire_water()
            elif candy_tube_only == 1 or 6 in candy:
                fire_candy()
            elif 6 in water:
                fire_water()
            time.sleep(.3)
        elif GPIO.input(cfg.buttons.get('reset')) == False:
            reset_counters()
            global water
            global candy
            water, candy = randomize_tubes()
    return


#class ProcessThread(Thread):
#    def __init__(self):
#        super(ProcessThread, self).__init__()
#        self.running = True
#        self.q = Queue.Queue()
#
#    def add(self, data):
#        self.q.put(data)
#
#    def stop(self):
#        self.running = False
#
#    def run(self):
#        q = self.q
#        while self.running:
#            try:
#                # block for 1 second only:
#                value = q.get(block=True, timeout=.5)
#                action_server_process(value)
#            except Queue.Empty:
#                sys.stdout.write('.')
#                sys.stdout.flush()
#
#        if not q.empty():
#            print "Elements left in the queue:"
#            while not q.empty():
#                print q.get()


def action_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = cfg.ACTION_IP
    port = cfg.ACTION_PORT
    s.bind((host, port))
    print "Listening on port {h} {p}...".format(h=host, p=port)

    s.listen(1)
    client, addr = s.accept()
    while True:
        data = client.recv(20)
        print (data)
        action_server_process(data)
    client.close()

#        try:
#            client, addr = s.accept()
#            ready = select.select([client, ], [], [], 2)
#            if ready[0]:
#                data = client.recv(4096)
#                action_server_process_thread.add(data)
#        except KeyboardInterrupt:
#            print
#            print "Stop."
#            break
#        except socket.error, msg:
#            print "Socket error! %s" % msg
#            break
#    action_server_cleanup()
    return


def action_server_cleanup():
    action_server_process_thread.stop()
    action_server_process_thread.join()
    return


def action_server_process(value):
    print value
    if value in cfg.tubes:
        print (value)
        fire_candy()
    elif value in cfg.sprayers:
        print (value)
        fire_water()
    elif value in cfg.bells:
        print (value)
        ring_bell("bell1")
#    time.sleep(.4)
    return


global num_tubes
global num_doors
global num_sprayers
global num_bells
global num_buttons
global water_spray_only
global candy_tube_only
global water_count
global candy_count
global water_tube
global candy_tube
global run_mode

num_tubes = len(cfg.tubes)
num_doors = len(cfg.doors)
num_sprayers = len(cfg.sprayers)
num_bells = len(cfg.bells)
num_buttons = len(cfg.buttons)
water_spray_only = 0
candy_tube_only = 0
water_count = 0
candy_count = 0
water_tube = 1
candy_tube = 1
run_mode = "local"


#
# Startup and initialize everything.
#

try:

#    print (water_tube)
#    print (candy_tube)

    parser = optparse.OptionParser()
    parser.add_option('-l', '--local', action="store_const", const="local", dest="run_mode", default="local")
    parser.add_option('-s', '--sensor', action="store_const", const="sensor", dest="run_mode")
    parser.add_option('-a', '--action', action="store_const", const="action", dest="run_mode")
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
#        action_server_process_thread = ProcessThread()
#        action_server_process_thread.start()
        action_server()

    else:
        print ("Whoops, something went wrong!")

except Exception, err:
    print "Exception:", str(err)
    import traceback, sys
    print '-'*60
    traceback.print_exc(file=sys.stdout)
    print '-'*60

# End