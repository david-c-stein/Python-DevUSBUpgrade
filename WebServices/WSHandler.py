import Global

import json
import time
import datetime
import os.path
import tornado.web
import tornado.websocket
from tornado.escape import json_encode, json_decode
from tornado.options import options
import uuid
import base64


def getClientID():
    return ('ID_' + str(uuid.uuid1()).replace('-',''))


class WSHandler(tornado.websocket.WebSocketHandler):

    logger = None
    
    clients = dict()
    master = ""

    # state from hw
    hwUsbHostDUT = False
    hwUsbHostPC = False
    hwUsbClientMulti = False
    hwUsbClientP1 = False
    hwUsbClientP2 = False
    hwUsbClientP3 = False
    hwUsbClientP4 = False
    hwDutEthernet = False
    hwDutWiu = False
    hwDutPower = False

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

    def initialize(self, logger, logconfig, queCam, queHdw, queSer, queWeb, config):

        self.logger = logger
        self.logconfig = logconfig
        self.config = config
        WSHandler.logger = self.logger

        self.logger.info("Initializing " + __file__)

        # message queues
        self.getMsg = queWeb
        self.putMsgSer = queSer.put
        self.putMsgCam = queCam.put
        self.putMsgHwd = queHdw.put

        # setup message handler
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=.2), self.msgHandler)

    #=============================================================

    def msgHandler(self):
    
        if not self.getMsg.empty():
            msg = self.getMsg.get()
            if not Global.__MULTIPROCESSING__:
                self.getMsg.task_done()
                
            if (msg != None):
                
                ##serial if (msg[0] == 'serial'):
                ##serial    WSHandler.sendAddData( msg );
            
                if (msg[0] == 'stateUpdate'):
                    WSHandler.hwUsbHostDUT = msg[1]['usbHostDUT']
                    WSHandler.hwUsbHostPC = msg[1]['usbHostPC']
                    WSHandler.hwUsbClientMulti = msg[1]['usbClientMulti']
                    WSHandler.hwUsbClientP1 =  msg[1]['usbClientP1']
                    WSHandler.hwUsbClientP2 = msg[1]['usbClientP2']
                    WSHandler.hwUsbClientP3 = msg[1]['usbClientP3']
                    WSHandler.hwUsbClientP4 = msg[1]['usbClientP4']
                    WSHandler.hwDutEthernet = msg[1]['dutEthernet']
                    WSHandler.hwDutWiu = msg[1]['dutWiu']
                    WSHandler.hwDutPower = msg[1]['dutPower']
                    
                    WSHandler.sendAllStatus();

        # continue message handler
        tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=.2), self.msgHandler)    
        
    #=============================================================

    def check_origin(self, origin):
        return True

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self, *args):
    
        # get client ip address
        x_real_ip = self.request.headers.get("X-Real-IP")
        self.ipAddr = x_real_ip or self.request.remote_ip  
        # Get unique client ID
        self.id = getClientID()
        
        #self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        WSHandler.clients[self.id] = {"id": self.id, "object": self}
        self.logger.info("Client added: id " + self.id + " IP addr: " + self.ipAddr)
        
        # update new client with the state of things
        self.sendStatus()
        self.sendImage()
        self.sendAlert( 'Welcome to DTS2', 'This is DTS2 located in the San Jose lab', 'Ok' )

    def on_close(self):
        if (WSHandler.master == self.id):
            WSHandler.master = ""
        if self.id in WSHandler.clients:
            del WSHandler.clients[self.id]
        self.logger.info("Client closed: id " + self.id + " IP address " + self.ipAddr)

    def sendImage(self):
        # opening the image file and encoding in base64
        if os.path.isfile("calibrate.jpg"):
            with open("calibrate.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
        else:
            with open("default.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())

        # sending the encoded image
        WSHandler.sendAllData(['calibrationImage', encoded_string.encode('utf8')])

    def on_message(self, message):
        self.logger.info("Client : " + self.id + " msg: " + message)
        self.msg = json_decode(message)

        # login message
        if (self.msg['event'] == 'login'):
            if(self.verifyLogin(self.msg)):
                if(WSHandler.master != ""):
                    # someone else has control
                    # ask are you really really sure
                    self.sendAlert( 'Login warning', 'Someone else is already logged into this system. Did you want to forcably take control?', 'Force')
                else:
                    WSHandler.master = self.id
                    WSHandler.sendAllStatus()
            else:
                self.sendAlert( 'Login warning', 'Incorrect username or password.', 'Ok')
        
        elif (self.msg['event'] == 'forceLogin'):
        
            # send message out to current master
            WSHandler.sendOneAlert(self, WSHandler.master, 'Losing control', 'Another user is forcing contol', 'Ok')
            
            WSHandler.master = self.id
            WSHandler.sendAllStatus()
        
        # get status message
        elif (self.msg['event'] == 'getStatus'):
            self.sendStatus()
            
        else:
            # all other message requre login
            if (WSHandler.master == self.id):

                ##serial if (self.msg['event'] == 'serial'):
                ##serial     # send data on to the serial console
                ##serial     self.putMsgSer( self.msg['data'] )
            
                if (self.msg['event'] == 'getCalibrationImage'):
                    # web calibration messages
                    self.sendImage();

                elif (self.msg['event'] == 'newCalibrationImage'):
                    # client request for new camera calibration image
                    self.logger.info("CAMERA CALIBRATING")
                    self.putMsgCam('calibrateCamera')

                elif (self.msg['event'] == 'calibPos'):
                    # regions message
                    self.logger.info( self.msg );
                    WSHandler.sendOthersData( self.id, ['calibPos', self.msg['data']] )
                    
                    data = self.msg['data'];
                    
                    regionName = data[0];
                    x = data[1];
                    y = data[2];
                    offsetX = data[3];
                    offsetY = data[4];
                    rotation = data[5];
                    skewX = data[6];
                    skewY = data[7];

                    topLeftX = data[8];
                    topLeftY = data[9];
                    topRightX = data[10];
                    topRightY = data[11];
                    bottomLeftX = data[12];
                    bottomLeftY = data[13];
                    bottomRightX = data[14];
                    bottomRightY = data[15];
                    
                    # pass position onto camera
                    self.putMsgCam( { 'event':'modifyRegion', 'data':{ 
                                        'regionName': regionName, 
                                        'topLeftX': topLeftX, 
                                        'topLeftY': topLeftY, 
                                        'bottomRightX': bottomRightX, 
                                        'bottomRightY': bottomRightY } } )
                    
                elif ((self.msg['event'] == 'usbHostDUT') or
                      (self.msg['event'] == 'usbHostPC') or
                      (self.msg['event'] == 'usbClientMulti') or
                      (self.msg['event'] == 'usbClientP1') or
                      (self.msg['event'] == 'usbClientP2') or
                      (self.msg['event'] == 'usbClientP3') or
                      (self.msg['event'] == 'usbClientP4') or
                      (self.msg['event'] == 'dutEthernet') or
                      (self.msg['event'] == 'dutWiu') or
                      (self.msg['event'] == 'dutPower')) :
                      
                    #-----------
                    #  button events to be passed on to HW
                    #  'usbHostDUT',  'usbHostPC', 'usbClientMulti', 'usbClientP1', 'usbClientP2'
                    #  'usbClientP3', 'usbClientP4', 'dutEthernet', 'dutWiu', 'dutPower'
                    #-----------
                    # send msg to the HW side
                    self.putMsgHwd( self.msg )
                    
                else:
                    self.logger.warn(' ??? ' + str(self.msg) )
                
            else:
                self.senddata( ["contStatus", "Not Logged In" ] )


    def senddata(self, a):
        self.write_message( json_encode(a) )
        
    @classmethod
    def sendAllData(cls, a):
        for c in cls.clients:
            cls.clients[c]['object'].senddata(a);
            
    @classmethod
    def sendOthersData(cls, id, a):
        for c in cls.clients:
            if cls.clients[c]['id'] != id:
                cls.clients[c]['object'].senddata(a);

    @classmethod
    def sendOneData(cls, id, a):
        for c in cls.clients:
            if cls.clients[c]['id'] == id:
                cls.clients[c]['object'].senddata(a);
                
    #---------------------------------------------------

    @classmethod
    def sendAllStatus(cls): 
        for c in cls.clients:
            x = ['stateUpdate', {
                    'usbHostDUT' : WSHandler.hwUsbHostDUT,
                    'usbHostPC'  : WSHandler.hwUsbHostPC,
                    'usbClientMulti' : WSHandler.hwUsbClientMulti,
                    'usbClientP1' : WSHandler.hwUsbClientP1,
                    'usbClientP2' : WSHandler.hwUsbClientP2,
                    'usbClientP3' : WSHandler.hwUsbClientP3,
                    'usbClientP4' : WSHandler.hwUsbClientP4,
                    'dutEthernet' : WSHandler.hwDutEthernet,
                    'dutWiu' : WSHandler.hwDutWiu,
                    'dutPower' : WSHandler.hwDutPower,
                    'control' : (WSHandler.master == WSHandler.clients[c]['id'])
                }]

            cls.clients[c]['object'].senddata(x)
        
    def sendStatus(self):
        # Send new client current state

        self.senddata( ['stateUpdate', {
                            'usbHostDUT' : WSHandler.hwUsbHostDUT,
                            'usbHostPC'  : WSHandler.hwUsbHostPC,
                            'usbClientMulti' : WSHandler.hwUsbClientMulti,
                            'usbClientP1' : WSHandler.hwUsbClientP1,
                            'usbClientP2' : WSHandler.hwUsbClientP2,
                            'usbClientP3' : WSHandler.hwUsbClientP3,
                            'usbClientP4' : WSHandler.hwUsbClientP4,
                            'dutEthernet' : WSHandler.hwDutEthernet,
                            'dutWiu' : WSHandler.hwDutWiu,
                            'dutPower' : WSHandler.hwDutPower,
                            'control' : (WSHandler.master == self.id)
                        }]
                     )

    
    def sendAllAlert(self, hdr, body, ftr='Ok'):
        WSHandler.senddata( ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] )

    def sendOthersAlert(self, id, hdr, body, ftr='Ok'):
        WSHandler.sendOthersData( id, ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] )

    def sendOneAlert(self, id, hdr, body, ftr='Ok'):
        WSHandler.sendOneData( id, ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] )
        
    def sendAlert(self, hdr, body, ftr='Ok'):
        self.senddata( ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] )        
        
        
                     
    def verifyLogin(self, msg):
        if(( msg['data'][0] == Global.__USERNAME__) and (msg['data'][1] == Global.__PASSWORD__)):
            return True
        else:
            return False
