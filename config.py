"""
Configuration for the network status tool.
"""

#from netstatus.host import Host
from host import Host
from netstatus.services.httpserver import HTTPServer
from netstatus.services.httpsserver import HTTPSServer
from netstatus.services.mssqlserver import MSSQLServer
from netstatus.services.pgsqlserver import PGSQLServer
from mail import Email
import status
import getpw
import logdb

#| How long should we wait between each round of pings? (Seconds)
sleepTime = 5*60

#| Where should the logs be stored during the day? (Note: the log file
#| will be deleted at the end of the day, after it has been emailed out
#| to the AirSci netadmin address.
logFile = '/tmp/airsci_network_status.log'

#| Email settings.
email = Email()
emailAddress = 'noone@mail.com'
emailTime = 170000 # In 24-hour HHMMSS format (localtime).

#| Alert threshold - how many successive rounds of tests must a service fail
#| before an email alert is sent out?
alertThreshold = 3


#| Add hosts to be monitored with their respective services
#| TODO: Adjust format for adding HTTPS, PGSQL, MSSQL, and SQL services 
def refresh_hosts():
    host_array = logdb.read_hosts()
    count = 0
    hosts = {}
    while count < len(host_array):
        name = str(host_array[count][0])
        ip = Host(str(host_array[count][1]))
        hosts[name] = ip
        count += 1

    services = logdb.read_services()
    for service in services:
        hostname = service[0]
        service_name = str(service[1])
        service_type = str(service[2])
        if service_type == "HTTP":
            hosts[hostname].addService(service_name, HTTPServer(hosts[hostname]))
        elif service_type == "HTTPS":
            hosts[hostname].addService(service_name, HTTPSServer(hosts[hostname]))
        #elif service_type == "SQL":
        #   hosts[hostname].addService(hostname, SQLServer(hosts[hostname]))
        elif service_type == "MSSQL":
            hosts[hostname].addService(service_name, MSSQLServer(hosts[hostname]))
        elif service_type == "PGSQL":
            hosts[hostname].addService(service_name, PGSQLServer(hosts[hostname]))


    return hosts



#| Add hosts in the format below.
#| hosts = {'hostname': Host('IP_ADDR'), 'another_host': Host('IP_ADDR'), ...}

#| Add services in the format below.
#| hosts['hostname'].addService('service_name', HTTPServer(hosts['hostname'], path="")
#| hosts['hostname'].addService('service_name', HTTPSServer(hosts['hostname'], path="", hostname="")
#| hosts['hostname'].addService('service_name', SQLServer(hosts['hostname'])
#| hosts['hostname'].addService('service_name', MSSQLServer(hosts['hostname'], user="", password="", database="")
#| hosts['hostname'].addService('service_name', PGSQLServer(hosts['hostname'], user="", password="", database="")

