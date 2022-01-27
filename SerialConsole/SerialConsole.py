#!/usr/bin/env python

import Global

if Global.__MULTIPROCESSING__:
    import multiprocessing

import os
import sys
import time
import platform
import serial
import string
import threading
import thread
import Queue

class Serial(serial.Serial):

    def __init__(self, serial_pt, baudrate = 115200, timeout=1):
        self.ser = None

        try:
            self.ser = serial.Serial(
                    port = serial_pt,
                    baudrate = baudrate,
                    bytesize = serial.EIGHTBITS,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    timeout = timeout,
                    xonxoff = False,
                    rtscts = False,
                   )

            # setup data queues
            self.send_q  = Queue.Queue()
            self.response_q = Queue.Queue()
            self.callback_q = Queue.Queue()

            self.alive = True

            # start read thread
            try:
                self.read_thread = threading.Thread(target=self.reader)
                self.read_thread.setDaemon(True)
                self.read_thread.start()
            except thread.error:
                print("Thread reader error")
                raise

            # start send thread
            try:
                self.send_thread = threading.Thread(target=self.writer)
                self.send_thread.setDaemon(True)
                self.send_thread.start()
            except thread.error:
                print("Thread writer error")
                raise

        except serial.serialutil.SerialException:
            # no serial connection
            self.ser = None
            print("Serial port open failed")
            raise

    def isOpen(self):
        return self.ser.isOpen()

    def __del__(self):
        self.alive = False
        if self.read_thread:
            self.read_thread.join()
            self.read_thread = None
        if self.send_thread:
            self.send_thread.join()
            self.send_thread = None
        self.ser.close()

    def reader(self):
        try:
            self.callbackEnable = False

            while self.alive:
                data = ""
                newline_seen = False

                # read a line - filtering characters as we go
                while not newline_seen and self.alive:
                
                    single_data = self.ser.read(1)
                    
                    '''
                    if (single_data == '\x80'):
                        # ok, seen from bootloader on reset
                        continue
                    elif (single_data == '\r'):
                        # strip \r characters
                        continue
                    elif (single_data == ''):
                        # timeout
                        continue
                    elif (single_data == '\n'):
                        # strip newline and use to end loop
                        newline_seen = True
                    elif (ord(single_data) < 128):
                        # copy alphanumeric characters
                        data += single_data
                    else:
                        data += '<%d>' % ord(single_data)
                    '''

                #print "<< " + data

                if self.callbackEnable:
                    self.callback_q.put(data)
                else:
                    self.response_q.put(data)

        except serial.SerialException:
            self.alive = False;
            print ("No USB connection")
            raise
        except serial.SerialTimeoutException:
            self.alive = False;
            print ("Connection timeout")
            raise
        except (KeyboardInterrupt, SystemExit):
            self.alive = False;
            self.ser.close()
            raise
        except Exception, err:
            self.alive = False;
            print ("ERROR: %s\n" % str(err))
            raise

    def writer(self):
        try:
            while self.alive:
                data = self.send_q.get()
                self.ser.write(data)
                self.ser.flush()
                self.send_q.task_done()
        except (KeyboardInterrupt, SystemExit):
            self.alive = False;
            self.ser.close()
            raise
        except Exception, err:
            self.alive = False;
            print ("ERROR: %s\n" % str(err))
            raise

    def read(self, timeout=1):
        # read from the response queue
        try:
            data = self.response_q.get(True, timeout)
            self.response_q.task_done()
        except Queue.Empty:
            data = ""
        return data

    def send(self, data):
        # put data in send queue
        self.send_q.put(data)
        return

    class callback(threading.Thread):
        def __init__(self, _sp, _function, args=None):
            threading.Thread.__init__(self)
            self.sp = _sp
            self.function = _function
            # controls the while loop in the run command
            self.alive = False

        def run(self):
            self.alive = True
            self.sp.callbackEnable = True
            try:
                while self.alive and self.sp.callbackEnable:
                    try:
                        data = self.sp.callback_q.get(True, timeout=1)
                        self.function(data)
                        self.sp.callback_q.task_done()
                    except Queue.Empty:
                        data = ""
                    except (KeyboardInterrupt, SystemExit):
                        return;
            except (KeyboardInterrupt, SystemExit):
                return;

        def stop(self):
            self.sp.callbackEnable = False
            self.alive = False

        def __del__(self):
            self.sp.callbackEnable = False
            self.alive = False
            self.join()



class SerialConsole(multiprocessing.Process if Global.__MULTIPROCESSING__ else threading.Thread):

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

    def __init__(self, logger, logconfig, queSer, queWeb, config):
        if Global.__MULTIPROCESSING__:
            #-- multiprocessing
            multiprocessing.Process.__init__(self)
        else:
            #-- threading
            super(SerialConsole, self).__init__()

        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.logger.info("Initializing " + __file__)

        # message queues
        self.getSer = queSer
        self.putMsgWeb = queWeb.put

        #TODO == put settings in config
        if platform.system() == "Linux":
            self.SERIAL_PORT = '/dev/ttyUSB0'
        else:
            self.SERIAL_PORT = 'COM1'

        self.SERIAL_BAUDRATE = 115200

        
    def myCallback(data):
        self.putMsgWeb(['serial', data])
        
        
    def run(self):
        # called on start() signal
        try:
            self.logger.info("Running Serial Console process")
            
            self.sp = Serial(self.SERIAL_PORT, self.SERIAL_BAUDRATE, timeout=1)
            self.cb = self.sp.callback(sp, myCallback)
            self.cb.start()
            
            while True:
                try:
                    # check for messages from the WebService
                    if (not self.getSer.empty()):
                        msg = self.getSer.get()
                        if not Global.__MULTIPROCESSING__:
                            self.getSer.task_done()
                        
                        # send it to the serial device
                        self.writeSerial(data)
                            
                except(KeyboardInterrupt, SystemExit):
                    self.logger.info("Interupted HW process")
                    self.cb.stop()
                    self.stop()
                    exit()

                except Exception as e:
                    self.cb.stop()
                    self.stop()
                    self.logger.exception(e)

        except Exception as e:
            self.logger.exception(e)

    def stop(self):
        return
                            