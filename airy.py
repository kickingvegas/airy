#!/usr/bin/env python3
import os
import sys
import argparse
import requests
from datetime import datetime
from pytz import timezone
import pytz
from functools import reduce
import sqlite3
from statistics import mean
import aqi
import json


fieldMap = {
    'ID': 'sensorID',
    'Label': 'label',
    'DEVICE_LOCATIONTYPE': 'deviceLocationType',
    'Lat': 'lat',
    'Lon': 'lon',
    'PM2_5Value': 'pm2_5Value',
    'LastSeen': 'lastSeen',
    'Type': 'type',
    'Hidden': 'hidden',
    'Version': 'version',
    'LastUpdateCheck': 'lastUpdateCheck',
    'Created': 'created',
    'Uptime': 'uptime',
    'RSSI': 'rssi',
    'p_0_3_um': 'p_0_3_um',
    'p_0_5_um': 'p_0_5_um',
    'p_1_0_um': 'p_1_0_um',
    'p_2_5_um': 'p_2_5_um',
    'p_5_0_um': 'p_5_0_um',
    'p_10_0_um': 'p_10_0_um',
    'pm1_0_cf_1': 'pm1_0_cf_1',
    'pm2_5_cf_1': 'pm2_5_cf_1',
    'pm10_0_cf_1': 'pm10_0_cf_1',
    'pm1_0_atm': 'pm1_0_atm',
    'pm2_5_atm': 'pm2_5_atm',
    'pm10_0_atm': 'pm10_0_atm',
    'humidity': 'humidity',
    'temp_f': 'temp_f',
    'pressure': 'pressure',
    'AGE': 'age',
    'Stats': 'stats'
}

sqlFieldTypes = {
    'sensorID': 'integer',
    'label': 'text',
    'deviceLocationType': 'text',
    'lat': 'real',
    'lon': 'real',
    'pm2_5Value': 'real',
    'lastSeen': 'integer',
    'type': 'text',
    'hidden': 'integer',
    'version': 'text',
    'lastUpdateCheck': 'integer',
    'created': 'integer',
    'uptime': 'integer',
    'rssi': 'integer',
    'p_0_3_um': 'real',
    'p_0_5_um': 'real',
    'p_1_0_um': 'real',
    'p_2_5_um': 'real',
    'p_5_0_um': 'real',
    'p_10_0_um': 'real',
    'pm1_0_cf_1': 'real',
    'pm2_5_cf_1': 'real',
    'pm10_0_cf_1': 'real',
    'pm1_0_atm': 'real',
    'pm2_5_atm': 'real',
    'pm10_0_atm': 'real',
    'humidity': 'integer',
    'temp_f': 'integer',
    'pressure': 'real',
    'age': 'integer',
    'stats': 'text'
}

def getLocalTime(timestamp):
    ts1 = datetime.fromtimestamp(timestamp, tz=pytz.utc)
    localTime = ts1.astimezone(timezone('US/Pacific'))
    return localTime

healthLevelMap = {
    0: 'Good. Air quality is considered satisfactory.',
    1: 'Moderate. Air quality is acceptable.',
    2: 'Unhealthy for Sensitive Groups. Members of sensitive groups may experience health effects if they are exposed for 24 hours.',
    3: 'Unhealthy. Everyone may begin to experience health effects if they are exposed for 24 hours.',
    4: 'Very Unhealthy. Health alert: everyone may experience more serious health effects if they are exposed for 24 hours.',
    5: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    6: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    7: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    8: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    9: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    -1: 'Invalid level'
}

def healthLevel(value):
    result = 0
    if 0 <= value < 50:
        result = 0
    elif 50 <= value < 100:
        result = 1

    elif 100 <= value < 150:
        result = 2

    elif 150 <= value < 200:
        result = 3

    elif 200 <= value < 250:
        result = 4

    elif 250 <= value < 300:
        result = 5

    elif 300 <= value < 350:
        result = 6

    elif 350 <= value < 400:
        result = 7

    elif 400 <= value < 500:
        result = 8

    elif value >= 500:
        result = 9

    else:
        result = -1

    return result

def aq_and_u_adjustment(pa):
    result = 0.778 * pa + 2.65
    return result


def convert2EPA(pm25):
    epaPM25 = int(aqi.to_aqi([(aqi.POLLUTANT_PM25, pm25)]))
    aqu25Adjust = aq_and_u_adjustment(pm25)
    epaAQU = int(aqi.to_aqi([(aqi.POLLUTANT_PM25, aqu25Adjust)]))

    return (epaPM25, epaAQU)


