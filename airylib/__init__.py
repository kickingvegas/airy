from datetime import datetime
import pytz
import aqi

fieldMap = {
    'ID': 'sensorID',
    'Label': 'label',
    'DEVICE_LOCATIONTYPE': 'deviceLocationType',
    'Lat': 'lat',
    'Lon': 'lon',
    'PM2_5Value': 'pm2_5Value',
    'LastSeen': 'lastSeen',
    'Type': 'type',
    'Hidden': 'hidden',
    'Version': 'version',
    'LastUpdateCheck': 'lastUpdateCheck',
    'Created': 'created',
    'Uptime': 'uptime',
    'RSSI': 'rssi',
    'p_0_3_um': 'p_0_3_um',
    'p_0_5_um': 'p_0_5_um',
    'p_1_0_um': 'p_1_0_um',
    'p_2_5_um': 'p_2_5_um',
    'p_5_0_um': 'p_5_0_um',
    'p_10_0_um': 'p_10_0_um',
    'pm1_0_cf_1': 'pm1_0_cf_1',
    'pm2_5_cf_1': 'pm2_5_cf_1',
    'pm10_0_cf_1': 'pm10_0_cf_1',
    'pm1_0_atm': 'pm1_0_atm',
    'pm2_5_atm': 'pm2_5_atm',
    'pm10_0_atm': 'pm10_0_atm',
    'humidity': 'humidity',
    'temp_f': 'temp_f',
    'pressure': 'pressure',
    'AGE': 'age',
    'Stats': 'stats'
}

sqlFieldTypes = {
    'sensorID': 'integer',
    'label': 'text',
    'deviceLocationType': 'text',
    'lat': 'real',
    'lon': 'real',
    'pm2_5Value': 'real',
    'lastSeen': 'integer',
    'type': 'text',
    'hidden': 'integer',
    'version': 'text',
    'lastUpdateCheck': 'integer',
    'created': 'integer',
    'uptime': 'integer',
    'rssi': 'integer',
    'p_0_3_um': 'real',
    'p_0_5_um': 'real',
    'p_1_0_um': 'real',
    'p_2_5_um': 'real',
    'p_5_0_um': 'real',
    'p_10_0_um': 'real',
    'pm1_0_cf_1': 'real',
    'pm2_5_cf_1': 'real',
    'pm10_0_cf_1': 'real',
    'pm1_0_atm': 'real',
    'pm2_5_atm': 'real',
    'pm10_0_atm': 'real',
    'humidity': 'integer',
    'temp_f': 'integer',
    'pressure': 'real',
    'age': 'integer',
    'stats': 'text'
}

def getLocalTime(timestamp):
    ts1 = datetime.fromtimestamp(timestamp, tz=pytz.utc)
    localTime = ts1.astimezone()
    return localTime

healthLevelMap = {
    0: 'Good. Air quality is considered satisfactory.',
    1: 'Moderate. Air quality is acceptable.',
    2: 'Unhealthy for Sensitive Groups. Members of sensitive groups may experience health effects if they are exposed for 24 hours.',
    3: 'Unhealthy. Everyone may begin to experience health effects if they are exposed for 24 hours.',
    4: 'Very Unhealthy. Health alert: everyone may experience more serious health effects if they are exposed for 24 hours.',
    5: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    6: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    7: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    8: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    9: 'Very Unhealthy. Health warnings of emergency conditions if they are exposed for 24 hours.',
    -1: 'Invalid level'
}

def healthLevel(value):
    result = 0
    if 0 <= value < 50:
        result = 0
    elif 50 <= value < 100:
        result = 1

    elif 100 <= value < 150:
        result = 2

    elif 150 <= value < 200:
        result = 3

    elif 200 <= value < 250:
        result = 4

    elif 250 <= value < 300:
        result = 5

    elif 300 <= value < 350:
        result = 6

    elif 350 <= value < 400:
        result = 7

    elif 400 <= value < 500:
        result = 8

    elif value >= 500:
        result = 9

    else:
        result = -1

    return result

def aq_and_u_adjustment(pa):
    result = 0.778 * pa + 2.65
    return result


def convert2EPA(pm25):
    epaPM25 = int(aqi.to_aqi([(aqi.POLLUTANT_PM25, pm25)]))
    aqu25Adjust = aq_and_u_adjustment(pm25)
    epaAQU = int(aqi.to_aqi([(aqi.POLLUTANT_PM25, aqu25Adjust)]))

    return (epaPM25, epaAQU)
