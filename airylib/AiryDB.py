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