class AiryArgparse:
    def __init__(self, parsedArgs):
        networkManager = NetworkManager()
        database = AiryDB()
        airy = Airy(parsedArgs, networkManager, database)
        airy.run()

class Airy:
    def __init__(self, args, networkManager, database):
        self.args = args
        self.sensorID = args.sensorID
        self.networkManager = networkManager
        self.database = database

    def run(self):
        sys.stdout.write('Airy SensorID: {0}\n'.format(self.sensorID))
        response =  self.networkManager.getSensorData(self.sensorID)

        responseDict = None

        if response.status_code == 200:
            responseDict = response.json()
            for e in responseDict['results']:
                ## Deserialize JSON result
                pResult = PurpleAirResult(e)

                ## Write to DB
                if self.database.read(pResult) == None:
                    self.database.write(pResult)

            ## Check Deltas
            sensorIDs = list(map(lambda x: x['ID'], responseDict['results']))

            if len(sensorIDs) > 0:
                current25Mean, previous25Mean = self.database.deltas(sensorIDs)

                if previous25Mean != None:
                    currentEPA = convert2EPA(current25Mean)
                    previousEPA = convert2EPA(previous25Mean)

                    delta = current25Mean - previous25Mean
                    deltaPercent = (delta / current25Mean) * 100.0

                    renderDelta = '↑' if delta >= 0 else '↓'

                    sys.stdout.write('  Raw PM 2.5: {0} {1} {2}%\n'.format(round(current25Mean, 2), renderDelta, round(deltaPercent, 2)))
                    sys.stdout.write('   EPA PM2.5: {0}\n'.format(currentEPA[0]))
                    sys.stdout.write('AQ & U PM2.5: {0}\n'.format(currentEPA[1]))

                    currentHealthLevel = healthLevel(currentEPA[1])
                    previousHealthLevel = healthLevel(previousEPA[1])

                    sys.stdout.write('Level {0}: {1}\n'.format(currentHealthLevel, healthLevelMap[currentHealthLevel]))

                    if currentHealthLevel in (0, 1) and previousHealthLevel not in (0, 1):
                        sys.stdout.write('ALERT: AQI level is ok.\n')
                    elif currentHealthLevel not in (0, 1) and previousHealthLevel in (0, 1):
                        sys.stdout.write('ALERT: AQI level is bad. Take measures.\n')
                    elif currentHealthLevel not in (0, 1) and previousHealthLevel not in (0, 1):
                        pass
                        #sys.stdout.write('ALERT: AQI level is bad. Continue taking measures.\n')

                else:
                    currentEPA = convert2EPA(current25Mean)

                    sys.stdout.write('  Raw PM 2.5: {0} Δ: {1}%\n'.format(round(current25Mean, 2), round(deltaPercent, 2)))
                    sys.stdout.write('   EPA PM2.5: {0}\n'.format(currentEPA[0]))
                    sys.stdout.write('AQ & U PM2.5: {0}\n'.format(currentEPA[1]))





