#!/usr/bin/env python3 -- coding: utf-8 --
""" Programme principal du KOSMOS en mode rotation Utilse une machine d'états D Hanon 12 décembre 2020 """
import logging
import time
from threading import Event
import RPi.GPIO as GPIO
import os
import sys
import pigpio

#Le programme est divisé en deux threads donc on a besoind du bibliotheque Thread
from threading import Thread

import kosmos_config as KConf

import kosmos_esc_motor as KMotor

MOTOR_BUTTON_GPIO = 21
GPIO.setmode(GPIO.BCM)  # on utilise les n° de GPIO et pas les broches
GPIO.setup(MOTOR_BUTTON_GPIO, GPIO.IN)
        
motorThread = KMotor.komosEscMotor(KConf.KosmosConfig())


time.sleep(2)
motorThread.power_on()

time.sleep(1)

motorThread.set_speed(1350)

time.sleep(5)

motorThread.set_speed(0)


time.sleep(1)

motorThread.power_off()
pigpio.pi().stop()