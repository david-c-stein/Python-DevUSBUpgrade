#!/usr/bin/env python

import Global

if Global.__MULTIPROCESSING__:
    import multiprocessing

import time
import threading
from tornado.escape import json_encode, json_decode

from RaspPi import RaspPi

'''
class binaryState(object):
    def __init__(self):
        self.currState = False
        self.prevState = False

    @property
    def state(self):
        return self.currState

    @state.setter
    def state(self, newState):
        self.prevState = self.currState;
        self.currState = newState

    @state.deleter
    def state(self):
        del self.currState
        del self.prevState

    def trigPos(self):
        # trigger on positive edge
        return (self.currState and not self.prevState)

    def trigNeg(self):
        return (self.prevState and not self.currState)

    def toggle(self):
        self.prevState = self.currState
        self.currState = not self.currState
'''


class hardwareState(object):

    def __init__(self):
        self._usbHost = False
        self._usbClientMulti = False
        self._usbClientP1 = False
        self._usbClientP2 = False
        self._usbClientP3 = False
        self._usbClientP4 = False
        self._dutEthernet = False
        self._dutWiu = False
        self._dutPower = False 
        self._tstRun = False
      
        self._usbClientLast = 0
        return

    # -------------------------------------------

    def getUsbHost(self):
        return self._usbHost

    def getUsbClientMulti(self):
        return self._usbClientMulti

    def getUsbClientP1(self):
        return self._usbClientP1

    def getUsbClientP2(self):
        return self._usbClientP2

    def getUsbClientP3(self):
        return self._usbClientP3

    def getUsbClientP4(self):
        return self._usbClientP4

    def getUsbClientLast(self):
        return self.usbClientLast
    
    def getDutEthernet(self):
        return self._dutEthernet
        
    def getDutWiu(self):
        return self._dutWiu
        
    def getDutPower(self):
        return self._dutPower

    def getTstRun(self):
        return self._tstRun
        
    # ---------------
    # power

    def setPowerOn(self):
        self._dutPower = True

    def setPowerOff(self):
        self._dutPower = False

    def setPowerToggle(self):
        self._dutPower = not self._dutPower

    # ---------------
    # ethernet

    def setDutEthernetOn(self):
        self._dutEthernet = True

    def setDutEthernetOff(self):
        self._dutEthernet = False

    def setDutEthernetToggle(self):
        self._dutEthernet = not self._dutEthernet

    # ---------------
    # WIU

    def setDutWiuOn(self):
        self._dutWiu = True

    def setDutWiuOff(self):
        self._dutWiu = False

    def setDutWiuToggle(self):
        self._dutWiu = not self._dutWiu

    # ---------------
    # host usb

    def setHostDUT(self):
        self._usbHost = False

    def setHostPc(self):
        self._usbHost = True

    def setHostToggle(self):
        self._usbHost = not self._usbHost

    # ---------------
    # client usb

    def setUsbClientMulti(self, value):
        self._usbClientMulti = value
        if(self._usbClientMulti == False):
            if (self._usbClientLast == 1):  
                self._usbClientP1 = True  
            else:  
                self._usbClientP1 = False
                
            if (self._usbClientLast == 2):  
                self._usbClientP2 = True  
            else:  
                self._usbClientP2 = False
                
            if (self._usbClientLast == 3):  
                self._usbClientP3 = True  
            else:  
                self._usbClientP3 = False
                
            if (self._usbClientLast == 4):  
                self._usbClientP4 = True  
            else:  
                self._usbClientP4 = False

    def setUsbClientMultiToggle(self):
        self.setUsbClientMulti(not self._usbClientMulti)

        
    def setUsbClientP1Toggle(self):
        self._usbClientP1 = not self._usbClientP1
        if(self._usbClientP1 == True):
            self._usbClientLast = 1
            if (not self._usbClientMulti):
                self._usbClientP2 = False
                self._usbClientP3 = False
                self._usbClientP4 = False

    def setUsbClientP1(self, value):
        self._usbClientP1 = value
        if (value == True):
            self._usbClientLast = 1
            if (not self._usbClientMulti):
                self._usbClientP2 = False
                self._usbClientP3 = False
                self._usbClientP4 = False

                
    def setUsbClientP2Toggle(self):
        self._usbClientP2 = not self._usbClientP2
        if(self._usbClientP2 == True):
            self._usbClientLast = 2
            if (not self._usbClientMulti):
                self._usbClientP1 = False
                self._usbClientP3 = False
                self._usbClientP4 = False

    def setUsbClientP2(self, value):
        self._usbClientP2 = value
        if (value == True):
            self._usbClientLast = 2
            if (not self._usbClientMulti):
                self._usbClientP1 = False
                self._usbClientP3 = False
                self._usbClientP4 = False

                
    def setUsbClientP3Toggle(self):
        self._usbClientP3 = not self._usbClientP3
        if(self._usbClientP3 == True):
            self._usbClientLast = 3
            if (not self._usbClientMulti):
                self._usbClientP1 = False
                self._usbClientP2 = False
                self._usbClientP4 = False

    def setUsbClientP3(self, value):
        self._usbClientP3 = value
        if (value == True):
            self._usbClientLast = 3
            if (not self._usbClientMulti):
                self._usbClientP1 = False
                self._usbClientP2 = False
                self._usbClientP4 = False
        
        
    def setUsbClientP4Toggle(self):
        self._usbClientP4 = not self._usbClientP4
        if(self._usbClientP4 == True):
            self._usbClientLast = 4
            if (not self._usbClientMulti):
                self._usbClientP1 = False
                self._usbClientP2 = False
                self._usbClientP3 = False

    def setUsbClientP4(self, value):
        self._usbClientP4 = value
        if (value == True):
            self._usbClientLast = 4
            if (not self._usbClientMulti):
                self._usbClientP1 = False
                self._usbClientP2 = False
                self._usbClientP3 = False

    # ---------------
    # Test status LED

    def setTstRunOn(self):
        self._tstRun = True

    def setTstRunOff(self):
        self._tstRun = False

    def setTstRunToggle(self):
        self._tstRun = not self._tstRun


