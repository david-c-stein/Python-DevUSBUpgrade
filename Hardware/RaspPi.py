#!/usr/bin/env python

import Global


if not Global.__EMULATE_HW__:
    import RPi.GPIO as GPIO
    


# Raspberry PI Notes
#  http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3

class _RASP(object):
    # 26 GPIO avaiable on the Raspberry PI 3
    # Name = Pin Number
    GPIO1 = 3
    GPIO2 = 5
    GPIO3 = 7
    GPIO4 = 8
    GPIO5 = 10
    GPIO6 = 11
    GPIO7 = 12
    GPIO8 = 13
    GPIO9 = 15
    GPIO10 = 16
    GPIO11 = 18
    GPIO12 = 19
    GPIO13 = 21
    GPIO14 = 22
    GPIO15 = 23
    GPIO16 = 24
    GPIO17 = 26
    GPIO18 = 29
    GPIO19 = 31
    GPIO20 = 32
    GPIO21 = 33
    GPIO22 = 35
    GPIO23 = 36
    GPIO24 = 37
    GPIO25 = 38
    GPIO26 = 40

    
    
class RaspPi(object):
    
    def __init__(self):
        # Raspberry PI Model A and B GPIO pin assignments
        
        if Global.__EMULATE_HW__:
            self.LOW = 0
            self.HIGH = 1
        else:
            self.LOW = GPIO.LOW
            self.HIGH = GPIO.HIGH
            
        # power for Device Under Test
        self.dutPwrBTN = _RASP.GPIO1
        self.dutPwrLED = _RASP.GPIO2
        self.dutPwrRLY = _RASP.GPIO3

        # Single or Multi usb access
        self.usbMltBTN = _RASP.GPIO4
        self.usbMltLED = _RASP.GPIO5

        # enable usb port 1
        self.usbOneBTN = _RASP.GPIO6
        self.usbOneRLY = _RASP.GPIO7
        
        # enable usb port 2
        self.usbTwoBTN = _RASP.GPIO8
        self.usbTwoRLY = _RASP.GPIO9
        
        # enable usb port 3
        self.usbThrBTN = _RASP.GPIO10
        self.usbThrRLY = _RASP.GPIO11
        
        # enable usb port 4
        self.usbForBTN = _RASP.GPIO12
        self.usbForRLY = _RASP.GPIO13

        # select host device
        self.hostSwBTN = _RASP.GPIO14
        self.hostSwRLY = _RASP.GPIO15

        # ethernet for Device Under Test
        self.dutEthBTN = _RASP.GPIO16
        self.dutEthLED = _RASP.GPIO17
        self.dutEthRLY = _RASP.GPIO18

        # WIU for Device Under Test
        self.dutWiuBTN = _RASP.GPIO19
        self.dutWiuLED = _RASP.GPIO20
        self.dutWiuRLY = _RASP.GPIO21
        
        # Test running
        self.tstRunLED = _RASP.GPIO23

        # Test kill button
        self.tstKilBTN = _RASP.GPIO22
        
        self.initHW()
        
    def __del__(self):
        if not Global.__EMULATE_HW__:
            GPIO.cleanup()
        return

    def initHW(self):
        # initialize relays
        self.setupRLY(self.dutPwrRLY, self.LOW)
        self.setupRLY(self.usbOneRLY, self.LOW)
        self.setupRLY(self.usbTwoRLY, self.LOW)
        self.setupRLY(self.usbThrRLY, self.LOW)
        self.setupRLY(self.usbForRLY, self.LOW)
        self.setupRLY(self.hostSwRLY, self.LOW)
        self.setupRLY(self.dutEthRLY, self.LOW)
        self.setupRLY(self.dutWiuRLY, self.LOW)
        
        # initialize leds
        self.setupLED(self.dutPwrLED, self.LOW)
        self.setupLED(self.usbMltLED, self.LOW)
        self.setupLED(self.dutEthLED, self.LOW)
        self.setupLED(self.dutWiuLED, self.LOW)
        self.setupLED(self.tstRunLED, self.LOW)
        
        # initialize buttons
        self.setupBTN(self.dutPwrBTN)
        self.setupBTN(self.usbMltBTN)
        self.setupBTN(self.usbOneBTN)
        self.setupBTN(self.usbTwoBTN)
        self.setupBTN(self.usbThrBTN)
        self.setupBTN(self.usbForBTN)
        self.setupBTN(self.hostSwBTN)
        self.setupBTN(self.dutEthBTN)
        self.setupBTN(self.dutWiuBTN)
        self.setupBTN(self.tstKilBTN)
       
        
    #------------------------
    # Relays
    
    def setupRLY(self, pin, init):
        if not Global.__EMULATE_HW__:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin, init)
        return
    
    def relayOn(self, pin):
        if not Global.__EMULATE_HW__:
            GPIO.output(pin, GPIO.HIGH)
        return
        
    def relayOff(self, pin):
        if not Global.__EMULATE_HW__:
            GPIO.output(pin, GPIO.LOW)
        return
    
    #------------------------
    # LEDs
    
    def setupLED(self, pin, init):
        if not Global.__EMULATE_HW__:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, init)
        return
    
    def ledOn(self, pin):
        if not Global.__EMULATE_HW__:
            GPIO.output(pin, GPIO.HIGH)
        return
    
    def ledOff(self, pin):
        if not Global.__EMULATE_HW__:
            GPIO.output(pin, GPIO.LOW)
        return
    
    #------------------------
    # Buttons
    
    def setupBTN(self, pin):
        # Button pin set as input w/ pull-up to avoid false detection
        if not Global.__EMULATE_HW__:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return
    
    def addEventDetect(self, pin, myCallback, bouncetime=300):
        if not Global.__EMULATE_HW__:
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=myCallback, bouncetime=bouncetime)
        return
    
    def removeEventDetect(self, pin):
        if not Global.__EMULATE_HW__:
            GPIO.remove_event_detect(pin)
        return
    
