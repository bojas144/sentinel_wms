# s1Url = 'IgnoreGetMapUrl=1&crs=EPSG:4326&dpiMode=7&format=image/png&layers=Sentinel-1%20IW_GRDH_1S&styles&BBOX=-20,-50,20,50&url=http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map%26VERSION%3D1.3.0%26BBOX%3D-20,-50,20,50%26CRS%3DEPSG:3857%26WIDTH%3D10%26HEIGHT%3D10%26LAYERS%3DSentinel-1%20IW_GRDH_1S%26STYLES%3D%26DPI%3D100%26MAP_RESOLUTION%3D100%26FORMAT_OPTIONS%3Ddpi:100%26TRANSPARENT%3DFALSE%26'
# urlWithParams = s1Url + "pol%3D" + 'VV' + "%26TIME%3D" + '2023-05-01/2023-05-05'
# newLayer = QgsRasterLayer(urlWithParams, 'wms1', 'wms')
# QgsProject.instance().addMapLayer(newLayer)