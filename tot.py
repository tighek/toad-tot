
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



def setup_channels():
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
    GPIO.setup(cfg.tubes.get('tube1'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube2'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube3'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube4'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube5'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.tubes.get('tube6'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.sprayers.get('spray1'), GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(cfg.bells.get('bell1'), GPIO.OUT, initial=GPIO.HIGH)
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


def fire_candy(w_cnt, c_cnt, w_tb, c_tb):
    if candy_tube_only == 1 and c_tb < num_tubes:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        c_cnt = 0
        fire_tube(cfg.tubes.get("tube"+str(c_tb)))
        c_tb += 1
    elif candy_tube_only == 1 and c_tb == num_tubes:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        c_cnt = 0
        fire_tube(cfg.tubes.get("tube"+str(c_tb)))
        ring_bell(cfg.bells.get('bell1'))
        c_tb = 1
    if 1 <= c_tb <= num_tubes-1 and c_cnt < 2:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        c_cnt += 1
        fire_tube(cfg.tubes.get("tube"+str(c_tb)))
        c_tb += 1
    elif c_tb == num_tubes and c_cnt < 2:
        tot_candy_metrics = open('tot_candy_metrics', 'a')
        tot_candy_metrics.write('1')
        tot_candy_metrics.close()
        c_cnt += 1
        fire_tube(cfg.tubes.get("tube"+str(c_tb)))
        ring_bell(cfg.bells.get('bell1'))
        c_tb = 1
        w_cnt = 0
    else:
        c_cnt = 0
        w_cnt, c_cnt, w_tb, c_tb = fire_water(w_cnt, c_cnt, w_tb, c_tb)
    return w_cnt, c_cnt, w_tb, c_tb


def fire_water(w_cnt, c_cnt, w_tb, c_tb):
    if water_spray_only == 1:
        tot_water_metrics = open('tot_water_metrics', 'a')
        tot_water_metrics.write('1')
        tot_water_metrics.close()
        spray_water(cfg.sprayers.get("spray"+str(w_tb)))
        w_tb = 1
    elif w_tb == 1 and w_cnt <= 2:
        tot_water_metrics = open('tot_water_metrics', 'a')
        tot_water_metrics.write('1')
        tot_water_metrics.close()
        w_cnt += 1
        spray_water(cfg.sprayers.get("spray"+str(w_tb)))
        w_tb = 1
    else:
        w_cnt = 0
        w_cnt, c_cnt, w_tb, c_tb = fire_candy(w_cnt, c_cnt, w_tb, c_tb)
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
        fire_tube(cfg.tubes.get("tube"+str(check_tube)))
        check_tube += 1
    check_spray = 1
    while check_spray < num_sprayers+1:
        spray_water(cfg.sprayers.get("spray"+str(check_spray)))
        check_spray += 1
    check_bell = 1
    while check_bell < num_bells+1:
        ring_bell(cfg.bells.get("bell"+str(check_bell)))
        check_bell += 1
    return


def sensomatic(w_count, c_count, w_tube, c_tube):
    while True:
#        if GPIO.input(cfg.buttons.get('water_only')) == False and GPIO.input(cfg.buttons.get('candy_only')) == False:
#            ring_bell(cfg.bells.get('bell1'))
#            time.sleep(60)
#        elif GPIO.input(cfg.buttons.get('water_only')) == False:
#            water_spray_only = 1
#        elif GPIO.input(cfg.buttons.get('water_only')) == True:
#            water_spray_only = 0
#        elif GPIO.input(cfg.buttons.get('candy_only')) == False:
#            candy_tube_only = 1
#        elif GPIO.input(cfg.buttons.get('candy_only')) == True:
#            candy_tube_only = 0
        if GPIO.input(cfg.doors.get('door1')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
            elif candy_tube_only == 1:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 1 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 1 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif GPIO.input(cfg.doors.get('door2')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
            elif candy_tube_only == 1:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 2 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 2 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif GPIO.input(cfg.doors.get('door3')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
            elif candy_tube_only == 1:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 3 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 3 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif GPIO.input(cfg.doors.get('door4')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
            elif candy_tube_only == 1:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 4 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 4 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif GPIO.input(cfg.doors.get('door5')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
            elif candy_tube_only == 1:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 5 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 5 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif GPIO.input(cfg.doors.get('door6')) == False:
            if water_spray_only == 1:
                w_cnt = 0
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
            elif candy_tube_only == 1:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 6 in candy:
                w_count, c_count, w_tube, c_tube = fire_candy(w_count, c_count, w_tube, c_tube)
            elif 6 in water:
                w_count, c_count, w_tube, c_tube = fire_water(w_count, c_count, w_tube, c_tube)
        elif GPIO.input(cfg.buttons.get('reset')) == False:
            reset_counters(w_count, c_count, w_tube, c_tube)
    return w_count, c_count, w_tube, c_tube


class ProcessThread(Thread):
    def __init__(self):
        super(ProcessThread, self).__init__()
        self.running = True
        self.q = Queue.Queue()

    def add(self, data):
        self.q.put(data)

    def stop(self):
        self.running = False

    def run(self):
        q = self.q
        while self.running:
            try:
                # block for 1 second only:
                value = q.get(block=True, timeout=.5)
                action_server_process(value)
            except Queue.Empty:
                sys.stdout.write('.')
                sys.stdout.flush()
        #
        if not q.empty():
            print "Elements left in the queue:"
            while not q.empty():
                print q.get()


def action_server():
    s = socket.socket()
    host = cfg.ACTION_IP
    port = cfg.ACTION_PORT
    s.bind((host, port))
    print "Listening on port {h} {p}...".format(h=host, p=port)

    s.listen(5)
    while True:
        try:
            client, addr = s.accept()
            ready = select.select([client,],[], [],2)
            if ready[0]:
                data = client.recv(4096)
                #print data
                action_server_process_thread.add(data)
        except KeyboardInterrupt:
            print
            print "Stop."
            break
        except socket.error, msg:
            print "Socket error! %s" % msg
            break
    #
    action_server_cleanup()

def action_server_cleanup():
    action_server_process_thread.stop()
    action_server_process_thread.join()


def action_server_process(value):
    """
    Implement this. Do something useful with the received data.
    """
    print value
    if value == "tube1":
        print (value)
        water_count, candy_count, water_tube, candy_tube = fire_candy(water_count, candy_count, water_tube, candy_tube)
    sleep(.4)


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

#
# Startup and initialize everything.
#

print ("Startup Routine")
startup()


if __name__ == "__main__":

    try:
        parser = optparse.OptionParser()
        parser.add_option('-l', '--local', action="store_const", const="local", dest="run_mode", default="local")
        parser.add_option('-s', '--sensor', action="store_const", const="sensor", dest="run_mode")
        parser.add_option('-a', '--action', action="store_const", const="action", dest="run_mode")
        (options, args) = parser.parse_args()

        action_server_process_thread = ProcessThread()
        action_server_process_thread.start()

        if options.run_mode == "local" or not options.run_mode:

            print ("Running in mode: " + options.run_mode)

            water, candy = randomize_tubes()

            print ("Water Tubes: %s" % water)
            print ("Candy Tubes: %s" % candy)

            water_count, candy_count, water_tube, candy_tube = sensomatic(water_count, candy_count, water_tube, candy_tube)

        elif options.run_mode == "sensor":
            print ("Running in mode: " + options.run_mode)


        elif options.run_mode == "action":
            print ("Running in mode: " + options.run_mode)
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