
import Global

if Global.__MULTIPROCESSING__:
    import multiprocessing

import os
import tornado.web

import IndexHandler
import WSHandler



class UploadHandler(tornado.web.RequestHandler):
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

    def initialize(self, logger, logconfig):
        self.logger = logger
        self.logconfig = logconfig

    def post(self):
        file_contents = self.request.files['file'][0].body
        with open("uploads/file", "wb") as f:
            f.write(file_contents)
        self.finish()

        

# HTTP Web Service
class HTTPHandler( tornado.web.Application ):

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
        
        self.logger = logger
        self.logconfig = logconfig
        self.config = config

        self.logger.info("Initializing " + __file__)

        # message queues
        self.queCam = queCam
        self.queHdw = queHdw
        self.queSer = queSer
        self.queWeb = queWeb
    
        self.static_dir = os.path.join(self.config["DIRNAME"], "static")
        self.static_dir_dict = dict(path=self.static_dir)

        self.address = self.config["IPADDRESS"]
        self.port = self.config["SOCKETIOPORT"]

        # define handlers
        self.handlers = [
            # public
            (r'/', IndexHandler.IndexHandler, dict(logger=self.logger, logconfig=self.logconfig, address=self.address, port=self.port)),
            (r'/ws/(.*)', WSHandler.WSHandler, dict(logger=self.logger, logconfig=self.logconfig, queCam=self.queCam, queHdw=self.queHdw, queSer=self.queSer, queWeb=self.queWeb, config=self.config)),
            (r'/file-upload', UploadHandler,  dict(logger=self.logger, logconfig=self.logconfig)),
            #(r'/api', ApiHandler.ApiHandler, dict(logger=self.logger, logconfig=self.logconfig, queCam=self.queCam, queHdw=self.queHdw, queSer=self.queSer, queWeb=self.queWeb, config=self.config)),
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path" : 'static/favicon.ico'}),
            (r'/(.*.js)', tornado.web.StaticFileHandler, {"path" : 'static/assets/js/.*.js'})
        ]
        
        self.settings = dict(
            debug=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )

        tornado.web.Application.__init__(self, handlers=self.handlers, default_host="", transforms=None, **self.settings)