class AiryDB:
    def __init__(self):
        pathComponents = [os.environ['HOME'], 'Library', 'Application Support', 'airy']
        libraryDir = reduce(lambda x, y: os.path.join(x, y), pathComponents)

        if not os.path.exists(libraryDir):
            sys.stderr.write('Initializing airy library')
            os.mkdir(libraryDir)

        self.dbFilename = os.path.join(libraryDir, 'airy.db')

        conn = sqlite3.connect(self.dbFilename)
        c = conn.cursor()
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='purpleair' ''')
        if c.fetchone()[0] == 1:
            pass
            #sys.stderr.write('Table exists.\n')

        else:
            sys.stderr.write('Table does not exist.\n')

            bufList = []
            bufList.append('CREATE')
            bufList.append('TABLE')
            bufList.append('purpleair')
            columns = ', '.join(map(lambda x: '{0} {1}'.format(x[0], x[1]), sqlFieldTypes.items()))
            bufList.append('({0})'.format(columns))

            cmd = ' '.join(bufList)
            c.execute(cmd)
            conn.commit()

        # commit the changes to db

        # close the connection
        conn.close()

    def deltas(self, sensorIDs):
        conn = sqlite3.connect(self.dbFilename)
        c = conn.cursor()
        sensorData = []
        for sensorID in sensorIDs:
            cmd = 'select sensorID, pm2_5Value, humidity, lastSeen from purpleair where sensorID in ({0})  order by lastSeen desc limit 2'.format(sensorID)
            rows = c.execute(cmd).fetchall()
            sensorData.append(rows)

        conn.close()

        firstRow = map(lambda x: x[0], sensorData)
        col_pm2_5 = map(lambda x: x[1], firstRow)
        humidity = sensorData[0][0][2]

        currentMean = mean(col_pm2_5)

        try:
            secondRow = map(lambda x: x[1], sensorData)
            col_pm2_5 = map(lambda x: x[1], secondRow)
            previousMean = mean(col_pm2_5)

            return (currentMean, previousMean)
        except:
            return (currentMean, None)


    def read(self, record):
        conn = sqlite3.connect(self.dbFilename)
        c = conn.cursor()
        cmd = 'select * from purpleair where lastSeen = {0} AND sensorID = {1}'.format(record.lastSeen, record.sensorID)
        rows = c.execute(cmd).fetchall()
        conn.commit()
        conn.close()

        if len(rows) == 0:
            return None
        else:
            return rows



    def write(self, record):
        localTime = getLocalTime(record.lastSeen)
        sys.stdout.write('{0}: PM 2.5 Value: {1} {2}\n'.format(record.sensorID, record.pm2_5Value, localTime.isoformat()))

        conn = sqlite3.connect(self.dbFilename)
        c = conn.cursor()

        bufList = []
        bufList.append('INSERT')
        bufList.append('INTO')
        bufList.append('purpleair')

        columns = []
        values = []

        fieldMapValues = filter(lambda x: x != 'stats', fieldMap.values())
        for key in fieldMapValues:
            try:
                value = getattr(record, key)

                if isinstance(value, str):
                    valueString = '"{0}"'.format(value)
                else:
                    valueString = '{0}'.format(value)
                values.append(valueString)
                columns.append(key)
            except AttributeError:
                continue

        bufList.append('({0})'.format(','.join(columns)))
        bufList.append('VALUES')
        bufList.append('({0})'.format(','.join(values)))

        cmd = ' '.join(bufList)

        c.execute(cmd)

        conn.commit()
        conn.close()

class PurpleAirResult:
    def __init__(self, resultDict):
        #for key in resultDict.keys():
        #    print('{0}: {1}'.format(key, resultDict[key]))

        for key in fieldMap.keys():
            if key in resultDict.keys():
                if key in ("PM2_5Value",
                           "p_0_3_um",
                           "p_0_5_um",
                           "p_1_0_um",
                           "p_2_5_um",
                           "p_5_0_um",
                           "p_10_0_um",
                           "pm1_0_cf_1",
                           "pm2_5_cf_1",
                           "pm10_0_cf_1",
                           "pm1_0_atm",
                           "pm2_5_atm",
                           "pm10_0_atm",
                           "pressure"):
                    setattr(self, fieldMap[key], float(resultDict[key]))

                elif key in ("humidity", "temp_f", "RSSI", 'Uptime'):
                    setattr(self, fieldMap[key], int(resultDict[key]))

                elif key == 'Hidden':
                    if resultDict[key] == 'false':
                        setattr(self, fieldMap[key], 0)
                    elif resultDict[key] == 'true':
                        setattr(self, fieldMap[key], 1)

                elif key == 'Stats':
                    statsDict = json.loads(resultDict[key])
                    setattr(self, fieldMap[key], statsDict)

                #elif key in ('LastSeen', 'LastUpdateCheck', 'Created'):
                #    ts1 = datetime.fromtimestamp(resultDict[key], tz=pytz.utc)
                #   #ts1.astimezone(timezone('US/Pacific'))
                #    setattr(self, fieldMap[key], ts1)

                else:
                    setattr(self, fieldMap[key], resultDict[key])


class NetworkManager:

    def getSensorData(self, sensorID):
        url = 'https://www.purpleair.com/json?show={0}'.format(sensorID)
        #print(url)
        r = requests.get(url)
        return r


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=("airy - send an alert whenever a steep change in air quality from a "
                                                  "public Purple Air monitor is detected"))

    parser.add_argument('sensorID', action='store', type=int)

    #  https://www.purpleair.com/json?show=<id>

    result = parser.parse_args()

    #print(result.sensorID)

    app = AiryArgparse(result)












