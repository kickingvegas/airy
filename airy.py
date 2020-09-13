#!/usr/bin/env python3
import os
import sys
import argparse
from airylib import *
from airylib.NetworkManager import  NetworkManager
from airylib.AiryDB import AiryDB
from airylib.PurpleAirResult import PurpleAirResult
from airylib.SMSMessenger import SMSMessenger
from airylib.SensorManager import SensorManager
from datetime import datetime
from pytz import timezone

class AiryArgparse:
    def __init__(self, parsedArgs):
        networkManager = NetworkManager()
        database = AiryDB()
        if parsedArgs.query_nearby_sensors:
            sensorManager = SensorManager(parsedArgs, networkManager, database)


        elif parsedArgs.sync_sensors:
            sensorManager = SensorManager(parsedArgs, networkManager, database)
            sensorManager.sync()

        else:
            airy = Airy(parsedArgs, networkManager, database)
            airy.run()

class Airy:
    def __init__(self, args, networkManager, database):
        self.args = args
        self.sensorID = args.sensorID
        self.networkManager = networkManager
        self.database = database

    def run(self):
        #sys.stdout.write('Airy SensorID: {0}\n'.format(self.sensorID))
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

                    self.renderOutput(current25Mean, delta, deltaPercent, currentEPA, previousEPA)

                    currentHealthLevel = healthLevel(currentEPA[1])
                    previousHealthLevel = healthLevel(previousEPA[1])

                    if currentHealthLevel in (0, 1) and previousHealthLevel not in (0, 1):
                        if self.args.twilio_sid and self.args.twilio_token and self.args.twilio_number:
                            smsMessenger = SMSMessenger(self.args.twilio_sid,
                                                        self.args.twilio_token,
                                                        self.args.twilio_number)
                            msg = 'ALERT: AQI level {0} is good. Open the windows!'.format(currentEPA[1])
                            smsMessenger.sendMessage('+14152972054', msg)

                    elif currentHealthLevel not in (0, 1) and previousHealthLevel in (0, 1):

                        if self.args.twilio_sid and self.args.twilio_token and self.args.twilio_number:
                            smsMessenger = SMSMessenger(self.args.twilio_sid,
                                                        self.args.twilio_token,
                                                        self.args.twilio_number)
                            msg = 'ALERT: AQI level {0} is bad. Take measures.'.format(currentEPA[1])
                            smsMessenger.sendMessage('+14152972054', msg)

                    elif currentHealthLevel not in (0, 1) and previousHealthLevel not in (0, 1):
                        pass

                else:
                    currentEPA = convert2EPA(current25Mean)
                    self.renderOutput(current25Mean, 0, 0.0, currentEPA, None)

    def renderHumanOutput(self, current25Mean, delta, deltaPercent, currentEPA, previousEPA):
        renderDelta = '↑' if delta >= 0 else '↓'
        sys.stdout.write('Airy SensorID: {0}\n'.format(self.args.sensorID))
        sys.stdout.write('    Raw PM2.5: {0} {1} {2}%\n'.format(round(current25Mean, 2), renderDelta, round(deltaPercent, 2)))
        sys.stdout.write('    EPA PM2.5: {0}\n'.format(currentEPA[0]))
        sys.stdout.write(' AQ & U PM2.5: {0}\n'.format(currentEPA[1]))
        currentHealthLevel = healthLevel(currentEPA[1])
        sys.stdout.write('      Level {0}: {1}\n'.format(currentHealthLevel, healthLevelMap[currentHealthLevel]))

    def renderLogOutput(self, current25Mean, delta, deltaPercent, currentEPA, previousEPA):
        renderDelta = '↑' if delta >= 0 else '↓'

        timestamp = datetime.now()
        zone = timezone('US/Pacific')
        localTime = zone.localize(timestamp)
        tsBuf = localTime.strftime('%Y-%m-%d %H:%M:%S %z')

        bufList = []
        bufList.append('SensorID: {0}'.format(self.args.sensorID))
        bufList.append('Raw_PM25: {0}'.format(round(current25Mean, 2)))
        bufList.append('EPA_PM25: {0}'.format(currentEPA[0]))
        bufList.append('AQU_PM25: {0}'.format(currentEPA[1]))
        bufList.append('delta: {0} {1}%'.format(renderDelta, round(deltaPercent, 2)))

        buf = ', '.join(bufList)

        sys.stdout.write('{0}: {1}\n'.format(tsBuf, buf))


    def renderOutput(self, current25Mean, delta, deltaPercent, currentEPA, previousEPA):
        if self.args.log_format:
            self.renderLogOutput(current25Mean, delta, deltaPercent, currentEPA, previousEPA)
        else:
            self.renderHumanOutput(current25Mean, delta, deltaPercent, currentEPA, previousEPA)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=("airy - send an alert whenever a steep change in air quality from a "
                                                  "public Purple Air monitor is detected"))
    parser.add_argument('sensorID', action='store', type=int)
    parser.add_argument('-l', '--log-format', action='store_true', help='Emit log file format')
    parser.add_argument('--twilio-sid', action='store', help='Twilio Account SID')
    parser.add_argument('--twilio-token', action='store', help='Twilio Account Token')
    parser.add_argument('--twilio-number', action='store', help='Twilio Phone Number')
    parser.add_argument('-s', '--sync-sensors', action='store_true', help='Sync sensors')
    parser.add_argument('-q', '--query-nearby-sensors', action='store_true', help='Query nearby sensors')
    result = parser.parse_args()
    app = AiryArgparse(result)












