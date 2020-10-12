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
import json

class SensorManager:
    def __init__(self, args, networkManager, database):
        self.args = args
        self.database = database
        self.networkManager = networkManager

    def sync(self):
        response = self.networkManager.getSensorList()

        if response.status_code == 200:
            try:
                responseDict = response.json()
            except json.decoder.JSONDecodeError:
                sys.stderr.write('Unable to parse network response. Exiting...\n')
                sys.exit(1)


            conn = self.database.openConnection()
            total = len(responseDict['results'])
            modulo = int(total / 10)
            count = 0
            updateCount = 0

            for e in responseDict['results']:
                count += 1

                pResult = PurpleAirResult(e)
                ## Read then write
                rows = self.database.readSensor(pResult, conn)
                if rows is None:
                    self.database.createSensor(pResult, conn)
                else:
                    # Compare row with pResult to update
                    if hasattr(pResult, 'lat') and hasattr(pResult, 'lon'):
                        for row in rows:
                            lat = round(row[2], 7)
                            lon = round(row[3], 7)
                            if (pResult.lat != lat) or (pResult.lon != lon):
                                sys.stderr.write('{0}, {1}, {2}\n'.format(lat, lon, row[4]))
                                self.database.updateSensor(pResult, conn)
                                updateCount += 1
                            else:
                                pass


                if ((count % modulo) == 0) or (count == 1) or (count == total):
                    percentDone = int(round((float(count) / float(total)) * 100.0, 0))
                    bar = '#' * int(percentDone/10)
                    sys.stdout.write('\r{0} {1}% done, updated: {2}'.format(bar, percentDone, updateCount))

                    if count == total:
                        sys.stdout.write('\n')



            self.database.closeConnection(conn)


        else:
            sys.stderr.write('Unable to read sensor list.\n')
            sys.exit(1)

