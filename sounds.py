#!/usr/bin/python

import pygame


pygame.mixer.init()

pygame.mixer.music.load("sounds/toad-yahoo.wav")
pygame.mixer.music.play()

while pygame.mixer.music.get_busy() == True:
    continue


