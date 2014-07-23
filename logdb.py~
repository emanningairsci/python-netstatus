"""
Handles logging information to MongoDB.
"""

from pymongo import MongoClient
from pymongo import ASCENDING
import math
import datetime
import config
import time


client = MongoClient('localhost', 27017)
db = client.netstatusDB
collection = db.log
collection.ensure_index([("timestamp", ASCENDING)])  


#|---------------------------------------------------------------------------------------
#| initDB: Clear all information from the 'log' and 'services' collection
#|----------------------------------------------------------------------------------------
def initDB():
    db.log.remove({})
    db.services.remove({})

#|-----------------------------------------------------------------------------------
#| minutes_to_DHM: a function translate the number of minutes given into a string of
#| days, hours and minutes. Returns a string.
#|-----------------------------------------------------------------------------------
def minutes_to_DHM(raw_minutes):
    raw_minutes = int(raw_minutes)
    days = math.floor(raw_minutes/24/60)
    raw_minutes = raw_minutes - days*60*24
    hours = math.floor(raw_minutes/60%24)
    raw_minutes = raw_minutes - hours*60
    minutes = raw_minutes
    if days == 1 and (hours > 1 or hours == 0) :
        time = "%s day, %s hours, and %s minutes" %(days, hours, minutes)
    elif hours == 1 and (days > 1 or days == 0) :
        time = "%s days, %s hour, and %s minutes" %(days, hours, minutes)
    elif hours == 1 and days == 1 :
        time = "%s day, %s hour, and %s minutes" %(days, hours, minutes)
    else :
        time = "%s days, %s hours, and %s minutes" %(days, hours, minutes)
    
    return time

#|-------------------------------------------------------------------------------------------------
#| read_hosts: a function to read the hosts stored in the 'log' collection of netstatusDB and pass
#| these names and their IP address to be used in config.py. Returns a matrix of hostnames and IPs:
#|
#| [ [hostname, IP], [another_host, another_IP], ... ]
#|-------------------------------------------------------------------------------------------------
def read_hosts():
    host_list = []
    host_data = []
    for host in db.log.find({}, {"hostname": 1, "IP": 1, "_id": 0}):
        try:
            host_data = [ str(host["hostname"]), str(host["IP"]) ]
            host_list.append(host_data)
        except LookupError:
            host__data = []
    
    return host_list


#|--------------------------------------------------------------------------------------------------
#| read_services: a function to read the service and service type associated with each host
#| returns a matrix of the form:
#|
#| [hostname, service name, service type], [hostname2, service name2 service type2], ... ]
#|--------------------------------------------------------------------------------------------------
def read_services():
    client = MongoClient('localhost', 27017)
    db = client.netstatusDB
    service_list = []
    service = []
    for data in db.services.find({}):
        hostname = str(data["hostname"])
        try:
            raw_service_data = data["services"]
        except LookupError:
            raw_service_data = []
        i = 0
        for service in raw_service_data:
            serv_name = str(raw_service_data[i]['name'])
            serv_type = str(raw_service_data[i]['type'])
            service = [hostname, serv_name, serv_type]
            service_list.append(service)
            i += 1

    return service_list


#|-----------------------------------------------------------------------------------------------------------
#| logDB: A function to create documents in the 'log' collection of the 'netstatusDB' database containing
#| information about each host's current status, downtime, uptime, and timestamp of the latest ping.
#|-----------------------------------------------------------------------------------------------------------
def logDB(status, hostname):
    """Log `status` to MongoDB log"""
    #| Update the status (online,offline) of the host
    #| If the host is online, increment its uptime value by the amount of time passed since the last check and reset the downtime counter to zero
    if status is True:    
        db.log.update(
            { "hostname": hostname },
            { '$set':{"hostname": hostname, "status": status, "downtime":0, "timestamp": datetime.datetime.now()}, '$inc':{"uptime":config.sleepTime / 60}},
            #| Set "upsert" to "True" in order to create a document if it doesn't already exist
            True
        )
    #| If it is not online, increment its downtime value by the amount of time passed since the last check and reset the uptime counter to zero
    if status is False:
        db.log.update(
            { "hostname": hostname },
            { '$set':{"hostname": hostname, "status": status, "uptime":0, "timestamp": datetime.datetime.now()}, '$inc':{"downtime":config.sleepTime / 60}},
            #| Set "upsert" to "True" in order to create a document if it doesn't already exist
            True
        )

#|-------------------------------------------------------------------------------------------------------
#|dailyDBSummary: This function is designed to create a summary table including each host's current
#|status and uptime. status.py calls this function at the end of each day to send the daily log reports
#|-------------------------------------------------------------------------------------------------------
def dailyDBSummary():

    client = MongoClient('localhost', 27017)
    db = client.netstatusDB
    collection = db.log
    summary_array = []
    host_data = []
    for host in db.log.find():
        host_data = [ str(host["hostname"]), str(host["status"]), str(host["uptime"]), str(host["downtime"]) ]
        summary_array.append(host_data)
    summary = ""
    for host in summary_array:
        if host[1] == "True":
            status = "online"
            time = minutes_to_DHM(host[2])
        elif host[1] == "False":
            status = "offline"
            time = minutes_to_DHM(host[3])
        summary += "Hostname:   %s \n" %host[0]
        summary += "\t Status:    %s \n" % status
        summary += "\t Up/Downtime:    %s \n\n" % time
        summary += "\r\n"
    return summary


