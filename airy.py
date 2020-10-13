#!/usr/bin/env python3
##
# Copyright 2020 Charles Y. Choi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

AIRY_VERSION = '0.1.0'

class AiryArgparse:
    def __init__(self, parsedArgs):
        networkManager = NetworkManager()
        database = AiryDB()

        if parsedArgs.version:
            sys.stdout.write('{0}\n'.format(AIRY_VERSION))
            sys.exit(0)

        if parsedArgs.sync_sensors:
            sensorManager = SensorManager(parsedArgs, networkManager, database)
            sensorManager.sync()

        elif parsedArgs.query_nearby_sensors:
            # TODO: implement
            sensorManager = SensorManager(parsedArgs, networkManager, database)

        elif parsedArgs.sensorID:
            airy = Airy(parsedArgs, networkManager, database)
            airy.run()

        else:
            sys.stderr.write('Undefined sensorID. Exiting...\n')
            sys.exit(1)


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

            sensorLabel = None

            for e in responseDict['results']:
                ## Deserialize JSON result
                pResult = PurpleAirResult(e)
                if sensorLabel == None:
                    sensorLabel = pResult.label

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
                        if self.args.to_sms and self.args.twilio_sid and self.args.twilio_token and self.args.twilio_number:
                            smsMessenger = SMSMessenger(self.args.twilio_sid,
                                                        self.args.twilio_token,
                                                        self.args.twilio_number)

                            currentHealthLevel = healthLevel(currentEPA[1])
                            msg = '{0}: AQ&U: {1}, AQI: {2}: {3}'.format(sensorLabel,
                                                                         currentEPA[1],
                                                                         currentHealthLevel,
                                                                         healthLevelMap[currentHealthLevel])

                            for to in self.args.to_sms:
                                smsMessenger.sendMessage(to, msg)

                    elif currentHealthLevel not in (0, 1) and previousHealthLevel in (0, 1):

                        if self.args.to_sms and self.args.twilio_sid and self.args.twilio_token and self.args.twilio_number:
                            smsMessenger = SMSMessenger(self.args.twilio_sid,
                                                        self.args.twilio_token,
                                                        self.args.twilio_number)
                            currentHealthLevel = healthLevel(currentEPA[1])

                            msg = '{0}: AQ&U: {1}, AQI: {2}: {3}'.format(sensorLabel,
                                                                         currentEPA[1],
                                                                         currentHealthLevel,
                                                                         healthLevelMap[currentHealthLevel])

                            for to in self.args.to_sms:
                                smsMessenger.sendMessage(to, msg)


                    else:
                        always = False
                        if self.args.to_sms and self.args.twilio_sid and self.args.twilio_token and self.args.twilio_number and always:
                            smsMessenger = SMSMessenger(self.args.twilio_sid,
                                                        self.args.twilio_token,
                                                        self.args.twilio_number)
                            currentHealthLevel = healthLevel(currentEPA[1])
                            msg = '{0}: AQ&U: {1}, AQI: {2}: {3}'.format(sensorLabel,
                                                                         currentEPA[1],
                                                                         currentHealthLevel,
                                                                         healthLevelMap[currentHealthLevel])

                            for to in self.args.to_sms:
                                smsMessenger.sendMessage(to, msg)

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
    parser.add_argument('sensorID', action='store', type=int, nargs="?")
    parser.add_argument('-l', '--log-format', action='store_true', help='Output log file format on stdout, otherwise use display format.')
    parser.add_argument('-q', '--query-nearby-sensors', action='store_true', help='Query nearby sensors')
    parser.add_argument('-s', '--sync-sensors', action='store_true', help='Sync sensors. Progress displayed on stdout, updated records on stderr.')
    parser.add_argument('-t', '--to-sms', action='append', nargs='+', help="Destination SMS number")
    parser.add_argument('--twilio-sid', action='store', help='Twilio Account SID')
    parser.add_argument('--twilio-token', action='store', help='Twilio Account Token')
    parser.add_argument('--twilio-number', action='store', help='Twilio Phone Number')
    parser.add_argument('-v', '--version', action='store_true', help='Display version')

    result = parser.parse_args()
    app = AiryArgparse(result)












