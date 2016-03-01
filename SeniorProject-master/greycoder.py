import RPi.GPIO as GPIO
import time

#setup the GPIO
GPIO.setmode(GPIO.BCM)

#hook me up to BCM GPIO #17
GPIO.setup(17, GPIO.INPUT)

#Simple output
while (True):
	print GPIO.input(17)
	sleep(0.05)

#cleanup the gpio when done.
