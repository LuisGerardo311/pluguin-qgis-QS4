# pluguin-qgis-QS4
#logica el pluguin


# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Soil
                                 A QGIS plugin
 el plugin genera sitios de muestreo para suelos degradados por salinización
                              -------------------
        begin                : 2017-09-30
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Lina Viasús - Gerardo Chaparro
        email                : lviasus1@gmail.com - ingerardoch@gmail.com
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import iface
from qgis.analysis import QgsGeometryAnalyzer
from PyQt4 import QtCore, QtGui
from osgeo import ogr
from qgis.gui import QgsMessageBar
import processing
import random
import sys
sys.path.append('C:\Users\toshiba\.qgis2\python\plugins')
from qgis.analysis import *

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from soil_logyc_dialog import SoilDialog
import os.path




class Soil:
    """QGIS Plugin Implementation."""

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
        #pluginPath = QFileInfo(os.path.realpath(__file__)).path()
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Soil_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QS4')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Soil')
        self.toolbar.setObjectName(u'Soil')

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
        return QCoreApplication.translate('Soil', message)


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

        # Create the dialog (after translation) and keep reference
        self.dlg = SoilDialog()
        self.dlg.gen_muestreo.clicked.connect(self.gen_muestreo)
        # Boton Guardar
        #self.dlg.guardar.clicked.connect(self.guardar_clicked)

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

        icon_path = ':/plugins/Soil/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'QS4'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QS4'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        self.dlg.capaarea.clear()
        self.dlg.capavias.clear()
        self.dlg.capacurvas.clear()
        self.dlg.capasuelos.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                layer_list.append(layer.name())
            else:
                layer_list.append(layer.name())

        self.dlg.capaarea.addItems(layer_list)
        self.dlg.capacurvas.addItems(layer_list)
        self.dlg.capavias.addItems(layer_list)
        self.dlg.capasuelos.addItems(layer_list)


        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass


    def gen_muestreo(self):

		#Se leen los vectores que esten el la lista de capas cargada en QGis
        layers = self.iface.legendInterface().layers()

		#Selecciona la capa de universo muestreal (área de estudio)
        selectedLayerIndex = self.dlg.capaarea.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        area_est = selectedLayer

        #inicio de la edición
        selectedLayer.startEditing()

        #agregar nuevo campo
        selectedLayer.dataProvider().addAttributes([QgsField("Area_Ha", QVariant.Int)])

        #Cierra edicion
        selectedLayer.commitChanges()

        #Activa edicion
        selectedLayer.startEditing()
        idx = selectedLayer.fieldNameIndex( "Area_Ha" )

        #Calculo de área en Ha mediante expresion
        e = QgsExpression( "$area/10000" )
        e.prepare(selectedLayer.pendingFields())
        for f in selectedLayer.getFeatures():
                value = e.evaluate (f)
                selectedLayer.changeAttributeValue (f.id(), idx, value)
        area_est.deselect(0)
        #atualizción de columna
        #cierre de edición
        selectedLayer.updateFields()
        selectedLayer.commitChanges()


        # definición de variables para estimar tamaño de muestra
        marg_error = self.dlg.marg_error.value()
        nivel_conf = self.dlg.nivel_conf.value()
        universo = int(value)

        #selección del tamaño de muestra
        if universo < 100000:
            muestra = (universo * (nivel_conf*nivel_conf * 0.5 * 0.5)) / ((universo - 1) * (marg_error*marg_error) + (nivel_conf * 0.5* 0.5))
            QMessageBox.information(self.dlg,"POBLACION FINITA", "Tamano de muestra: " + str(int(muestra)))

        else:
            muestra = ((nivel_conf**2) * 0.5 * 0.5) / (marg_error**2)
            QMessageBox.information(self.dlg,"POBLACION INFINITA", "Tamano de muestra: " + str(int(muestra)))

        #Se parsea a entero el tamaño de muestra
        muestra_int = int(muestra)

        #Generación de los buffer sobre la capa vías
        # Se leen los vectores que esten el la lista de capas cargada en QGis
        layers = self.iface.legendInterface().layers()

        # Selecciona la capa vial para hacer multibuffer (capa de vías)
        selectedLayerIndex = self.dlg.capavias.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        vias = selectedLayer

        #extracción de vías tipo 1, 2, 3, 4 (aptas para trasporte en automovil)
        processing.runalg('qgis:extractbyattribute', vias, "TIPO_VIA", 5, "4" , "C:/Users/toshiba/Downloads/vias_aptas.shp")
        vias_aptas = iface.addVectorLayer("C:/Users/toshiba/Downloads/vias_aptas.shp", "", "ogr")

        # Generar el buffer de la capa vias aptas
        #processing.runalg('qgis:fixeddistancebuffer', vias_aptas, 500, 5, True, "C:/Users/toshiba/Downloads/buffer_vias500.shp")
        #buffer_vias500 = iface.addVectorLayer("C:/Users/toshiba/Downloads/buffer_vias500.shp", "", "ogr")

        #processing.runalg('qgis:fixeddistancebuffer', vias_aptas, 1000, 5, True, "C:/Users/toshiba/Downloads/buffer_vias1000.shp")
        #buffer_vias1000 = iface.addVectorLayer("C:/Users/toshiba/Downloads/buffer_vias1000.shp", "", "ogr")

        #processing.runalg('qgis:fixeddistancebuffer', vias_aptas, 1500, 5, True, "C:/Users/toshiba/Downloads/buffer_vias1500.shp")
        #buffer_vias1500 = iface.addVectorLayer("C:/Users/toshiba/Downloads/buffer_vias1500.shp", "", "ogr")

        processing.runalg('qgis:fixeddistancebuffer', vias_aptas, 2000, 5, True, "C:/Users/toshiba/Downloads/buffer_vias2000.shp")
        buffer_vias2000 = iface.addVectorLayer("C:/Users/toshiba/Downloads/buffer_vias2000.shp", "", "ogr")

        #extracción por atributos de suelos con media, alta y muy alta suceptibilidad
  		#Selecciona la capa suelos (capa de suceptibilidad)
        selectedLayerIndex = self.dlg.capasuelos.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        suelos = selectedLayer
        processing.runalg('qgis:extractbyattribute', suelos, "Codigo_Cla", 3, "2" , "C:/Users/toshiba/Downloads/suelos_sal.shp")
        suelos_sal = iface.addVectorLayer("C:/Users/toshiba/Downloads/suelos_sal.shp", "", "ogr")

        #Selección de zonas donde se tomarán las muestras
        #Intersección entre buffer 1km y suelos salinos
        overlayAnalyzer = QgsOverlayAnalyzer()
        overlayAnalyzer.intersection(buffer_vias2000, suelos_sal, "C:/Users/toshiba/Downloads/area_muestreo.shp")
        area_muestreo = iface.addVectorLayer("C:/Users/toshiba/Downloads/area_muestreo.shp", "", "ogr")

        #Unir polígonos del área de muestreo (dissolve)
        QgsGeometryAnalyzer().dissolve(area_muestreo,"C:/Users/toshiba/Downloads/diss.shp", False, -1 )
        diss = iface.addVectorLayer("C:/Users/toshiba/Downloads/diss.shp", "", "ogr")

        #Generación de sitios de muestreo
        processing.runalg('qgis:randompointsinsidepolygonsfixed', diss, 0, muestra_int, 0, "C:/Users/toshiba/Downloads/sitios_muestreo.shp")
        sitios_muestreo = iface.addVectorLayer("C:/Users/toshiba/Downloads/sitios_muestreo.shp", "", "ogr")

        #buffer 30 metros de los sitios de muestreo para extraer por mascara
        processing.runalg('qgis:fixeddistancebuffer', sitios_muestreo, 30, 5, True, "C:/Users/toshiba/Downloads/buffer_sitios30.shp")
        buffer_sitios30 = iface.addVectorLayer("C:/Users/toshiba/Downloads/buffer_sitios30.shp", "", "ogr")

        #Generar mapa pendiente a partir del DEM
  		#Selecciona el DEM
        selectedLayerIndex = self.dlg.capacurvas.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        dem = selectedLayer
        processing.runalg('gdalogr:slope', dem, 1, True, False,True, 1, "C:/Users/toshiba/Downloads/slope.tif")
        slope = iface.addRasterLayer("C:/Users/toshiba/Downloads/slope.tif", "SLOPE")

        #extraer por mascara slpoe - buffer 30m sitios de muestreo



        #migrar campo de un poligono (categoria de salinización) a la capa de puntos de muestreo
        processing.runalg('saga:addpolygonattributestopoints', sitios_muestreo, area_muestreo, "Codigo_Cla", "C:/Users/toshiba/Downloads/puntos_clase.shp")
        puntos_clase = iface.addVectorLayer("C:/Users/toshiba/Downloads/puntos_clase.shp", "", "ogr")




        QMessageBox.information(self.dlg, "MENSAJE", "todo corre bien hasta aqui" )
