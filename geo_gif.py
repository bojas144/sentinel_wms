import shutil
import requests
from PIL import Image
import os

date = ['2023-05-01/2023-05-01',
        '2023-05-01/2023-05-02',
        '2023-05-01/2023-05-03',
        '2023-05-01/2023-05-04',
        '2023-05-01/2023-05-05']

url = 'http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map&crs=EPSG:4326&bbox=-100,-100,100,100&version=1.3&styles=&width=1000&height=600&layers=Sentinel-1%20IW_GRDH_1S&format=image/png&pol=VV&&request=GetMap'

frames = []

path = 'img/'

for x in date:
    imgurl = url + '&time=' + x
    response = requests.get(imgurl, stream=True)
    with open(path + x[-2:] + '.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    frames.append(Image.open(path + x[-2:] + '.png'))
    os.remove(path + x[-2:] + '.png')

frame_one = frames[0]
frame_one.save("my_awesome2.gif", format="GIF", append_images=frames, save_all=True, duration=1000, loop=0)