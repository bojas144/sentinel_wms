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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsRasterLayer, QgsProject
from qgis.utils import iface
# Initialize Qt resources from file resources.py
from .resources import *

from .wms_url import WmsUrl

# Import the code for the DockWidget
from .sentinel_wms_dockwidget import SentinelWMSDockWidget
import os.path, shutil, requests
from PIL import Image



class SentinelWMS:
    """QGIS Plugin Implementation."""

    s1Hidden = False

    s1UrlTest = WmsUrl(url='http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map',
                       crs='EPSG:4326',
                       bbox='-100,-100,100,100',
                       version='1.3',
                       width='1000',
                       height='600',
                       layers='Sentinel-1%20IW_GRDH_1S',
                       format='image/png')
    
    s2UrlTest = WmsUrl(url='http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S2-PT.map',
                       crs='EPSG:4326',
                       bbox='-100,-100,100,100',
                       version='1.3',
                       width='1000',
                       height='600',
                       layers='S2MSI2A%20Ukraine',
                       format='image/png')

    __s1UrlTemplate = "IgnoreGetMapUrl=1&format=image/png&layers=Sentinel-1%20IW_GRDH_1S&styles&url=http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map%26"

    __s2UrlTemplate = "IgnoreGetMapUrl=1&crs=EPSG:4326&dpiMode=7&format=image/png&layers=S2MSI2A%20Ukraine&styles&url=http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S2-PT.map%26VERSION%3D1.3.0%26BBOX%3D1381306.275553602492,5183386.680486263707,4883406.024684443139,7991345.14467981644%26CRS%3DEPSG:3857%26WIDTH%3D1004%26HEIGHT%3D806%26LAYERS%3DS2MSI2A%20Ukraine%26STYLES%3D%26DPI%3D96%26MAP_RESOLUTION%3D96%26FORMAT_OPTIONS%3Ddpi:96%26TRANSPARENT%3DTRUE"

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

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

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
            self.dockwidget.pushBtn.clicked.connect(self.btnAddWms)
            self.dockwidget.satList.currentTextChanged.connect(self.hideBox)
            self.dockwidget.pbCopyUrl.clicked.connect(self.btnCopyUrl)
            self.dockwidget.pbCreateGif.clicked.connect(self.createGif)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def btnAddWms(self):
        self.dockwidget.setWarningText("")
        try:
            if self.dockwidget.isChangeActiveLayer():
                oldLayer = iface.activeLayer()
                QgsProject.instance().layerTreeRoot().removeLayer(oldLayer)
            if self.dockwidget.isAddOsmLayer():
                QgsProject.instance().addMapLayer(QgsRasterLayer('type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0','OSM tile layer', 'wms'))
            self.createLayer()
            #print(self.s1UrlTest.getUrl())
        except Exception as e:
            print(e)
            self.dockwidget.setWarningText(str(e))

    def btnCopyUrl(self):
        url = self.s1UrlTest.getMap()
        print(url)

    def createLayer(self):
        urlWithParams, title = self.createUrl()
        newLayer = QgsRasterLayer(self.s1UrlTest.getQgisUrl(), title, 'wms')
        print(self.s1UrlTest.getQgisUrl())
        if not newLayer.isValid():
            raise Exception("Unvalid url")
        else:
            QgsProject.instance().addMapLayer(newLayer)
            self.dockwidget.setCopyUrl(self.s1UrlTest.getMap())

    def createUrl(self):
        # Check which mission was choosen, read parameters
        if self.s1Hidden:
            self.s1UrlTest.url='http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S2-PT.map'
            self.s1UrlTest.layers='S2MSI2A%20Ukraine'
            time = self.dockwidget.getTime([self.dockwidget.s2StartDate, self.dockwidget.s2EndDate])
            maxCc = self.dockwidget.getS2MaxCc()
            params = ['maxCC', maxCc]
            urlWithParams = self.__s2UrlTemplate + "%26maxCC%3D" + maxCc + "%26TIME%3D" + time
            layerTitle = 'Sentinel-2' + ' ' + 'maxCC:' + maxCc + ' ' + 'time:' + time
        else:
            self.s1UrlTest.url='http://64.225.135.141.nip.io/?map%3D/etc/mapserver/S1-PT.map'
            self.s1UrlTest.layers='Sentinel-1%20IW_GRDH_1S'
            pol = self.dockwidget.getS1Pol()
            params = ['pol', pol]
            time = self.dockwidget.getTime([self.dockwidget.s1StartDate, self.dockwidget.s1EndDate])
            urlWithParams = self.__s1UrlTemplate + "pol%3D" + pol + "%26TIME%3D" + time
            layerTitle = 'Sentinel-1' + ' ' + 'pol:' + pol + ' ' + 'time:' + time
        crs = self.dockwidget.getEpsg()
        ###
        self.s1UrlTest.time = time
        self.s1UrlTest.crs = crs
        self.s1UrlTest.params = (params,)
        ###
        urlWithParams = 'crs=' + crs + '&' + urlWithParams
        return urlWithParams, layerTitle
    
    def chooseDirPath(self):
        dirname = str(QFileDialog.getExistingDirectory(self.dockwidget, "Select Directory"))
        print(dirname)

    def createGif(self):
        try:
            days = self.dockwidget.getTimestap()
            frames = []
            url = self.s1UrlTest
            dirname = str(QFileDialog.getExistingDirectory(self.dockwidget, "Select Directory"))
            if len(dirname) == 0:
                return
            dirname = dirname + '/'
            print(dirname)
            for d in days:
                url.time = d
                response = requests.get(url.getMap(), stream=True)
                with open(dirname + d[-2:] + '.png', 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                frames.append(Image.open(dirname + d[-2:] + '.png'))
                os.remove(dirname + d[-2:] + '.png')
            del url
            frame_one = frames[0]
            frame_one.save(dirname + "Sentinel1.gif", format="GIF", append_images=frames, save_all=True, duration=1000, loop=0)
        except Exception as e:
            print(e)
            self.dockwidget.setWarningText(str(e))

    def hideBox(self):
        if self.s1Hidden:
            self.dockwidget.s1Gb.show()
            self.dockwidget.s2Gb.hide()
            self.s1Hidden = False
        else:
            self.dockwidget.s1Gb.hide()
            self.dockwidget.s2Gb.show()
            self.s1Hidden = True
