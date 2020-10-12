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

from airylib.PurpleAirResult import PurpleAirResult
import sys

class SensorManager:
    def __init__(self, args, networkManager, database):
        self.args = args
        self.database = database
        self.networkManager = networkManager

    def sync(self):
        response = self.networkManager.getSensorList()

        if response.status_code == 200:
            responseDict = response.json()

            conn = self.database.openConnection()
            for e in responseDict['results']:
                pResult = PurpleAirResult(e)

                ## Read then write
                rows = self.database.readSensor(pResult, conn)
                if rows is None:
                    self.database.createSensor(pResult, conn)
                else:
                    # Compare row with pResult to update
                    if hasattr(pResult, 'lat') and hasattr(pResult, 'lon'):
                        for row in rows:
                            lat = row[2]
                            lon = row[3]
                            if (pResult.lat != lat) or (pResult.lon != lon):
                                self.database.updateSensor(pResult, conn)
                            else:
                                pass

            self.database.closeConnection()


        else:
            sys.stderr.write('Unable to read sensor list.\n')
            sys.exit(1)

