#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime
from pytz import timezone
import pytz
from functools import reduce
import sqlite3
from statistics import mean
import aqi
import json
from airylib import *
from airylib.NetworkManager import  NetworkManager
from airylib.AiryDB import AiryDB
from airylib.PurpleAirResult import PurpleAirResult

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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=("airy - send an alert whenever a steep change in air quality from a "
                                                  "public Purple Air monitor is detected"))
    parser.add_argument('sensorID', action='store', type=int)
    parser.add_argument('-l', '--log-format', action='store_true', help='Emit log file format')
    result = parser.parse_args()
    app = AiryArgparse(result)












