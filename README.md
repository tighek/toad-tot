# toad-tot

Toad Trunk or Treat

Our toad house originally debuted at the Pinewood Preparatory School Trunk or Treat
in Oct 2014.  It's a bean bag toss game that dispenses vandy.

The original version had 2 doors which where wired directly to the candy cannons
(picture and diagram included).  It was a pretty simple game and the kids learned which
doors would give candy.  Some of the older kids also learned that if they stood in the
right spot they could catch candy from the smaller kids which had to stand closer to
the game.

We are back in 2015 with this new and improved version!  The toad house is now automated
with a Raspberry Pi.  The improved (upgraded from 2 tubes to 6 tubes) candy cannons are
wired to a relay strip controlled by the RPi.  All of the doors are wired to RPi GPIO
pins.


Future features:
  - Play a sound effect for each type of door.
  - Web interface for:
    + Handling the functions of the 3 mechanical switches.
    + Provide a live camera feed looking at the person playing.
    + Lock-out to stop all candy and water activities.


Features in v1.1
  - Add length of dictionary for easier reconfig for number of tubes or doors.


Features in v1.0:

  - All 6 doors create an action
  - Doors will be randomized so that 4 doors deliver candy and 2 doors deliver water.
  - If 2 water doors are opened consecutively the next door will be candy.
  - If 2 candy doors are opened consecutively the next door will be water.
  - When the 6th candy tube is used, ring a bell so we know to reload.
  - There are 3 switches concealed beside the automation gear:
    + Switch #1 resets the counters, randomizes the doors, and effectively starts the
      game for a new player.
    + Switch #2 sets all doors to dispense candy.  This is for the little kids.
    + Switch #3 sets all doors to dispense water.  This is for the older kids that
      coming back for candy...
 