#|--------------------------------------------------------------------------------------------------------------------------------------------------------------
#| logService: This function creates a document in the 'services' collection of the 'netstatusDB' database that contains information about
#| each host's monitored services. The list of services and their status are contained in a subdocument named 'services' and are of the format:
#|
#| {"_id" : ObjectID("..."), "hostname": "host", "services" : [ {"status": true, "uptime": 24, "type" "HTTP", "name" : "serv_1", "downtime" : 0}, ... ] } 
#|--------------------------------------------------------------------------------------------------------------------------------------------------------------
def logService(service, status, hostname):
    client = MongoClient('localhost', 27017)
    db = client.netstatusDB
    collection = db.services

    #| Make sure the host has been logged in this database collection before
    #| TODO: This could probably be simplified with some 'upsert' logic below
    host_in_DB = db.services.find({"hostname": hostname}).count()
    if host_in_DB == 0:
        db.services.insert({"hostname": hostname})

    #| if the service has been logged before, update its status. Otherwise create a new subdocument
    #| in 'services' for that host
    matching_service = db.services.find({ "hostname": hostname, "services.name": service }).count()
    if matching_service != 0:
        if status is True:
            db.services.update(
                {"hostname": hostname, "services.name": service},
                {'$set': {"services.$.status": status, "services.$.downtime": 0},
                '$inc': {"services.$.uptime": config.sleepTime / 60}}
            )
        elif status is False:
            db.services.update(
                {"hostname": hostname, "services.name": service},
                {'$set': {"services.$.status": status, "services.$.uptime": 0},
                '$inc': {"services.$.downtime": config.sleepTime / 60}}
            )
    else:
        if status is True:
            db.services.update(
                { "hostname": hostname},
                { '$push': {"services": {"name": service, "status": status, "uptime": config.sleepTime / 60, "downtime": 0} } }
            )
        elif status is False:
            db.services.update(
                { "hostname": hostname},
                { '$push': {"services": {"name": service, "status": status, "downtime": config.sleepTime / 60, "uptime": 0} } }
            )

#|--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#| logHistory: A function to log how long the host was up in each hour. Documents should be stored in the "history"
#| collection of the "netstatusDB" database.
#| Each document in this database will contain a "hostname" and "history" item and should be formatted like this:
#|              
#| {"_id": ObjectId("..."), "hostname" : "host", "history" : [ {"timestamp": 1404403200, "minutes": 45}, {"timestamp": 1404406800, "minutes": 60}, etc... ]}
#|
#| The timestamps should be in the Unix epoch format for use with cal-Heatmap (ex., 946753200 translates to 12:00:00 PM, Jan 1, 2000 MST)
#|--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def logHistory(status, hostname):

    client = MongoClient('localhost', 27017)
    db = client.netstatusDB
    collection = db.history

    #| create a timestamp for the current hour
    epoch_time = int(time.time())
    hour = int(time.strftime("%H"))
    day = int(time.strftime("%d"))
    month = int(time.strftime("%m"))
    year = int(time.strftime("%Y"))
    rounded_epoch = int(datetime.datetime(year, month, day, hour).strftime('%s'))

    #| Make sure the host has been logged in this database collection before
    host_in_DB = db.history.find({"hostname": hostname}).count()
    if host_in_DB == 0:
        db.history.insert({"hostname": hostname})

    #| If 'status' is 'true', the server is still online, then (config.sleepTime) minutes should be added
    #| to the total number of uptime minutes in that hour. We first need to make sure the timestamp exists in the
    #| database before we can increment it.

    timestamp_exists = db.history.find({"hostname": hostname, "history.timestamp": rounded_epoch}).count()    

    #| if the current timestamp does already exist in the DB, increment it's 'minutes' value
    #| by the appropriate amount (config.sleepTime or zero)
    if status is True and timestamp_exists != 0:
        db.history.update(
            {"hostname" : hostname, "history.timestamp": rounded_epoch }, {'$inc': {"history.$.minutes":config.sleepTime / 60} }
        )
    elif status is False and timestamp_exists != 0:
        db.history.update(
            {"hostname" : hostname, "history.timestamp": rounded_epoch }, {'$inc': {"history.$.minutes": 0} }
        )

    #| if the current timestamp does not already exist in the DB, create a record for that timestamp
    #| and assign the appropriate value to 'minutes'
    if status is True and timestamp_exists == 0:
        db.history.update(
            {"hostname": hostname}, {'$push': { "history": { "timestamp": rounded_epoch, "minutes":config.sleepTime / 60} } }
        )
    elif status is False and timestamp_exists == 0:
        db.history.update(
            {"hostname": hostname}, {'$push': { "history": { "timestamp": rounded_epoch, "minutes": 0} } }
        )
            
