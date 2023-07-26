# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SentinelWMS
                                 A QGIS plugin
 Plugin that shares CloudFerro's data from Sentinel
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-07-04
        git sha              : $Format:%H$
        copyright            : (C) 2023 by CloudFerro
        email                : cloudferro@cloudferro.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QTimer
from qgis.PyQt.QtGui import QIcon, QFont
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QDialog, QApplication
from qgis.core import *
from qgis.utils import iface
# Initialize Qt resources from file resources.py
from .resources import *

from .wms_url import WmsUrl

# Import the code for the DockWidget
from .sentinel_wms_dockwidget import SentinelWMSDockWidget
import os.path, shutil, requests
from PIL import Image, ImageDraw, ImageFont
from sys import platform

def getOsFontsDirectory():
    if platform == 'linux' or platform == 'linux2':
        return '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf'
    elif platform == "darwin":
        print('os x')
    elif platform == "win32":
        print('win32')

class SentinelWMS:
    """QGIS Plugin Implementation."""

    selectedMission = 0

    __s1UrlTemplate = WmsUrl(url='http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map',
                       crs='EPSG:4326',
                       bbox='-90,-180,90,180',
                       version='1.3',
                       width='1600',
                       height='1024',
                       layers='Sentinel-1%20IW_GRDH_1S',
                       format='image/png')
    
    __s2UrlTemplate = WmsUrl(url='http://64.225.135.141.nip.io/?map=/etc/mapserver/piramida.map',
                       crs='EPSG:4326',
                       bbox='44.087585,20.961914,53.252069,40.561523',
                       version='1.3',
                       width='1600',
                       height='1024',
                       layers='CLD%20Masking',
                       format='image/png')
    
    _bboxS1 = [(-180,180),(-90,90)]
    _bboxS2 = [(-180,180),(-85,85)]
    _availableCrs = ['EPSG:4326', 'EPSG:2180', 'EPSG:3857']
    
    _timer = QTimer()

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SentinelWMS_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CloudFerro Sentinel WMS plugin')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SentinelWMS')
        self.toolbar.setObjectName(u'SentinelWMS')

        #print "** INITIALIZING SentinelWMS"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SentinelWMS', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/sentinel_wms/cf-logo.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Sentinel WMS'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING SentinelWMS"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.dockwidget = None
        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD SentinelWMS"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&CloudFerro Sentinel WMS plugin'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True
            
            #print "** STARTING SentinelWMS"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = SentinelWMSDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.dockwidget.pushBtn.clicked.connect(self.dockwidget.clearWarning)
            self.dockwidget.pushBtn.clicked.connect(self.btnAddWms)
            #self.dockwidget.satList.currentIndexChanged.connect(self.dockwidget.getSelectenMission)
            self.dockwidget.satList.currentIndexChanged.connect(self.hideBox)
            self.dockwidget.pbCopyUrl.clicked.connect(self.dockwidget.clearWarning)
            self.dockwidget.pbCopyUrl.clicked.connect(self.btnCopyUrl)
            self.dockwidget.pbS1CreateGif.clicked.connect(self.dockwidget.clearWarning)
            self.dockwidget.pbS1CreateGif.clicked.connect(self.createGif)
            self.dockwidget.pbS2CreateGif.clicked.connect(self.dockwidget.clearWarning)
            self.dockwidget.pbS2CreateGif.clicked.connect(self.createGif)
            self.dockwidget.pbLayout.clicked.connect(self.createPrintLayout)
            iface.layerTreeView().currentLayerChanged.connect(self.dockwidget.resetQowOpacity)
            self.dockwidget.pbAddOsmTileLayer.clicked.connect(self.addOsmTile)
            self._timer.timeout.connect(self.clearLbCopyUrl)
            self._timer.timeout.connect(self.clearLbCreateGif)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def hideBox(self):
        self.selectedMission = self.dockwidget.getSelectedMission()
        if self.selectedMission == 0:
            self.dockwidget.s2Gb.hide()
            self.dockwidget.s1Gb.show()
            self.dockwidget.s2Gif.hide()
            self.dockwidget.s1Gif.show()
        elif self.selectedMission == 1:
            self.dockwidget.s1Gb.hide()
            self.dockwidget.s2Gb.show()
            self.dockwidget.s1Gif.hide()
            self.dockwidget.s2Gif.show()

    def getTemplateUrl(self):
        if self.selectedMission == 1:
            return self.__s2UrlTemplate
        elif self.selectedMission == 0:
            return self.__s1UrlTemplate

    def clearLbCopyUrl(self):
        self.dockwidget.lbCopyUrl.setText('')
        self._timer.stop()

    def clearLbCreateGif(self):
        self.dockwidget.lbCreateGif.setText('')
        self._timer.stop()

    def timerStart(self, obj, txt):
        obj.setText(txt)
        self._timer.start(2000)

    def saveFileDialog(self, extension):
        dialog = QFileDialog()
        dialog.setDirectory(os.path.join(QgsProject.instance().homePath()))
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
        dialog.setDefaultSuffix(extension)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(['{} (*.{})'.format(extension, extension),'all (*.*)'])
        if dialog.exec_() == QDialog.Accepted:
            return dialog.selectedFiles()[0]
        else:
            return

    def btnAddWms(self):
        self.dockwidget.setWarningText("")
        try:
            if self.dockwidget.isChangeActiveLayer():
                oldLayer = iface.activeLayer()
                QgsProject.instance().layerTreeRoot().removeLayer(oldLayer)
            # if self.dockwidget.isAddOsmLayer():
            #     QgsProject.instance().addMapLayer(QgsRasterLayer('type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0','OSM tile layer', 'wms'))
            self.createLayer()
        except Exception as e:
            print(e)
            self.dockwidget.setWarningText(str(e))

    def addOsmTile(self):
        rlayer = QgsRasterLayer('type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0','OSM tile layer', 'wms')
        QgsProject.instance().addMapLayer(rlayer, False)
        layerTree = iface.layerTreeCanvasBridge().rootGroup()
        layerTree.insertChildNode(-1, QgsLayerTreeLayer(rlayer))

    def btnCopyUrl(self):
        try:
            url = self.getTemplateUrl()
            self.checkCrs()
            url.bbox = self.setBBox()
            cb = QApplication.clipboard()
            cb.setText(url.getMap())
            self.timerStart(self.dockwidget.lbCopyUrl, 'Copied to url!')
        except Exception as e:
            print(e)
            self.dockwidget.setWarningText(str(e))

    def createLayer(self):
        urlWithParams, title = self.createUrl()
        newLayer = QgsRasterLayer(urlWithParams.getQgisUrl(), title, 'wms')
        if not newLayer.isValid():
            raise Exception("Unvalid url")
        else:
            QgsProject.instance().addMapLayer(newLayer)

    def createUrl(self):
        # Check which mission was choosen, read parameters
        if self.selectedMission == 1:
            time = self.dockwidget.getTime([self.dockwidget.s2StartDate, self.dockwidget.s2EndDate])
            maxCc = self.dockwidget.getS2MaxCc()
            params = ['maxCC', maxCc]
            layerTitle = 'Sentinel-2' + ' ' + 'maxCC:' + maxCc + ' ' + 'time:' + time
        elif self.selectedMission == 0:
            pol = self.dockwidget.getS1Pol()
            params = ['pol', pol]
            time = self.dockwidget.getTime([self.dockwidget.s1StartDate, self.dockwidget.s1EndDate])
            layerTitle = 'Sentinel-1' + ' ' + 'pol:' + pol + ' ' + 'time:' + time
        urlWithParams = self.getTemplateUrl()
        urlWithParams.time = time
        urlWithParams.crs = self.dockwidget.getEpsg()
        urlWithParams.params = (params,)
        return urlWithParams, layerTitle
    
    def createGif(self):
        try:
            if self.selectedMission == 0:
                days = self.dockwidget.getTimestap([self.dockwidget.deS1GifStart, self.dockwidget.deS1GifEnd])
            elif self.selectedMission == 1:
                days = self.dockwidget.getTimestap([self.dockwidget.deS2GifStart, self.dockwidget.deS2GifEnd])            
            frames = []
            url = self.getTemplateUrl()
            url.bbox = self.setBBox()
            pluginDir = os.path.dirname(os.path.realpath(__file__))
            filename = self.saveFileDialog('gif')
            if filename == None:
                return
            imgPath = pluginDir + '/imgfor.png'
            cfLogo = Image.open(pluginDir + '/cf-logo.png')
            cfLogo.thumbnail((100,100))
            margin = 10
            fontPath = getOsFontsDirectory()
            for d in days:
                url.time = d
                response = requests.get(url.getMap(), stream=True)
                with open(imgPath, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                with Image.open(imgPath) as img:
                    myFont = ImageFont.truetype(font=fontPath,size=30)
                    ImageDraw.Draw(img).text((10, 10), d, fill=(0,0,0), font=myFont)
                    img.paste(cfLogo, (0 + margin, img.height - cfLogo.height - margin), cfLogo)
                    frames.append(img)
                os.remove(imgPath)
            del url
            frame_one = frames[0]
            frame_one.save(filename, format="GIF", append_images=frames, save_all=True, duration=1000, loop=0)
            self.timerStart(self.dockwidget.lbCreateGif, 'Created gif successfuly!')
        except Exception as e:
            print(e)
            self.dockwidget.setWarningText(str(e))

    def setBBox(self):
            xmin = iface.mapCanvas().extent().xMinimum()
            xmax = iface.mapCanvas().extent().xMaximum()
            ymin = iface.mapCanvas().extent().yMinimum()
            ymax = iface.mapCanvas().extent().yMaximum()
            bbx = str(ymin) + ","+ str(xmin) + "," + str(ymax) + "," + str(xmax)
            # if self.selectedMission == 0:
            #     exBbox = self._bboxS1
            # elif self.selectedMission == 1:
            #     exBbox = self._bboxS2
            # if (round(xmax) not in range(exBbox[0][0], exBbox[0][1])) or (round(xmin) not in range(exBbox[0][0], exBbox[0][1])) or (round(ymin) not in range(exBbox[1][0], exBbox[1][1])) or (round(ymax) not in range(exBbox[1][0], exBbox[1][1])):
            #     raise Exception(f"BBOX too big:\n {ymin}\n {xmin}\n {ymax}\n {xmax}\n")
            # del exBbox
            return bbx
    
    def checkCrs(self):
        crs = iface.mapCanvas().mapSettings().destinationCrs().authid()
        if crs in self._availableCrs:
            pass
        else:
            raise Exception('Unavailable CRS!')

    def createPrintLayout(self):
        activeLayer = iface.activeLayer()
        layers = [l for l in QgsProject.instance().mapLayers().values()]
        x = [x for x in range(len(layers))]
        x.sort(reverse=True)
        names = [l.name() for l in QgsProject.instance().mapLayers().values()]
        names = [names[i] for i in x]
        layers = [layers[i] for i in x]
        project = QgsProject.instance()
        manager = project.layoutManager()
        layoutName = 'Layout1'
        layouts_list = manager.printLayouts()
        # remove any duplicate layouts
        for layout in layouts_list:
            if layout.name() == layoutName:
                manager.removeLayout(layout)
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(layoutName)
        manager.addLayout(layout)
        # create map item in the layout
        map = QgsLayoutItemMap(layout)
        map.setRect(20, 20, 20, 20)
        # set the map extent
        ms = QgsMapSettings()
        ms.setLayers([activeLayer]) # set layers to be mapped
        rect = QgsRectangle(ms.fullExtent())
        rect.scale(1.1)
        ms.setExtent(rect)
        map.setExtent(rect)
        layout.addLayoutItem(map)
        map.attemptMove(QgsLayoutPoint(5, 20, QgsUnitTypes.LayoutMillimeters))
        map.attemptResize(QgsLayoutSize(190, 177, QgsUnitTypes.LayoutMillimeters))
        # set scalebar extent
        scalebar = QgsLayoutItemScaleBar(layout)
        scalebar.setStyle('Single Box')
        scalebar.setLinkedMap(map)
        scalebar.setSegmentSizeMode(QgsScaleBarSettings.SegmentSizeMode.SegmentSizeFitWidth)
        scalebar.setMaximumBarWidth(80)
        scalebar.setUnits(QgsUnitTypes.DistanceUnit.DistanceKilometers)
        scalebar.setUnitLabel('km')
        layout.addLayoutItem(scalebar)
        scalebar.attemptMove(QgsLayoutPoint(202, 182, QgsUnitTypes.LayoutMillimeters))
        # set title extent
        title = QgsLayoutItemLabel(layout)
        title.setText("Print Layout for Cloudferro's WMS")
        title.setFont(QFont("Ubuntu regular", 18, QFont.Bold))
        title.adjustSizeToText()
        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(88, 8, QgsUnitTypes.LayoutMillimeters))
        # set legend extent
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle("Legend")
        legend.setWmsLegendHeight(0)
        legend.setWmsLegendWidth(0)
        layout.addLayoutItem(legend)
        legend.attemptMove(QgsLayoutPoint(202, 20, QgsUnitTypes.LayoutMillimeters))
        # export
        pdfPath = self.saveFileDialog('pdf')
        if pdfPath == None:
            return
        exporter = QgsLayoutExporter(layout)
        exporter.exportToPdf(pdfPath, QgsLayoutExporter.PdfExportSettings())
