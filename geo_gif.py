import shutil
import requests

url = [
    'http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map&crs=EPSG:4326&bbox=-100,-100,100,100&version=1.3&styles=&width=1000&height=600&layers=Sentinel-1%20IW_GRDH_1S&format=image/png&time=2023-05-01/2023-05-01&pol=VV&&request=GetMap',
    'http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map&crs=EPSG:4326&bbox=-100,-100,100,100&version=1.3&styles=&width=1000&height=600&layers=Sentinel-1%20IW_GRDH_1S&format=image/png&time=2023-05-01/2023-05-02&pol=VV&&request=GetMap',
    'http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map&crs=EPSG:4326&bbox=-100,-100,100,100&version=1.3&styles=&width=1000&height=600&layers=Sentinel-1%20IW_GRDH_1S&format=image/png&time=2023-05-01/2023-05-03&pol=VV&&request=GetMap'
    ]   

response = requests.get(url[0], stream=True)
with open('img.png', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
del response