#!/usr/bin/env python

import Global

if Global.__MULTIPROCESSING__:
    import multiprocessing

'''
    Primary reason for choosing pygame
    
                     2.7  3.2  3.3  3.4  LINUX  WIN32
    -------------------------------------------------------
        OpenCV       YES   -    -    -   YES    YES
        PyGame       YES  YES  YES  YES  YES    YES
        SimpleCV     YES   -    -    -   YES    YES
        VideoCapture YES   -    -    -    -     YES
'''

'''
    Events defined

                t1    t2    t3    t4    t5    t6 ...
        none |  
       Grnen |  ------      ------      ------
       Amber |        ------      ------      ------
         Red |
         
         
              1)  green 3s,  amber 3s, cont
              2)  green .5s, amber .5s, cont 
              3)  amber 3s, off 1s, cont

              '''

import sys
import math
import pygame
import pygame.camera
from pygame.locals import *
import threading
import time
from tornado.escape import json_encode, json_decode


if Global.__MULTIPROCESSING__:
    import multiprocessing
    

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    if sys.version_info < (3, 4):
        # On most other platforms the best timer is time.time()
        default_timer = time.time
    else:
        # Python3.4 this has become
        default_timer = time.perf_counter


''' 
    subclass list so that it only keeps a max number of values
        -- currently hardcoded to 20
'''

class L(list):

    LISTLEN = 20

    def append(self, item):
        list.append(self, item)
        if len(self) > LISTLEN: 
            self[:1]=[]


