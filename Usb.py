#!/usr/bin/env python3

import os
import pyudev


__version__ = "0.0.0.1"



#-----------------------
# shell cmds
def cmd_raw(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout.readlines()

def cmd(command):
    result = cmd_raw(command)
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
        result = cmd('mount | grep ' + self.device)
        if result:
            dev, on, self.mount_point, null = result[0].split(' ', 3)
            return True
        return False

    def mount(self):
        if not self.is_mounted():
            result = cmd('udisks --mount ' + self.device)[0]
            if re.match('^Mounted',result):
                mounted, dev, at, self.mount_point = result.split(' ')
        return self.mount_point

    def unmount(self):
        if self.is_mounted():
            result = cmd('udisks --unmount ' + self.device)
            self.mount_point = None

    def eject(self):
        if self.is_mounted():
            self.unmount()
        result = cmd('udisks --eject ' + self.device)
        self.mount_point = None

#-----------------------
# udev methods
class udevDevice(object):

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



