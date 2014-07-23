"""
Log things to a file.
"""

import time
import os

from netstatus import Online, Offline
import config


class Log():
    def __init__(self):
        self.logFile = config.logFile
        self.log = open(self.logFile, "a+")

    def write(self, message):
        self.log.write("[%s] %s\r\n" % (time.asctime(), message))
        self.log.flush()

    def read(self):
        with open(self.logFile, 'rb') as f:
            return f.read()

    def add(self, status, host, service=None):
        if status == Online: status = "online"
        else: status = "offline"

        if service == None:
            self.write("%s appears to be %s (ping failed)." % (host,
                        status))
        else:
            self.write("The %s server on %s is %s." % (service, host,
                        status))

    def empty(self):
        self.log.close()
        os.remove(self.logFile)
        self.log = open(self.logFile, "a+")
