#!/usr/bin/env python

try:
    import websocket
except ImportError:
    print "pip install websocket-client"
    
import thread
import time
import sys
import base64
import json
import ssl
import Logger
import threading


class WSClientConn():
 
    def __init__(self):
        self.callbacks = {}
        self.ws = None

    def connect(self, url):
        try:
            websocket.enableTrace(True)
            self.ws = websocket.WebSocketApp(
                    url,
                    on_message = self.on_message,
                    on_error = self.on_error,
                    on_close = self.on_close,
                    on_open = self.on_open
                )
            
            self.wsThread = threading.Thread(target=self.ws.run_forever, args=())  #  ping_interval=5,

            self.wsThread.deamon = True
            self.wsThread.start()
           
        except Exception as e:
            raise
            
    def disconnect(self):
        self.ws.close()

    #------------
 
    def on_message(self, ws, message):
        j = json.loads(message)
        self.dispatch(j[0], j[1])

    def on_close(self, ws):
        print("Connection Closed")
        self.dispatch('closed', None)
 
    def on_open(self, ws):
        print("Connection Opened")
        self.dispatch('opened', None)

    def on_error(self, ws, error):
        print("Connection ERROR")
        self.dispatch('error', error)
 
    def sendMsg(self, eventName, eventData):
        payload = json.dumps({'event': eventName, 'data': eventData })
        self.ws.send(payload)
 
    #------------
 
    def bind(self, eventName, callback):
        if(eventName not in self.callbacks):
            self.callbacks[eventName] = []
        self.callbacks[eventName].append(callback)
        
    def unbind(self, eventName, callback):
        del self.callbacks[eventName][callback]
        
    def dispatch(self, eventName, message):
        try:
            chain = self.callbacks[eventName]
            if(chain == None):
                return          # no callbacks for this event
            for cb in chain:
                cb(message)
                
        except Exception as e:
            print e

            
class ClientAutomation(object):

    UNKNOWN = 0
    DISCONNECTED = 1
    CONNECTED = 2
    CONTROL = 3
    ERROR = 4

    def __init__(self):
        self.iAmInControl = False
        self.usbHostDUT = False
        self.usbHostPC = False
        self.usbClientMulti = False
        self.usbClientP1 = False
        self.usbClientP2 = False
        self.usbClientP3 = False
        self.usbClientP4 = False
        self.dutEthernet = False
        self.dutWiu = False
        self.dutPower = False
        self.conn = None
        
    def __del__(self):
        if (self.conn != None):
            self.conn.disconnect()

    def connect(self):
        try:
            # connect to server
            self.conn = WSClientConn()

            # connection event bindings
            self.conn.bind('opened', ClientAutomation.connected)
            self.conn.bind('closed', ClientAutomation.disconnected)
            self.conn.bind('error',  ClientAutomation.error)
            
            # server bindings
            self.conn.bind('stateUpdate', self.stateUpdate)
            self.conn.bind('contStatus', self.contStatus)
            self.conn.bind('calibPos', self.calibPos)
            self.conn.bind('calibrationImage', self.saveImage)
            self.conn.bind('alert', self.alert)

            self.conn.connect("ws://127.0.0.1:8888/ws/")
          
            return True
            
        except Exception as e:
            print e
            return False
        
    def disconnect(self):
        if (self.conn != None):
            self.conn.disconnect()

    #----------

    @classmethod
    def connected(cls, event):
        cls.updateStatus(cls.CONNECTED)
        
    @classmethod
    def disconnected(cls, event):
        cls.updateStatus(cls.DISCONNECTED)

    @classmethod
    def error(cls, event):
        cls.updateStatus(cls.ERROR)

    @staticmethod
    def updateStatus(state):
        print(state)
    
    #----------
    
    def contStatus(self, data):
        ''' ["contStatus", "Not Logged In" ] '''
        print data
        
    def calibPos(self, data):
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
        print data
        
    def saveImage(self, data):
        fh = open("calibImg.png", "wb")
        fh.write(base64.decodestring( data )) 

    def alert(self, data):
        ''' ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}] '''
        print (' hdr: ' + data['hdr'])
        print ('body: ' + data['bdy'])
        
    def stateUpdate(self, data):
        # state message
        self.iAmInControl = data['control']
        self.usbHostDUT = data['usbHostDUT']
        self.usbHostPC = data['usbHostPC']
        self.usbClientMulti = data['usbClientMulti']
        self.usbClientP1 = data['usbClientP1']
        self.usbClientP2 = data['usbClientP2']
        self.usbClientP3 = data['usbClientP3']
        self.usbClientP4 = data['usbClientP4']
        self.dutEthernet = data['dutEthernet']
        self.dutWiu = data['dutWiu']
        self.dutPower = data['dutPower']
        
    #---------
    
    def login(self, username, password):
        self.conn.sendMsg('login', [username, password])
        
    def forceLogin(self):
        self.conn.sendMsg('forceLogin', None)
       
    def setUsbHostDUT(self):
        self.conn.sendMsg('usbHostDUT', 'On')
        
    def setUsbHostPC(self):
        self.conn.sendMsg('usbHostPC', 'On')
        
    def setUsbClientMulti(self, value):
        self.conn.sendMsg('usbClientMulti', value)
        
    def setUsbClientP1(self, value):
        self.conn.sendMsg('usbClientP1', value)
        
    def setUsbClientP2(self, value):
        self.conn.sendMsg('usbClientP2', value)

    def setUsbClientP3(self, value):
        self.conn.sendMsg('usbClientP3', value)

    def setUsbClientP4(self, value):
        self.conn.sendMsg('usbClientP4', value)

    def setDutEthernet(self, value):
        self.conn.sendMsg('dutEthernet', value)

    def setDutWiu(self, value):
        self.conn.sendMsg('dutWiu', value)

    def setDutPower(self, value):
        self.conn.sendMsg('dutPower', value)

    def setTstRun(self, value):
        self.conn.sendMsg('tstRun', value)


