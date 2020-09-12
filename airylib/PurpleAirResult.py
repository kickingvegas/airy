import json
from airylib import *

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

