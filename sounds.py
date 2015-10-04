#!/usr/bin/python

import pygame


pygame.mixer.init()

pygame.mixer.music.load("sounds/reset/reset1.wav")
pygame.mixer.music.play()

while pygame.mixer.music.get_busy() == True:
    continue


