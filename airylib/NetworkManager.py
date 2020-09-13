import requests

class NetworkManager:

    def getSensorData(self, sensorID):
        url = 'https://www.purpleair.com/json?show={0}'.format(sensorID)
        #print(url)
        r = requests.get(url)
        return r