class Hardware(multiprocessing.Process if Global.__MULTIPROCESSING__ else threading.Thread):

    def __getstate__(self):
        # Process safe logger copy
        d = self.__dict__.copy()
        if 'logger' in d:
            d['logger'] = d['logger'].name
        return d

    def __setstate__(self, d):
        # Process safe logger copy
        if 'logger' in d:
            logging.config.dictConfig(d['logconfig'])
            d['logger'] = logging.getLogger(d['logger'])
        self.__dict__.update(d)

    def __init__(self, logger, logconfig, queCam, queHdw, queWeb, config):
        if Global.__MULTIPROCESSING__:
            #-- multiprocessing
            multiprocessing.Process.__init__(self)
        else:
            #-- threading
            super(Hardware, self).__init__()

        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.logger.debug("Initializing " + __file__)

        # message queues
        self.getMsg = queHdw
        self.putMsgCam = queCam.put
        self.putMsgWeb = queWeb.put

        self.GPIO = None
        self.hwState = hardwareState()
        self.sendWebCurrentState()
        return

    #---------
    #  Power

    def _PowerSetHW(self):
        # signal hardware
        if(self.hwState.getDutPower):
            self.GPIO.relayOn(self.GPIO.dutPwrRLY)
            self.GPIO.ledOn(self.GPIO.dutPwrLED)
        else:
            self.GPIO.relayOff(self.GPIO.dutPwrRLY)
            self.GPIO.ledOff(self.GPIO.dutPwrLED)
        # signal web
        self.sendWebCurrentState()
        return
    
    def handlerDutPowerBTN(event):
        self.hwState.setPowerToggle()
        self._PowerSetHW()
        return

    def evtDutPower(self, type):
        if(type == 'btnPressed'):
            self.hwState.setPowerToggle()
        elif(type == 'On'):
            self.hwState.setPowerOn()
        elif(type == 'Off'):
            self.hwState.setPowerOff()
        else:
            self.logger.warn("evtDutPower: unknown type : " + str(type))
        self._PowerSetHW()
        return

    #---------
    # Ethernet

    def _DutEthSetHW(self):
        # signal hardware
        if(self.hwState.getDutEthernet):
            self.GPIO.relayOn(self.GPIO.dutEthRLY)
            self.GPIO.ledOn(self.GPIO.dutEthLED)
        else:
            self.GPIO.relayOff(self.GPIO.dutEthRLY)
            self.GPIO.ledOff(self.GPIO.dutEthLED)
        # signal web
        self.sendWebCurrentState()
        return
    
    def handlerDutEthBTN(event):
        self.hwState.setDutEthernetToggle()
        self._DutEthSetHW()
        return

    def evtDutEth(self, type):
        if(type == 'btnPressed'):
            self.hwState.setDutEthernetToggle()
        elif(type == 'On'):
            self.hwState.setDutEthernetOn()
        elif(type == 'Off'):
            self.hwState.setDutEthernetOff()
        else:
            self.logger.warn("evtDutEth: unknown type : " + str(type))

        self._DutEthSetHW()
        return

    #---------
    # WIU

    def _DutWiuSetHW(self):
        # signal hardware
        if(self.hwState.getDutWiu):
            self.GPIO.relayOn(self.GPIO.dutWiuRLY)
            self.GPIO.ledOn(self.GPIO.dutWiuLED)
        else:
            self.GPIO.relayOff(self.GPIO.dutWiuRLY)
            self.GPIO.ledOff(self.GPIO.dutWiuLED)
        # signal web
        self.sendWebCurrentState()
        return
    
    def handlerDutWiuBTN(event):
        self.hwState.setDutWiuToggle()
        self._DutWiuSetHW()
        return

    def evtDutWiu(self, type):
        if(type == 'btnPressed'):
            self.hwState.setDutWiuToggle()
        elif(type == 'On'):
            self.hwState.setDutWiuOn()
        elif(type == 'Off'):
            self.hwState.setDutWiuOff()
        else:
            self.logger.warn("evtDutWiu: unknown type : " + str(type))
        self._DutWiuSetHW()
        return
        
    #---------
    #  Usb Multi

    def handlerUsbMltBTN(event):
        self.logger.debug("usbMltBTN pressed")
        # toggle state
        self.hwState.setUsbClientMultiToggle()
        # signal web
        self.sendWebCurrentState()
        return

    def evtUsbMlt(self, type):
        self.logger.debug("usbMltBTN pressed")
        if(type == 'btnPressed'):
            self.hwState.setUsbClientMultiToggle()
        elif(type == 'On'):
            self.hwState.setUsbClientMulti(True)
        elif(type == 'Off'):
            self.hwState.setUsbClientMulti(False)
        else:
            self.logger.warn("evtUsbMlt: unknown type : " + str(type))
        self.sendWebCurrentState()
        return

    #---------
    # Usb Port 1

    def _UsbOneSetHW(self):
        # signal hardware
        if(self.hwState.getUsbClientP1):
            self.GPIO.relayOn(self.GPIO.usbOneRLY)
        else:
            self.GPIO.relayOff(self.GPIO.usbOneRLY)
        # signal web
        self.sendWebCurrentState()

    def handlerUsbOneBTN(event):
        self.hwState.setUsbClientP1Toggle()
        self._UsbOneSetHW()
        return

    def evtUsbOne(self, type):
        if(type == 'btnPressed'):
            self.hwState.setUsbClientP1Toggle()
        elif(type == 'On'):
            self.hwState.setUsbClientP1(True)
        elif(type == 'Off'):
            self.hwState.setUsbClientP1(False)
        else:
            self.logger.warn("evtUsbOne: unknown type : " + str(type))
        self._UsbOneSetHW()
        return

    #---------
    # Usb Port 2

    def _UsbTwoSetHW(self):
        # signal hardware
        if(self.hwState.getUsbClientP2):
            self.GPIO.relayOn(self.GPIO.usbTwoRLY)
        else:
            self.GPIO.relayOff(self.GPIO.usbTwoRLY)
        # signal web
        self.sendWebCurrentState()

    def handlerUsbTwoBTN(event):
        self.hwState.setUsbClientP2Toggle()
        self._UsbTwoSetHW()
        return

    def evtUsbTwo(self, type):
        if(type == 'btnPressed'):
            self.hwState.setUsbClientP2Toggle()
        elif(type == 'On'):
            self.hwState.setUsbClientP2(True)
        elif(type == 'Off'):
            self.hwState.setUsbClientP2(False)
        else:
            self.logger.warn("evtUsbTwo: unknown type : " + str(type))
        self._UsbTwoSetHW()
        return

    #---------
    # Usb Port 3

    def _UsbThrSetHW(self):
        # signal hardware
        if(self.hwState.getUsbClientP3):
            self.GPIO.relayOn(self.GPIO.usbThrRLY)
        else:
            self.GPIO.relayOff(self.GPIO.usbThrRLY)
        # signal web
        self.sendWebCurrentState()

    def handlerUsbThrBTN(event):
        self.hwState.setUsbClientP3Toggle()
        self._UsbThrSetHW()
        return

    def evtUsbThr(self, type):
        if(type == 'btnPressed'):
            self.hwState.setUsbClientP3Toggle()
        elif(type == 'On'):
            self.hwState.setUsbClientP3(True)
        elif(type == 'Off'):
            self.hwState.setUsbClientP3(False)
        else:
            self.logger.warn("evtUsbThr: unknown type : " + str(type))
        self._UsbThrSetHW()
        return

    #---------
    # Usb Port 4

    def _UsbForSetHW(self):
        # signal hardware
        if(self.hwState.getUsbClientP4):
            self.GPIO.relayOn(self.GPIO.usbForRLY)
        else:
            self.GPIO.relayOff(self.GPIO.usbForRLY)
        # signal web
        self.sendWebCurrentState()

    def handlerUsbForBTN(event):
        self.hwState.setUsbClientP4Toggle()
        self._UsbForSetHW()
        return

    def evtUsbFor(self, type):
        if(type == 'btnPressed'):
            self.hwState.setUsbClientP4Toggle()
        elif(type == 'On'):
            self.hwState.setUsbClientP4(True)
        elif(type == 'Off'):
            self.hwState.setUsbClientP4(False)
        else:
            self.logger.warn("evtUsbFor: unknown type : " + str(type))
        self._UsbForSetHW()
        return

    #---------
    # Usb Host

    def _HostSetHW(self):
        # signal hardware
        if(self.hwState._usbHost):
            self.GPIO.relayOn(self.GPIO.hostSwRLY)
        else:
            self.GPIO.relayOff(self.GPIO.hostSwRLY)
        # signal web
        self.sendWebCurrentState()
    
    def handlerHostBTN(event):
        self.hwState.setHostToggle()
        self._HostSetHW()
        return

    def evtHostDut(self, type):
        if(type == 'btnPressed'):
            self.hwState.setHostDUT()
        elif(type == 'On'):
            self.hwState.setHostDUT()
        elif(type == 'Off'):
            self.hwState.setHostPC()
        else:
            self.logger.warn("evtHostDut: unknown type : " + str(type))
        self._HostSetHW()
        return

    def evtHostPc(self, type):
        if(type == 'btnPressed'):
            self.hwState.setHostPc()
        elif(type == 'On'):
            self.hwState.setHostPc()
        elif(type == 'Off'):
            self.hwState.setHostDUT()
        else:
            self.logger.warn("evtHostPc: unknown type : " + str(type))
        self._HostSetHW()
        return
        
    #---------
    #  Run

    def _TstRunSetHW(self):
        # signal hardware
        if(self.hwState.getTstRun):
            self.GPIO.ledOn(self.GPIO.tstRunLED)
        else:
            self.GPIO.ledOff(self.GPIO.tstRunLED)
        # signal web
        self.sendWebCurrentState()
        return
    
    def evtTstRun(self, type):
        if(type == 'btnPressed'):
            self.hwState.setTstRunToggle()
        elif(type == 'On'):
            self.hwState.setTstRunOn()
        elif(type == 'Off'):
            self.hwState.setTstRunOff()
        else:
            self.logger.warn("evtTstRun: unknown type : " + str(type))
        self._TstRunSetHW()
        return
  
    #---------
    
    def _TstKill(self, whom, reason):
        self.logger.debug("_TstKill")
        # signal hardware

        # Reset HW system
        self._usbHost = False
        self._usbClientMulti = False
        self._usbClientP1 = False
        self._usbClientP2 = False
        self._usbClientP3 = False
        self._usbClientP4 = False
        self._dutEthernet = False
        self._dutWiu = False
        self._dutPower = False 
        self._tstRun = False
        self._usbClientLast = 0

        # Reset hardware
        self.GPIO.initHW()

        # signal web
        self.putMsgWeb( ['KILLTEST', { 'whom' : whom, 'reason': reason }] )
        return
    
    
    def evtTstKill(self, whom, reason=''):
        self._TstKill( whom, reason );
        return
  
    def handlerTstKillBTN(event):
        self._TstKill('Button', 'Killed at test station by "panic" button');
        return
  
    #---------

    def getCurrentState(self):
        return( [ 'stateUpdate', {
                    'usbHostDUT' : (not self.hwState.getUsbHost()),
                    'usbHostPC'  : (self.hwState.getUsbHost()),
                    'usbClientMulti' : self.hwState.getUsbClientMulti(),
                    'usbClientP1' : self.hwState.getUsbClientP1(),
                    'usbClientP2' : self.hwState.getUsbClientP2(),
                    'usbClientP3' : self.hwState.getUsbClientP3(),
                    'usbClientP4' : self.hwState.getUsbClientP4(),
                    'dutEthernet' : self.hwState.getDutEthernet(),
                    'dutWiu' : self.hwState.getDutWiu(),
                    'dutPower' : self.hwState.getDutPower(),
                    'tstRun' : self.hwState.getTstRun()
                }]
              )

    def sendWebCurrentState(self):
        self.putMsgWeb( self.getCurrentState() )
        
    def run(self):
        # called on start() signal
        try:
            self.logger.debug("Running HW process")

            # initialize Raspberry PI Hardware
            self.GPIO = RaspPi();

            # Reset hardware
            self.GPIO.initHW()

            # setup button event callbacks
            self.GPIO.addEventDetect(self.GPIO.dutPwrBTN, self.handlerDutPowerBTN);
            self.GPIO.addEventDetect(self.GPIO.usbMltBTN, self.handlerUsbMltBTN);
            self.GPIO.addEventDetect(self.GPIO.usbOneBTN, self.handlerUsbOneBTN);
            self.GPIO.addEventDetect(self.GPIO.usbTwoBTN, self.handlerUsbTwoBTN);
            self.GPIO.addEventDetect(self.GPIO.usbThrBTN, self.handlerUsbThrBTN);
            self.GPIO.addEventDetect(self.GPIO.usbForBTN, self.handlerUsbForBTN);
            self.GPIO.addEventDetect(self.GPIO.hostSwBTN, self.handlerHostBTN);
            self.GPIO.addEventDetect(self.GPIO.dutEthBTN, self.handlerDutEthBTN);
            self.GPIO.addEventDetect(self.GPIO.dutWiuBTN, self.handlerDutWiuBTN);
            self.GPIO.addEventDetect(self.GPIO.tstKilBTN, self.handlerTstKillBTN);

            while True:
                try:
                    # do run HW stuffs
                    # ----------------------

                    # check for messages from the WebService
                    if (not self.getMsg.empty()):
                    
                        self.msg = self.getMsg.get()
                        if not Global.__MULTIPROCESSING__:
                            self.getMsg.task_done()

                        self.logger.debug( 'HW : ' + str(self.msg) )
                        
                        event = self.msg['event']
                        type = self.msg['data']
                        
                        print '====================='
                        print event
                        print '======'
                        print type
                        print '====================='
                        
                        
                        if (event == 'usbHostDUT'):       self.evtHostDut(type)
                        elif (event == 'usbHostPC'):      self.evtHostPc(type)
                        elif (event == 'usbClientMulti'): self.evtUsbMlt(type)
                        elif (event == 'usbClientP1'):    self.evtUsbOne(type)
                        elif (event == 'usbClientP2'):    self.evtUsbTwo(type)
                        elif (event == 'usbClientP3'):    self.evtUsbThr(type)
                        elif (event == 'usbClientP4'):    self.evtUsbFor(type)
                        elif (event == 'dutEthernet'):    self.evtDutEth(type)
                        elif (event == 'dutWiu'):         self.evtDutWiu(type)
                        elif (event == 'dutPower'):       self.evtDutPower(type)
                        elif (event == 'tstRun'):         self.evtTstRun(type)
                        else:
                            self.logger.error( "WHHAAAAATTT ??????    HW ")

                    # HW butt presses hancled in callbacks
                    time.sleep(.2)

                except(KeyboardInterrupt, SystemExit):
                    self.logger.debug("Interupted HW process")
                    self.stop()
                    exit()

                except Exception as e:
                    self.logger.exception(e)

        except Exception as e:
            self.logger.exception(e)

    def stop(self):
        return

    #--------------------------

    def initHW(self):
        #self.parseConfig()
        return

    def parseConfig(self):
        self.config["asdf"] = 1




