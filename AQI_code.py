import urllib.parse
import urllib.request
from collections import namedtuple
import math
import json


AQIReading = namedtuple('AQIReading', ['AQI', 'latitude', 'longitude', 'name'])
PURPLEAIR_URL = 'https://www.purpleair.com/data.json'
NOMINATIM_F_URL = 'https://nominatim.openstreetmap.org/search?'
NOMINATIM_R_URL = 'https://nominatim.openstreetmap.org/reverse?format=json&'
REFERER = 'https://www.ics.uci.edu/~thornton/ics32/ProjectGuide/Project3/tjwada'


class PurpleAirAPI():
    def __init__(self):
        '''Initializes class with a Path to a JSON for reading the file from an API'''
        self._read_API(PURPLEAIR_URL)

    def get_aqi_dict(self) -> dict:
        '''Returns a dictionary of the JSON.'''        
        return self._reading_dict
        

    def _read_API(self, url: str) -> None:
        '''
        Attempts to connect to PurpleAir API and initializes dictionary attribute.
        Excepts errors accordingly and prints error messages.
        '''
        _aqi_response = None
        try:
            _aqi_request = urllib.request.Request(url)
            _aqi_response = urllib.request.urlopen(_aqi_request)
            _json_txt = _aqi_response.read()
            _json_txt = _json_txt.decode(encoding = 'utf-8')
            self._reading_dict = json.loads(_json_txt)

        except urllib.error.HTTPError as e:
            print('FAILED')
            print(e.code, url)
            print('NOT 200')

        except json.decoder.JSONDecodeError:
            print('FAILED')
            print('200', url)            
            print('FORMAT')
    
        except urllib.error.URLError:
            print('FAILED')
            print(url)
            print('NETWORK')
            
        finally:
            if _aqi_response != None:            
                _aqi_response.close()


class NominatimForwardAPI():
    def __init__(self, location: str):
        self._nom_url = NOMINATIM_F_URL + urllib.parse.urlencode([('q', location), ('format', 'json'), ('Referer', REFERER)])
        self._read_API(self._nom_url)

    def get_fwd_dict(self) -> dict:
        '''Returns a dictionary of the JSON.'''        
        return self._reading_dict

    def _read_API(self, url: str) -> None:
        '''
        Attempts to connect to NOMINATIM API and initializes dictionary attribute.
        Excepts errors accordingly and prints error messages.
        '''
        _nf_response = None
        try:
            _nf_request = urllib.request.Request(url)
            _nf_response = urllib.request.urlopen(_nf_request)
            _json_txt = _nf_response.read()
            _json_txt = _json_txt.decode(encoding = 'utf-8')
            self._reading_dict = json.loads(_json_txt)[0]

        except urllib.error.HTTPError as e:
            print('FAILED')
            print(e.code, url)
            print('NOT 200')

        except json.decoder.JSONDecodeError:
            print('FAILED')
            print('200', url)            
            print('FORMAT')            

        except urllib.error.URLError:
            print('FAILED')
            print(url)
            print('NETWORK')

            
        finally:
            if _nf_response != None:            
                _nf_response.close()



def GetReadings(aqi_info: dict, center_lat: float, center_lon: float) -> int:
    '''
    Returns a list of sorted AQIReading namedtuples based on a sensor dictionary, center location,
    range, AQI threshold, and a maximum number of readings.
    '''
    for reading in aqi_info['data']:
        if _reading_valid_check(reading[1], reading[4], reading[25], reading[27], reading[28]):
            distance = CalculateDistance(center_lat, center_lon, reading[27], reading[28])
            AQI = DetermineAQI(reading[1])
            if distance <= 5:
                return AQI



def GetLat(location_dict: dict) -> float:
    '''Returns latitude of a reverse Nominatim dictionary'''
    return float(location_dict['lat'])


def GetLon(location_dict: dict) -> float:
    '''Returns longitude of a reverse Nominatim dictionary'''
    return float(location_dict['lon'])


def DetermineAQI(PM: float) -> int:
    '''
    Converts a PM reading to an AQI reading.
    '''
    if PM == None:
        pass
    elif 0.0 <= PM < 12.1:
        return _calculate_AQI(PM, 0.0, 12.0, 0, 50)
    elif 12.1 <= PM < 35.5:
        return _calculate_AQI(PM, 12.1, 35.4, 51, 100)
    elif 35.5 <= PM < 55.5:
        return _calculate_AQI(PM, 35.5, 55.4, 101, 150)
    elif 55.5 <= PM < 150.5:
        return _calculate_AQI(PM, 55.5, 150.4, 151, 200)
    elif 150.5 <= PM < 250.5:
        return _calculate_AQI(PM, 150.5, 250.4, 201, 300)
    elif 250.5 <= PM < 350.5: 
        return _calculate_AQI(PM, 250.5, 350.4, 301, 400)
    elif 350.5 <= PM < 500.5:
        return _calculate_AQI(PM, 350.5, 500.4, 401, 500)
    elif PM >= 500.5:
        return 501


def _calculate_AQI(PM: float, PM_Floor: float, PM_Ceiling: float, AQI_Floor: float, AQI_Ceiling: float) -> int:
    '''
    Calculates AQI reading given a certain interval and PM.
    '''
    proportion = (PM - PM_Floor) / (PM_Ceiling - PM_Floor)
    AQI = (AQI_Ceiling - AQI_Floor) * proportion + AQI_Floor
    if AQI >= (math.floor(AQI) + 0.5):
        return math.ceil(AQI)
    else:
        return math.floor(AQI)


def CalculateDistance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    '''
    Calculates distance from one set of coordinates to another.
    '''
    dlat = abs(math.radians(lat1) - math.radians(lat2))
    dlon = abs(math.radians(lon1) - math.radians(lon2))
    alat = (math.radians(lat1) + math.radians(lat2)) / 2
    x = dlon * math.cos(alat)
    return math.sqrt(x**2 + dlat**2) * 3958.8


def _reading_valid_check(pm: float, age: int, Type: int, lat: float, lon: float) -> bool:
    '''
    Ensures readings of a sensor are interesting to us. Returns False if not.
    '''
    if None not in [pm, age, Type, lat, lon]:
        if age <= 3600 and Type == 0:
            return True
    return False

def find_aqi(location: str) -> int:
    loc_dict = NominatimForwardAPI(location).get_fwd_dict()
    landl = [GetLat(loc_dict), GetLon(loc_dict)]
    aqi_dict = PurpleAirAPI().get_aqi_dict()
    return GetReadings(aqi_dict, landl[0], landl[1])