class Camera(multiprocessing.Process if Global.__MULTIPROCESSING__ else threading.Thread):
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
            super(Camera, self).__init__()

        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.logger.info("Initializing " + __file__)

        # message queues
        self.getMsg = queCam
        self.putMsgWeb = queWeb.put
        self.putMsgHdw = queHdw.put

        
        # initialize camera
        pygame.camera.init()
        
        # configure camera
        #self.size = (320,240)
        self.size = (640,480)
        
        # gets a list of available cameras.
        self.cameras = pygame.camera.list_cameras()
        if not self.cameras:
            self.logger.error("No cameras detected")
            raise ValueError("No cameras detected")

        # get first camera with specified size and RGB colorspace
        self.camera = pygame.camera.Camera(self.cameras[0], self.size, "RGB")
        self.camera.start()
        self.clock = pygame.time.Clock()
        
        self.img = pygame.Surface(self.size)
        self.imgTime = 0
        self.FPS = 5
        self.loopDelta = 1.0 / self.FPS
       
        self.calibrate = False
        self.monitoring = False
        self.regions = ()
        self.msg = None
        return

    def queryImage(self):
        # check to see if an image is ready
        return self.camera.query_image()
        
    def getImage(self, img):
        self.camera.get_image(img)
        return
        
    def getRaw(self):
        return self.camera.get_raw()

    def saveImage(self, img, filename, caption=""):
        pygame.image.save(img, filename)
        return
        
    def getControls(self):
        return self.camera.get_controls()
        
    def setControls(self, hflip=False, vFlip=False, brightness=255):
        return self.camera.set_controls()
        
    def getSize(self):
        return self.camera.get_size()    
        
    #----------
        
    def processRegions(self, img, region):
        #    https://en.wikipedia.org/wiki/RGB_color_space
    
        rSum = 0.0
        gSum = 0.0
        bSum = 0.0
    
        # sum pixels in region
        for x in range(region.location.x1, region.location.x2 + 1):
            for y in range(region.location.y, region.location.y2 + 1):
                r, g, b = img[x,y]
                rSum = rSum + r
                gSum = gSum + g
                bSum = bSum + b
                
        # basic averaging
        c = ((region.location.x2 - region.location.x1) * (region.location.y2 - region.location.y1))
        rAve = int(rSum / c)
        gAve = int(gSum / c)
        bAve = int(bSum / c)

        # For our evil purposes we are only intested in 
        # the LED states : Off, Green, Amber, Red, White
        AMBER = { 'name' : 'amber', 'red' : 255, 'green' : 191 , 'blue' : 0   }
        RED   = { 'name' : 'red',   'red' : 255, 'green' : 0 ,   'blue' : 0   }
        GREEN = { 'name' : 'green', 'red' : 0,   'green' : 255 , 'blue' : 0   }
        WHITE = { 'name' : 'white', 'red' : 255, 'green' : 255 , 'blue' : 255 }
        COLORS = [AMBER, RED, GREEN, WHITE]

        self.logger.info(COLORS)
        
        colorThreshold = 64

        colorName = None
        
        # Basic color matching 
        for color in range(COLORS): 
            dRed = color.red = rAve
            dGreen = color.green - gAve
            dblue = color.blue - bAve
        
            # length of difference vector
            length = math.sqrt( (d_red * d_red) + (d_green * d_green) + (d_blue * d_blue) )
        
            if length < colorThreshold:
                colorName = color.name
                break
        
        # check for events
        self.processEvents(region, colorName, imgTime)

        
    def processEvents(self, region, colorName, imgTime):

        '''
            examples:
            LED flashes alternating amber and green every 3 seconds
            { 'id01' : [{'amber', 3}, {'green', 3}] }
        
            LED flashes alternating amber and green rapidly
            { 'id02' : [{'amber', 0.5}, {'green', 0.5}] }

            LED flashes alternating amber 3 seconds and off 1 second
            { 'id03' : [{'amber', 3}, {'none', 1}] }

            LED steady green for 2 minutes
            { 'id04' : [{'green', 120}] }

            LED off for 5 minutes
            { 'id05' : [{'none', 300}] }
            
            When pattern is identified a message is returned with the ID
            
            ------------------------------------------
            
            Region 1:      t5    t4    t3    t2    t1 --> t -->
                history  | c,t | c,t | c,t | c,t | c,t | c,t |...| c,t |
          event pattern  | c,t | c,t |

        '''
    
        # check to see if there has been a change
        if( region['hist'][0].c != colorName ):
        
            # Something new has happened in this region
            # REMINDER: L list only keeps the last L.LISTLEN entries.
            region['hist'].append({'c': colorName, 't':imgTime})
            
            #--------------------------
            # check event patterns for a match
            for pattern in region.events.patterns:
                match = False
                timeThreshold = 0.5
                dTime = 0.0
           
                # check color pattern
                for i in length(pattern):
                    if (pattern[i].c != region.hist[i].c):
                        match = False
                        break
                            
                    # probably should loop through patter if pattern started 
                    # in a different spot in sequence until it is started
                            
                    # sum time differences squared
                    dT = pattern[i].t - region.hist[i].t
                    dTime += (dT * dT)
    
                # length of difference vector
                length = math.sqrt( dTime )
                if (length < timeThreshold):
                    match = True
            
                if (match == True):

                    # pattern stop
                    if region.currentPattern != None:
                        # send event msg to web
                        putMsgWeb( ['camera', { 'region': region.regionName, 'id': region.currentPattern, 'type': 'stop', 'time': imgTime }] )
                
                    # pattern start
                    region.currentPattern = pattern.id
        
                    # send event msg to web
                    putMsgWeb( ['camera', { 'region': region.regionName, 'id': region.currentPattern, 'type': 'start', 'time': imgTime }] )

                else:
                
                    # no pattern matches - just send the current color
                    putMsgWeb( ['camera', { 'region': region.regionName, 'color': colorName, 'time': imgTime }] )

                    
        #--------------------------
        # check color durations for a match
        for durat in region.events.durations:
            # check color 
            
            # check times
        
            # send event msg to web
            putMsgWeb( ['camera', { 'region': region.regionName, 'id': eventID, 'time': imgTime }] )


    def addRegion(self, data):
        self.regions.append({
                'regionName' : data[0],
                'hist' : L(), 
                'topLeftX' : data[1],
                'topLeftY' : data[2],
                'bottomRightX' : data[3],
                'bottomRightY' : data[4],
                'events' : L()
            })
        pass
        
    def delRegion(self, name):
        self.regions[name] = []
                
    def modRegion(self, data):
        pass
        
    def addEvent(self, data):
        pass        

    def delEvent(self, ):
        pass        
        
    def run(self):
        # called on start() signal
        try:
            self.logger.info("Running Camera process")
            
            while True:
                try:
                    # --------------------------------
                    # check for messages from the WebService
                    if (not self.getMsg.empty()):
                        self.msg = self.getMsg.get()
                        if not Global.__MULTIPROCESSING__:
                            self.getMsg.task_done()

                        if (self.msg != None):
                            # add region
                            if (self.msg['event'] == 'addRegion'):
                                addRegion( self.msg['data'] )
                                
                            # remove region
                            if (self.msg['event'] == 'delRegion'):
                                self.delRegion( self.msg['data'].name )
                                
                            # modify region
                            if (self.msg['event'] == 'modifyRegion'):
                                self.modRegion( self.msg['data'] )
                             
                            # add event
                            if (self.msg['event'] == 'addEvent'):
                                self.eventsToWatchFor.add( self.msg['data'] )

                            # remove event
                            if (self.msg['event'] == 'delEvent'):
                                addEvent( self.msg['data'] )

                            # start monitoring the camera
                            if (self.msg['event'] == 'startMonitoring'):
                                self.monitoring = True

                            # stop monitoring the camera
                            if (self.msg['event'] == 'stopMonitoring'):
                                self.monitoring = False
                                
                            # calibrate the camera
                            if (self.msg['event'] == 'calibrateCamera'):
                                self.calibrate = True
                    
                    # calibrate camera
                    if ( self.calibrate == True ):
                        filename = 'calibrate.jpg'
                        self.getImage(self.img)
                        self.saveImage( self.img, filename )
                        self.putMsgWeb( ['calibrate', {'filename': filename}] )
                        self.calibrate = False
                        
                    # activily watching LEDs
                    if ( self.monitoring == True ):
                        
                        # grab an image from the camera
                        self.getImage(self.img)
                        self.imgTime = default_timer()

                        # process image data within each region
                        for region in self.regions:
                            self.processRegions(self.img, self.region)

                        # get metrics
                        self.clock.tick()
                        #self.logger.info('FPS: ' + str(self.clock.get_fps()))

                        #-------------------------------------
                        # compute time may vary, throttle to keep FPS consistent
                        sleepTime = self.loopDelta - (default_timer() - self.imgTime)
                        if sleepTime > 0:
                            time.sleep(sleepTime)
                        else:
                            self.logger.warn(" CAMERA: Things may be taking too long - FPS: " + str(self.clock.get_fps()))
                   
                    else:
                        time.sleep(.2)

                except(KeyboardInterrupt, SystemExit):
                    self.logger.info("Interupted HW process")
                    self.stop()
                    exit()

                except Exception as e:
                    self.logger.exception(e)

        except Exception as e:
            self.logger.exception(e)

    def stop(self):
        self.camera.stop()
        return



