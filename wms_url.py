class WmsUrl:
    params = {
        'url': '',
        'crs': '',
        'bbox': '',
        'version': '',
        'width': '',
        'height': '',
        'layers': '',
        'format': '',
        'time': '',
    }

    url = ''
    crs = ''
    bbox = ''
    version = ''
    styles = ''
    width = ''
    height = ''
    layers = ''
    format = ''
    time = ''
    params = {}
    _wmsUrl = ''

    def __init__(self, url='', crs='', bbox='', version='', styles='', width='', height='', layers='', format='', time='', *params):
        self.url = url
        self.crs = crs
        self.bbox = bbox
        self.version = version
        self.width = width
        self.height = height
        self.layers = layers
        self.format = format
        self.time = time
        self.params = params

    def getUrl(self, urlSeparator):
        url = 'crs=' + self.crs + '&' + 'bbox=' + self.bbox + '&' + 'version=' + self.version + '&' + 'styles=' + self.styles + '&' + 'width=' + self.width + '&' + 'height=' + self.height + '&' + 'layers=' + self.layers + '&' + 'format=' + self.format + '&' + "url=" + self.url + urlSeparator
        # if len(self.params) > 0:
        #     url = url + '&' + self.params[0][0] + '=' + self.params[0][1]
        return url

    def getQgisUrl(self):
        qgisUrl = 'IgnoreGetMapUrl=1&' + self.getUrl('%26')
        #+ '%3D' + self.params[0][0] + '%26' + self.params[0][1]
        if len(self.params) > 0:
            qgisUrl = qgisUrl + self.params[0][0] + '%3D' + self.params[0][1] + '%26'
        qgisUrl = qgisUrl + 'time%3D' + self.time
        return qgisUrl

    def getMap(self):
        mapUrl = self.url + '&' + 'crs=' + self.crs + '&' + 'bbox=' + self.bbox + '&' + 'version=' + self.version + '&' + 'styles=' + self.styles + '&' + 'width=' + self.width + '&' + 'height=' + self.height + '&' + 'layers=' + self.layers + '&' + 'format=' + self.format + '&' + 'time=' + self.time
        if len(self.params) > 0:
            mapUrl = mapUrl + '&' + self.params[0][0] + '=' + self.params[0][1] + '&'
        mapUrl = mapUrl + '&request=GetMap'
        return mapUrl
    
    def getTitle(self):
        return self.layers + ' ' + self.time

dummy = WmsUrl('http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map',
               'EPSG:4326',
               '-100,-100,100,100',
               '1.3',
               '',
               '600',
               '400',
               'Sentinel-1%20IW_GRDH_1S',
               'image/png',
               '2023-05-01/2023-05-05',
               ['pol', 'VV'])