def main():

    ca = ClientAutomation()
    
    print 'starting ws conenction'
    ca.connect()
    time.sleep(4)

    ca.login('qa', 'test')
    time.sleep(2)
  
    ca.forceLogin()
    time.sleep(2)
    
    ca.setUsbHostDUT()
    time.sleep(1)
        
    ca.setUsbHostPC()
    time.sleep(1)

    value = 'On'
    ca.setUsbClientMulti(value)
    time.sleep(1)
    ca.setUsbClientP1(value)
    time.sleep(1)
    ca.setUsbClientP2(value)
    time.sleep(1)
    ca.setUsbClientP3(value)
    time.sleep(1)
    ca.setUsbClientP4(value)
    time.sleep(1)

    value = 'Off'
    ca.setUsbClientMulti(value)
    time.sleep(1)
    ca.setUsbClientP1(value)
    time.sleep(1)
    ca.setUsbClientP2(value)
    time.sleep(1)
    ca.setUsbClientP3(value)
    time.sleep(1)
    ca.setUsbClientP4(value)
    time.sleep(1)
    
    value = 'On'
    ca.setUsbClientMulti(value)
    time.sleep(1)
    ca.setUsbClientP1(value)
    time.sleep(1)
    ca.setUsbClientP2(value)
    time.sleep(1)
    ca.setUsbClientP3(value)
    time.sleep(1)
    ca.setUsbClientP4(value)
    time.sleep(1)
    
   
    value = 'On'
    ca.setDutEthernet(value)
    time.sleep(1)
    ca.setDutWiu(value)
    time.sleep(1)
    
    value = 'Off'
    ca.setDutEthernet(value)
    time.sleep(1)
    ca.setDutWiu(value)
    time.sleep(1)

    ca.setDutPower('On')
    time.sleep(1)
    ca.setDutPower('Off')
    time.sleep(1)
    ca.setDutPower('On')
    time.sleep(1)
    ca.setDutPower('Off')
    time.sleep(1)

    ca.setTstRun('On')
    time.sleep(1)
    
    
    
    print 'stopping ws connection'
    ca.disconnect()


if __name__ == '__main__':
    main()
