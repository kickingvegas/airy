import os
import sys
import Cocoa
import CoreLocation
from PyObjCTools import AppHelper
import objc

class LocationManager(Cocoa.NSObject):
    def init(self):
        self = objc.super(LocationManager, self).init()
        if self is None: return None

        self.manager = CoreLocation.CLLocationManager.alloc().init()
        self.manager.setDelegate_(self)

        self.first = True
        return self

    def locationManager_didUpdateLocations_(self, manager, locations):
        #print(locations)
        lat = locations[0].coordinate().latitude
        lon = locations[0].coordinate().longitude
        if self.first:
            print('{0}, {1}'.format(lat, lon))
            self.first = False
            AppHelper.stopEventLoop()

    def locationManager_didFailWithError_(self, manager, error):
        sys.stderr.write('ERROR: {0}\n'.format(error))
        sys.exit(1)

    def locationManager_didChangeAuthorizationStatus_(self, manager, status):
        pass
        #print('{0}'.format(status))

    def requestLocation(self):
        self.manager.startUpdatingLocation()

if __name__ == '__main__':
    locationManager = LocationManager.alloc().init()
    locationManager.requestLocation()
    AppHelper.runConsoleEventLoop()










