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

import sqlite3
import os
import sys
from functools import reduce
from statistics import mean
from airylib import *

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
            sys.stderr.write('Creating purpleair table.\n')
            bufList = []
            bufList.append('CREATE')
            bufList.append('TABLE')
            bufList.append('purpleair')
            columns = ', '.join(map(lambda x: '{0} {1}'.format(x[0], x[1]), sqlFieldTypes.items()))
            bufList.append('({0})'.format(columns))

            cmd = ' '.join(bufList)
            c.execute(cmd)
            conn.commit()

        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='sensors' ''')
        if c.fetchone()[0] == 1:
            pass
        else:
            sys.stderr.write('Creating sensors table.\n')
            bufList = []
            bufList.append('CREATE')
            bufList.append('TABLE')
            bufList.append('sensors')
            columns = ['sensorID integer', 'label text', 'lat real', 'lon real', 'deviceLocationType text']
            bufList.append('({0})'.format(', '.join(columns)))
            cmd = ' '.join(bufList)
            c.execute(cmd)
            conn.commit()

        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='index' AND name='idx_sensorID' ''')
        if c.fetchone()[0] == 1:
            pass
        else:
            sys.stderr.write('Creating index for sensors.sensorID.\n')
            bufList = []
            bufList.append('CREATE')
            bufList.append('UNIQUE')
            bufList.append('INDEX')
            bufList.append('"idx_sensorID"')
            bufList.append('ON')
            bufList.append('sensors')
            columns = ['sensorID']
            bufList.append('({0})'.format(', '.join(columns)))
            cmd = ' '.join(bufList)
            c.execute(cmd)
            conn.commit()

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

        primary, secondary = col_pm2_5
        if primary == 0.0 and secondary > 0.0:
            currentMean = secondary
        elif primary > 0.0 and secondary == 0.0:
            currentMean = primary
        else:
            currentMean = mean([primary,secondary])

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
        conn.close()

        if len(rows) == 0:
            return None
        else:
            return rows


    def write(self, record):
        localTime = getLocalTime(record.lastSeen)
        #sys.stdout.write('{0}: PM 2.5 Value: {1} {2}\n'.format(record.sensorID, record.pm2_5Value, localTime.isoformat()))

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

    def openConnection(self):
        conn = sqlite3.connect(self.dbFilename)
        return conn

    def closeConnection(self, conn):
        conn.commit()
        conn.close()

    def readSensor(self, record, conn):
        cmd = 'select sensorID, label, lat, lon, deviceLocationType from sensors where sensorID = {0}'.format(record.sensorID)
        c = conn.cursor()
        rows = c.execute(cmd).fetchall()

        result = []
        for row in rows:
            e = {}
            e['sensorID'] = row[0]
            e['label'] = row[1]
            e['lat'] = row[2]
            e['lon'] = row[3]
            e['deviceLocationType'] = row[4]
            result.append(e)

        return result




    def createSensor(self, record, conn):
        c = conn.cursor()
        bufList = []
        bufList.append('INSERT')
        bufList.append('INTO')
        bufList.append('sensors')

        columns = []
        values = []

        fieldMapValues = ['sensorID', 'lat', 'lon', 'label', 'deviceLocationType']
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


    def updateSensor(self, record, conn):
        c = conn.cursor()
        bufList = []
        bufList.append('UPDATE')
        bufList.append('sensors')
        bufList.append('set')

        columns = []
        values = []

        fieldMapValues = ['sensorID', 'lat', 'lon', 'label', 'deviceLocationType']
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

        pairList = []
        for pair in zip(columns, values):
            columnName, value = pair
            pairList.append('{0} = {1}'.format(columnName, value))
        bufList.append('{0}'.format(', '.join(pairList)))

        bufList.append('WHERE')
        bufList.append('sensorID = {0}'.format(record.sensorID))

        cmd = ' '.join(bufList)
        sys.stderr.write('{0}\n'.format(cmd))

        c.execute(cmd)

    def reindexSensors(self, conn):
        c = conn.cursor()

        cmd = 'REINDEX idx_sensorID'
        c.execute(cmd)
        conn.commit()







