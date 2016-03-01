# -*- coding: utf-8 -*-

import struct, binhex, sys, time
import RPi.GPIO as GPIO
from multiprocessing import Process, Value, Array, Lock
from sys import stdout
from evdev import InputDevice
from select import select

# Set GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

# You'll need to find the name of your particular mouse to put in here...
#file = open("/dev/input/by-id/usb-PixArt_USB_Optical_Mouse-event-mouse","rb")
file = open("/dev/input/by-id/usb-Microsoft_Microsoft®_Comfort_Mouse_4500-event-mouse","rb")


# Try Read Mouse
def readMouse(val, lock):
    byte = file.read(16)    
    (type,code,mouseValue) =  struct.unpack_from('hhi', byte, offset=8)

    # if Mouse is running
    if type == 2:
   
        #if Left or Right 
        if code == 0:
            if mouseValue < 0:
                #print "LEFT",mouseValue
                GPIO.output(15, GPIO.LOW)

            elif mouseValue > 0:
                #print "RIGHT",mouseValue
                GPIO.output(15, GPIO.HIGH)
                with lock:
                    val.value += mouseValue

#make my data locked from other processes to manipulate
def eraseData(val, lock):
    with lock:
        val.value = 0;

#
def readSpeedData(val, lock, speed, interval):
    with lock:
        currentSpeed = val.value
	#given number of "mouseValues" divide by given interval
        speed = currentSpeed / interval
        print "Speed is: %d per second" % speed
        val.value = 0

# Main function
if __name__ == '__main__':
    speed = 0;
    v = Value('i', 0)  
    lock = Lock()
    #time to see if filament is moving
    waitTime = 5
    #time interval we will read speed
    interval = 0.1
    #initial time to start mouseValue
    start = time.time()
    #value where we wait until we read the data
    future = start + interval
    #always running program
    while True:
        #during first time interval
        while time.time() < future:           
            # Start ReadMouse as a process
            p = Process(target=readMouse, args=(v, lock)) 
            p.start()

            # Wait for X seconds or until process finishes
            p.join(waitTime)
        	
            # If process is still running without response from filament movement
            if p.is_alive():

                # Terminate process because we know it has stopped
                p.terminate()
                p.join()
                print "Mouse hasnt moved for last ", waitTime, " second(s)"
                #reset data
				eraseData(v, lock)
                #print "Global value IN is: ", v.value
                GPIO.output(18, GPIO.HIGH)

                #Lets to something about it (Sleep here represent any function)
                time.sleep(1)

                GPIO.output(18, GPIO.LOW)

            #print "Global value is: ", v.value
            #stdout.write("VALUE%d" % v.value)
            #stdout.flush()

		#since filament moved, read the speed
        readSpeedData(v, lock, speed, interval)
        
		#update time interval
        start = time.time()
        future = start + interval

