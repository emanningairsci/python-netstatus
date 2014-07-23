#!/usr/bin/env python2
# Air Sciences network status checking script

import time
from netstatus import Online, Offline
import config
from log import Log
from logdb import logDB
from logdb import initDB
from logdb import logService
from logdb import logHistory
from logdb import dailyDBSummary 

def main():
    offCount = {}
    emailSent = False
    log = Log()
    config.hosts = config.refresh_hosts()

    #| Initialize offCount to 0
    for host in config.hosts:
        offCount[host] = 0

    #| Initialize 'log' and 'services' collection of the database
    #| (clears all information)

    #initDB()
     

    #| Loop forever and test all hosts.
    while True:
        print "Updating-------------"
        config.hosts = config.refresh_hosts()
        for host in config.hosts:
            offlineServices = checkHost(host, log)
            #| If services are offline, 
            if offlineServices != []:
                offCount[host] += 1
                #| Email an alert when the alertThreshold has been reached.
                if offCount[host] == config.alertThreshold:
                    time_offline = offCount[host]*(config.sleepTime/60) 
                    msg = "%s, or a service on it, appears to be offline and has not responded to %s consecutive pings. That's over %s minutes offline so far." % (host, offCount[host], time_offline)
                    config.email.send('%s is Offline - NetStatus Alert' % host,
                            config.emailAddress, msg)
                    log.write(msg)

            #| If services have gone from 'offline' to 'online', exception for newly added hosts
            try:
                if offlineServices == [] and offCount[host] >= config.alertThreshold:
                    time_offline = offCount[host]*(config.sleepTime/60)
                    msg = "The host %s has gone from 'offline' to 'online'. It spent up to %s minutes offline." %(host, time_offline)
                    config.email.send("%s is Online again - NetStatus Alert" %host,
                        config.emailAddress, msg)
                    log.write(msg)
                    offCount[host] = 0
            except LookupError:
                offCount[host] = 0

        #| Send stats at the end of each day.
        if getTime() >= config.emailTime and emailSent == False:
            summary_text = dailyDBSummary()
            summary_text += "\r\n \r\n \r\n Network status logs:\r\n \r\n%s" % log.read()
            config.email.send('Daily NetStatus Logs',
                    config.emailAddress, summary_text)
            log.empty()
            emailSent = True
        elif getTime() <= config.emailTime:
            emailSent = False

        #| Wait some time before checking all the hosts again.
        print "Waiting.................."
        time.sleep(config.sleepTime)


def checkHost(hostname, log):
    """Checks a given host's services and returns a list of offline
       services. If no services were offline, returns an empty list.
    """
    host = config.hosts[hostname]
    offlineServices = []
    status = host.getStatus() 
    if status == Offline:
        #log.add(status, hostname)
	logDB(status, hostname)
        logHistory(status, hostname)
        for service in host.getServices():
            status = False
            log.add(status, hostname, service)
            logService(service, status, hostname)
        return ["ping"]
    else:
	logDB(status, hostname)
        logHistory(status, hostname)

    for service in host.getServices():
        status = host.getService(service).getStatus()
        log.add(status, hostname, service)
        logService(service, status, hostname)
        if status == Offline:
            offlineServices += service
            response = host.getService(service).getResponse()
            if response == None:
                print "broken service %s.%s" % (hostname, service)
                continue
            for key in response:
                lines = str(response[key]).split('\n')
                for line in lines:
                   log.write("INFO: %s.%s.%s - %s" % (hostname, service,
                               key, line.strip('\r')))
    return offlineServices

def getTime():
    return int(time.strftime("%H%M%S"))

if __name__ == "__main__":
    main()
