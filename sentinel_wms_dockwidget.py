# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SentinelWMSDockWidget
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

import os

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QLocale
from qgis.utils import iface
from datetime import timedelta

#Import qgis libraries for python
from qgis.core import QgsRasterLayer, QgsProject

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sentinel_wms_dockwidget_base.ui'))


class SentinelWMSDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(SentinelWMSDockWidget, self).__init__(parent)
        """Setup gui on start"""
        self.setupUi(self)
        self.initPolList()
        self.initSatList()
        self.initEpsgList()
        self.s2Gb.hide()
        self.s2Gif.hide()
        self.warning.setStyleSheet("color: red;")
        self.qowOpacity.opacityChanged.connect(self.setLayerOpacity)
        self.s1StartDate.calendarWidget().setLocale(QLocale(QLocale.English))
        self.s1EndDate.calendarWidget().setLocale(QLocale(QLocale.English))
        self.s2StartDate.calendarWidget().setLocale(QLocale(QLocale.English))
        self.s2EndDate.calendarWidget().setLocale(QLocale(QLocale.English))
        self.deS1GifStart.calendarWidget().setLocale(QLocale(QLocale.English))
        self.deS1GifEnd.calendarWidget().setLocale(QLocale(QLocale.English))
        self.deS2GifStart.calendarWidget().setLocale(QLocale(QLocale.English))
        self.deS2GifEnd.calendarWidget().setLocale(QLocale(QLocale.English))

    def initSatList(self):
        self.satList.addItem('Sentinel1')
        self.satList.addItem('Sentinel2')

    def initPolList(self):
        availablePolarisations = [
            'VV',
            'VH',
            'HV',
            'HH'
        ]
        for x in availablePolarisations: self.polList.addItem(x)

    def initEpsgList(self):
        preffix = 'EPSG:'
        availableEpsg = [
            '4326',
            '3857',
            '2180'
        ]
        for x in availableEpsg: self.epsgList.addItem(preffix + x)

    def getSelectedMission(self):
        return self.satList.currentIndex()
    
    def getSelectedPolarisation(self):
        return self.polList.currentIndex()

    def getEpsg(self):
        return str(self.epsgList.currentText())

    def getS1Pol(self):
        return str(self.polList.currentText())

    def getS1Time(self):
        return (self.s1StartDate, self.s1EndDate)
    
    def getS2Time(self):
        return (self.s2StartDate, self.s2EndDate)
        
    def getTime(self, dateEdits):
        startDate = dateEdits[0].date().toPyDate()
        endDate = dateEdits[1].date().toPyDate()
        if (endDate < startDate):
            raise Exception("Start date cannot be later than end date!")
        return str(startDate) + '/' + str(endDate)
    
    def getTimestap(self, dateEdits):
        startDate = dateEdits[0].date().toPyDate()
        endDate = dateEdits[1].date().toPyDate()
        if (endDate < startDate):
            raise Exception("Start date cannot be later than end date!")
        delta = endDate - startDate   # returns timedelta
        days = []
        for i in range(delta.days + 1):
            days.append(str(startDate) + '/' + str(startDate + timedelta(days=i)))
        return days
    
    def setWarningText(self, text):
        self.warning.setText(text)

    def isChangeActiveLayer(self):
        if self.cbChangeActiveLayer.isChecked():
            return True
        else:
            return False
        
    def isAddOsmLayer(self):
        if self.cbAddOsmTileLayer.isChecked():
            return True
        else:
            return False
        
    def setLayerOpacity(self):
        activeLayer = iface.activeLayer()
        if activeLayer != None:
            activeLayer.setOpacity(self.qowOpacity.opacity())
            activeLayer.reload()

    def resetQowOpacity(self):
        if iface.activeLayer() is None:
            self.qowOpacity.setOpacity(1)
        else:
            self.qowOpacity.setOpacity(iface.activeLayer().opacity())

    def clearWarning(self):
        if len(self.warning.text()) is not '':
            self.warning.setText('')

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

