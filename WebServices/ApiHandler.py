import Global

import json
import time
import datetime
import os.path
import tornado.web
from tornado.escape import json_encode, json_decode
from tornado.options import options
import uuid
import base6


class ApiHandler(tornado.web.RequestHandler):

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

    #=============================================================

    @web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": id, "value" : value}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self):
        pass
