#!/usr/bin/env python3

import Global

import datetime
import getopt
import inspect
import json
import os
import platform
import pyudev
import sys
import time
import threading


if Global.__MULTIPROCESSING__:
    import multiprocessing
    from multiprocessing import Queue
else:
    if sys.version_info[0] < 3:
        from Queue import Queue
    else:
        from queue import Queue

import Logger

starttime = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")


__version__ = "0.0.0.1"


#-----------------------
# shell cmds
def getFromShell_raw(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout.readlines()

def getFromShell(command):
    result = getFromShell_raw(command)
    for i in range(len(result)):       
        result[i] = result[i].strip() # strip out white space
    return result

#-----------------------
# drive mount/unmount
class storageDevice(object):
    def __init__(self, device):
        self.device = str(device)
        self.mount_point = None

    def as_string(self):
        return "%s -> %s" % (self.device, self.mount_point)

    def is_mounted(self):
        result = getFromShell('mount | grep ' + self.device)
        if result:
            dev, on, self.mount_point, null = result[0].split(' ', 3)
            return True
        return False

    def mount(self):
        if not self.is_mounted():
            result = getFromShell('udisks --mount ' + self.device)[0]
            if re.match('^Mounted',result): 
                mounted, dev, at, self.mount_point = result.split(' ')
        return self.mount_point

    def unmount(self):
        if self.is_mounted():
            result = getFromShell('udisks --unmount ' + self.device)
            self.mount_point = None

    def eject(self):
        if self.is_mounted():
            self.unmount()
        result = getFromShell('udisks --eject ' + self.device)
        self.mount_point = None

#-----------------------
class myApp(object):

    logQ = None
    logger = None
    logconfig = None

    pLG = None  # Logging thread
    
    pCA = None  # Camera thread/process
    pHW = None  # Hardware thread/process
    pWS = None  # WebServices thread/process
    pSC = None  # Serial Console thread/process

    def main(self, argv):
        # initialize logging
        if Global.__MULTIPROCESSING__:
            self.logQ = multiprocessing.Queue(-1)
        else:
            self.logQ = Queue(-1)

        self.pLG = threading.Thread(target=Logger.logger_thread, args=(self.logQ,))
        self.pLG.start()

        self.logger  = Logger.logging.getLogger(__name__)
        self.logconfig = Logger.logconfig
        self.logger.info("Start time: " + starttime)

        self.configFile = None

        # parse command line arguments
        try:
            opts, args = getopt.getopt(argv, "hd:", ["help", "desc="])
        except getopt.GetoptError as e:
            self.logger.exception(str(e))
            self.usage()
            return
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()
                return
            elif opt in ("-d", "--dfile"):
                self.configFile = arg
            else:
                self.usage()
                return

        if(self.configFile == None):
            self.usage()
            return

        # usb devices
        self.usbMon = None
        self.current_devices = {}
            
        # initilize and run
        self.initilize()
        self.start()
        self.stop()

    #-----------------------
    def initilize(self):
        try:
            # identify platform
            self.logger.info("------------------------------")
            self.logger.info("  machine: " + platform.machine())
            self.logger.info("  version: " + platform.version())
            self.logger.info(" platform: " + platform.platform())
            self.logger.info("   system: " + platform.system())
            self.logger.info("processor: " + platform.processor())
            if Global.__MULTIPROCESSING__:
                self.logger.info("    cores: " + str(multiprocessing.cpu_count()))
            self.logger.info("    nodes: " + platform.node())
            self.logger.info("PythonImp: " + platform.python_implementation())
            self.logger.info("PythonVer: " + platform.python_version())
            self.logger.info("starttime: " + starttime)
            self.logger.info("scriptver: " + __version__)
            self.logger.info("------------------------------")
            
            # include paths
            dirs = ['pythonLibs', 'Hardware', 'WebServices', 'Camera', 'SerialConsole']
            self.initPaths(dirs)

            # initialize queues
            if Global.__MULTIPROCESSING__:
                self.queCam = multiprocessing.Queue()
                self.queHdw = multiprocessing.Queue()
                self.queWeb = multiprocessing.Queue()
                self.queSer = multiprocessing.Queue()
            else:
                self.queCam = Queue()
                self.queHdw = Queue()
                self.queWeb = Queue()
                self.queSer = Queue()

            # hardware configuration
            self.configHW = {
                "HTTPPORT" : 8888,
                "SOCKETIOPORT" : 8888
            }

            # include configuation from file 
            data = self.readFile(self.configFile)
            self.configHW.update(data)
            
            print(self.configHW)
            
            # monitor usb for devices
            self.udevContext = pyudev.Context()
            self.udevMonitor = pyudev.Monitor.from_netlink(context)
            self.udevMonitor.filter_by(subsystem='usb', device_type='usb_device')
            #>>>>>> check to see if subsystem='block' is needed for flashdrives
            self.usbMon =  pyudev.MonitorObserver(self.udevMonitor, callback=process_device_event)
            self.usbMon.daemon = False
            
            # initialize camera process
            import Camera
            self.pCA = Camera.Camera(self.logger, self.logconfig, self.queCam, self.queHdw, self.queWeb, self.configHW)
            
            # initialize hardware process
            import Hardware
            self.pHW = Hardware.Hardware(self.logger, self.logconfig, self.queCam, self.queHdw, self.queWeb, self.configHW)

            # initialize web services process
            import WebServices
            self.pWS = WebServices.WebServices(self.logger, self.logconfig, self.queCam, self.queHdw,  self.queSer, self.queWeb, self.configHW)

            # initialize  process
            import SerialConsole
            self.pSC = SerialConsole.SerialConsole(self.logger, self.logconfig, self.queSer, self.queWeb, self.configHW)
            
        except Exception as e:
            self.logger.exception(e)

        return

    #-----------------------
    # json file methods
    
    def readFile(self, path):
        with open(path, 'r') as datafile:
            return(json.load(datafile))

    def writeFile(self, path, data):
        with open(path, 'w') as datafile:
            json.dump(data, datafile)

    #-----------------------
    # udev methods

    def process_device_event(device):
        log_device_event(device)
    
    def device_info(device):
        # return the attributes of a given device
        vendor = device['ID_VENDOR'].replace('_',' ')
        model = device['ID_MODEL'].replace('_',' ')
        try:
            serial = device['ID_SERIAL_SHORT']
        except:
            serial = device['ID_SERIAL']
        return({'vendor':vendor, 'model':model, 'serial':serial})
   
    def log_device_event(device):
        # log device to/from the dict of current devices
        devname = device['DEVNAME']
        if (device.action == 'add'):
            current_devices[devname] = device_info(device)
            self.logger.info('added : ' + devname)
        if (device.action == 'remove'):
            try:
                del current_devices[devname]
                self.logger.info('removed : ' + devname)
            except KeyError:
                self.logger.warn('Unable to remove : ' + devname)
                pass
        return(current_devices)
   
    def get_block_info(dev_name):
        dev = pyudev.Device.from_device_file(context, dev_name)
        self.logger.info('    Device name: %s' % dev.get('DEVNAME'))
        self.logger.debug('    Device type: %s' % dev.get('DEVTYPE'))
        self.logger.debug('     Bus system: %s' % dev.get('ID_BUS'))
        self.logger.info('Partition label: %s' % dev.get('ID_FS_LABEL'))
        self.logger.debug('             FS: %s' % dev.get('ID_FS_SYSTEM_ID'))
        self.logger.debug('        FS type: %s' % dev.get('ID_FS_TYPE'))
        self.logger.debug('   Device usage: %s' % dev.get('ID_FS_USAGE'))
        self.logger.debug('   Device model: %s' % dev.get('ID_MODEL'))
        self.logger.info(' Partition type: %s' % dev.get('ID_PART_TABLE_TYPE'))
        self.logger.debug('     USB driver: %s' % dev.get('ID_USB_DRIVER'))
        self.logger.debug('        Path id: %s' % dev.get('ID_PATH'))
        
        try:
            objProc = subprocess.Popen('lsblk --nodeps %s | grep -v SIZE  | awk \'{ print $4 }\'' % dev.get('DEVNAME'), shell=True, bufsize=0, executable="/bin/bash", stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = objProc.communicate()
            self.logger.info('       Capacity: %s' % out[0].strip())
        except OSError, e:
            self.logger.error(e)
   
    #-----------------------
    # file methods
    
    def dd_copy(self, dest, orig):
        # destination  ie "/dev/sda"
        with open(dest,'rb') as f:
            # origination  ie "~/image.dd"
            with open(orig, "wb") as i:
                while True:
                    if i.write(f.read(512)) == 0:
                        break
                        
    def verify_dd_copy(self, dest, orig):
        desthash = fileMd5(dest)
        orighash = fileMd5(dest)
        if(desthash == orighash):
            return True
        else:
            return False
        
    def fileMd5(filename, blocksize=2**20):
        m = hashlib.md5()
        with open(filename,'rb') as f:
            while True:
                buf = f.read(blocksize)
                if not buf:
                    break
                m.update( buf )
        return m.hexdigest()
    
    #-----------------------
    def start(self):
        try:
            # start camera process
            self.pCA.start()
            # start hardware process
            self.pHW.start()
            # start webservices process
            self.pWS.start()
            # start serialconsole process
            self.pSC.start()

            # monitor usb thread
            self.usbMon.start()
            
            RUNNING = True;
            
            while RUNNING:
                try:
                    time.sleep(0.200)
                    
                    # manage flash drive functions
                    
                    
                except (KeyboardInterrupt, SystemExit):
                    self.logger.info("Interrupted")
                    self.stop()
                    exit()
                except Exception as e:
                    self.logger.exception(str(e))

        except Exception as e:
            self.logger.exception(str(e))

    #-----------------------
    def stop(self):
        # stop processes
        if(self.pCA != None):
            self.pCA.stop()
        if(self.pHW != None):
            self.pHW.stop()
        if(self.pWS != None):
            self.pWS.stop()
        #console--   if(self.pSC != None):
        #console--       self.pSC.stop()

    #-----------------------
    def usage(self):
        print("\n\n python " + __file__ + " -d <config>.cfg \n")
        exit()

    #-----------------------
    def initPaths(self, dirs):

        try:
            # include <local> paths   NOTE: realpath() works with simlinks
            cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
            if cmd_folder not in sys.path:
                sys.path.insert(0, cmd_folder)
                self.logger.info("Path Added : " + cmd_folder)

            # include dirs passed
            for dir in dirs:
                cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], dir)))
                if cmd_subfolder not in sys.path:
                    sys.path.insert(0, cmd_subfolder)
                    self.logger.info("Path Added : " + cmd_subfolder)

        except Exception as e:
            self.logger.exception(str(e))
            raise


if __name__== '__main__':
    myApp().main(sys.argv[1:])

