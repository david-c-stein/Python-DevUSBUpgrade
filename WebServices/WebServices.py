#!/usr/bin/env python

import Global

if Global.__MULTIPROCESSING__:
    import multiprocessing

import os
import platform
import socket
import sys
import threading
import tornado.httpserver
import tornado.ioloop

from subprocess import *


class WebServices(multiprocessing.Process if Global.__MULTIPROCESSING__ else threading.Thread):

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

    def __init__(self, logger, logconfig, queCam, queHdw, queSer, queWeb, config):
        if Global.__MULTIPROCESSING__:
            #-- multiprocessing
            multiprocessing.Process.__init__(self)
        else:
            #-- threading
            super(WebServices, self).__init__()

        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.logger.info("Initializing " + __file__)

        # message queues
        self.queCam = queCam
        self.queHdw = queHdw
        self.queSer = queSer
        self.queWeb = queWeb

        if os.name == "nt":
            # windows
            self.config["IPADDRESS"] = socket.gethostbyname(socket.gethostname())
        else:
            # linux
            self.config["IPADDRESS"] = self.get_ip_address("eth0")


    def run(self):
        # called on start() signal
        try:
            self.logger.info("Running Web process")

            # Identify network information
            self.config["DIRNAME"] = os.path.dirname(__file__)
            self.logger.info("IPAddress: " + str(self.config["IPADDRESS"]))
            self.logger.info("HTTPport: " + str(self.config["HTTPPORT"]))
            self.logger.info("SocketIOport: " + str(self.config["SOCKETIOPORT"]))

            # HTTP Web and WebSocket servers
            import HTTPHandler
            http_server = tornado.httpserver.HTTPServer( HTTPHandler.HTTPHandler(self.logger, self.logconfig, self.queCam, self.queHdw, self.queSer, self.queWeb, self.config) )
            http_server.listen(self.config["HTTPPORT"])

            #Error handler
            import ErrorHandler
            
            # Get it all running
            #tornado.ioloop.IOLoop.instance().start()
            tornado.ioloop.IOLoop.current().start()

        except(KeyboardInterrupt, SystemExit):
            self.logger.info("Interupted HW process")
            self.stop()
            exit()

        except Exception as e:
            self.logger.exception(e)

    def stop(self):
        return

    def get_ip_address(self, ifname):
        
        if platform.system() == "Linux":
            
            # linux
            if sys.version_info[0] < 3:

                # RaspberryPi
                # :o(
                
                cmd = "ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1"
                p = Popen(cmd, shell=True, stdout=PIPE)
                output = p.communicate()[0]
                return output.replace('\n', '').replace('\r','')

                # python 2
                #import fcntl
                #import struct
                #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #return socket.inet_ntoa( fcntl.ioctl(
                #        s.fileno(),
                #        0x8915, # SIOCGIFADDR
                #        struct.path('256s', ifname[:15])
                #    )[20:24])
            else:
                # python 3
                return socket.gethostbyname(socket.getfqdn())
            
        else:
            # windows
            import netifaces as ni
            ip = ni.ifaddresses(ifname)[2][0]['addr']
            return ip


