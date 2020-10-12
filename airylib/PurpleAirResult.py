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

