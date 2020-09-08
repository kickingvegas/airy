#!/usr/bin/env python3
import os
import sys
import argparse
import requests
from datetime import datetime
from pytz import timezone
import pytz


class AiryArgparse:
    def __init__(self, parsedArgs):
        networkManager = NetworkManager()
        database = AiryDB()
        airy = Airy(parsedArgs.sensorID, networkManager, database)
        airy.run()

class Airy:
    def __init__(self, sensorID, networkManager, database):
        self.sensorID = sensorID
        self.networkManager = networkManager
        self.database = database

    def run(self):
        print('Airy SensorID: {0}'.format(self.sensorID))
        response =  self.networkManager.getSensorData(self.sensorID)

        responseDict = None

        if response.status_code == 200:
            responseDict = response.json()
            results = []
            for e in responseDict['results']:
                pResult = PurpleAirResult(e)
                results.append(pResult)

            print(results[0].pm2_5Value)
            print(results[1].pm2_5Value)


class AiryDB:
    def __init__(self):
        pass


class PurpleAirResult:
    def __init__(self, resultDict):
        fieldMap = {
            'ID': 'sensorID',
            "Label": "label",
            "DEVICE_LOCATIONTYPE": "deviceLocationType",
            "Lat": "lat",
            "Lon": "lon",
            "PM2_5Value": "pm2_5Value",
            "LastSeen": "lastSeen",
            "Type": "type",
            "Hidden": "hidden",
            "Version": "version",
            "LastUpdateCheck": "lastUpdateCheck",
            "Created": "created",
            "Uptime": "uptime",
            "RSSI": "rssi",
            "p_0_3_um": "p_0_3_um",
            "p_0_5_um": "p_0_5_um",
            "p_1_0_um": "p_1_0_um",
            "p_2_5_um": "p_2_5_um",
            "p_5_0_um": "p_5_0_um",
            "p_10_0_um": "p_10_0_um",
            "pm1_0_cf_1": "pm1_0_cf_1",
            "pm2_5_cf_1": "pm2_5_cf_1",
            "pm10_0_cf_1": "pm10_0_cf_1",
            "pm1_0_atm": "pm1_0_atm",
            "pm2_5_atm": "pm2_5_atm",
            "pm10_0_atm": "pm10_0_atm",
            "humidity": "humidity",
            "temp_f": "temp_f",
            "pressure": "pressure",
            "AGE": "age",
            "Stats": "stats"
        }

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

                elif key in ("humidity", "temp_f", "RSSI"):
                    setattr(self, fieldMap[key], int(resultDict[key]))

                elif key in ('LastSeen', 'LastUpdateCheck', 'Created'):
                    ts1 = datetime.fromtimestamp(resultDict[key], tz=pytz.utc)
                    #ts1.astimezone(timezone('US/Pacific'))
                    setattr(self, fieldMap[key], ts1)

                else:
                    setattr(self, fieldMap[key], resultDict[key])


class NetworkManager:

    def getSensorData(self, sensorID):
        url = 'https://www.purpleair.com/json?show={0}'.format(sensorID)
        print(url)
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












