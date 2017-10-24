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


        ruta = str(self.dlg.txtruta.text())
        QMessageBox.information(self.dlg, "Los archivos se guardan en:", ruta )

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
        processing.runalg('qgis:extractbyattribute', vias, "TIPO_VIA", 5, "4" , ruta+r"/vias_aptas.shp")
        vias_aptas = iface.addVectorLayer(ruta+r"/vias_aptas.shp", "", "ogr")

        # Generar el buffer de la capa vias aptas, update de los buffer y asignación del tiempo de desplazamiento
        processing.runalg('qgis:fixeddistancebuffer', vias_aptas, 500, 5, True, ruta+r"/buffer_vias500.shp")
        buffer_vias500 = iface.addVectorLayer(ruta+r"/buffer_vias500.shp", "", "ogr")
        processing.runalg('qgis:fieldcalculator',buffer_vias500,"tiempo",1,5,0,True, "35" , ruta+r"/t500.shp" )
        t500 = iface.addVectorLayer(ruta+r"/t500.shp", "", "ogr")

        processing.runalg('qgis:fixeddistancebuffer', vias_aptas, 1000, 5, True, ruta+r"/buffer_vias1000.shp")
        buffer_vias1000 = iface.addVectorLayer(ruta+r"/buffer_vias1000.shp", "", "ogr")
        processing.runalg('qgis:fieldcalculator',buffer_vias1000,"tiempo",1,5,0,True, "70" , ruta+r"/t1000.shp" )
        t1000 = iface.addVectorLayer(ruta+r"/t1000.shp", "", "ogr")

        up1000 = processing.runalg('saga:update', t1000 , t500,False, ruta+r"/up1000.shp")
        up1000 = iface.addVectorLayer(ruta+r"/up1000.shp", "", "ogr")

        processing.runalg('qgis:fixeddistancebuffer', vias_aptas, 1500, 5, True, ruta+r"/buffer_vias1500.shp")
        buffer_vias1500 = iface.addVectorLayer(ruta+r"/buffer_vias1500.shp", "", "ogr")
        processing.runalg('qgis:fieldcalculator',buffer_vias1500,"tiempo",1,5,0,True, "95" , ruta+r"/t1500.shp" )
        t1500 = iface.addVectorLayer(ruta+r"/t1500.shp", "", "ogr")

        up1500 = processing.runalg('saga:update', t1500 , up1000,False, ruta+r"/up1500.shp")
        up1500 = iface.addVectorLayer(ruta+r"/up1500.shp", "", "ogr")

        processing.runalg('qgis:fixeddistancebuffer', vias_aptas, 2000, 5, True,ruta+r"/buffer_vias2000.shp")
        buffer_vias2000 = iface.addVectorLayer(ruta+r"/buffer_vias2000.shp", "", "ogr")
        processing.runalg('qgis:fieldcalculator',buffer_vias2000,"tiempo",1,5,0,True, "120" , ruta+r"/t2000.shp" )
        t2000 = iface.addVectorLayer(ruta+r"/t2000.shp", "", "ogr")

        up2000 = processing.runalg('saga:update', t2000 , up1500,False, ruta+r"/up2000.shp")
        up2000 = iface.addVectorLayer(ruta+r"/up2000.shp", "", "ogr")

        #extracción por atributos de suelos con media, alta y muy alta suceptibilidad
  		#Selecciona la capa suelos (capa de suceptibilidad)
        selectedLayerIndex = self.dlg.capasuelos.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        suelos = selectedLayer
        processing.runalg('qgis:extractbyattribute', suelos, "Codigo_Cla", 3, "2" , ruta+r"/suelos_sal.shp")
        suelos_sal = iface.addVectorLayer(ruta+r"/suelos_sal.shp", "", "ogr")

        #Selección de zonas donde se tomarán las muestras
        #Intersección entre buffer 1km y suelos salinos
        overlayAnalyzer = QgsOverlayAnalyzer()
        overlayAnalyzer.intersection(buffer_vias2000, suelos_sal, ruta+r"/area_muestreo.shp")
        area_muestreo = iface.addVectorLayer(ruta+r"/area_muestreo.shp", "", "ogr")

        #Unir polígonos del área de muestreo (dissolve)
        QgsGeometryAnalyzer().dissolve(area_muestreo,ruta+r"/diss.shp", False, -1 )
        diss = iface.addVectorLayer(ruta+r"/diss.shp", "", "ogr")

        #Generación de sitios de muestreo
        processing.runalg('qgis:randompointsinsidepolygonsfixed', diss, 0, muestra_int, 1500, ruta+r"/sitios_muestreo.shp")
        sitios_muestreo = iface.addVectorLayer(ruta+r"/sitios_muestreo.shp", "", "ogr")

        #buffer 30 metros de los sitios de muestreo para extraer por mascara
        processing.runalg('qgis:fixeddistancebuffer', sitios_muestreo, 30, 5, True, ruta+r"/buffer_sitios30.shp")
        buffer_sitios30 = iface.addVectorLayer(ruta+r"/buffer_sitios30.shp", "", "ogr")

        #Generar mapa pendiente a partir del DEM
  		#Selecciona el DEM
        selectedLayerIndex = self.dlg.capacurvas.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        dem = selectedLayer
        path = processing.runalg('gdalogr:slope', dem, 1, True, False,True, 1, None)
        slope = QgsRasterLayer(path['OUTPUT'],'slope')
        QgsMapLayerRegistry.instance().addMapLayer(slope)

        #extraer por mascara slpoe - buffer 30m sitios de muestreo
        path = processing.runalg('gdalogr:cliprasterbymasklayer',slope,buffer_sitios30,"0",False,True,True,5,0,1,1,1,False,0,False,"",None)
        slope_sitios = QgsRasterLayer(path['OUTPUT'],'slope_sitios')
        QgsMapLayerRegistry.instance().addMapLayer(slope_sitios)

        #poligonizar el raster slope_sitios
        processing.runalg('gdalogr:polygonize', slope_sitios, "pendiente", ruta+r"/slope_sitios_PG.shp")
        slope_sitios_PG = iface.addVectorLayer(ruta+r"/slope_sitios_PG.shp", "", "ogr")

        #actualizar la capa de sitios de muestreo, insertando una columna (pendiente) con el valor de la pendiente
        processing.runalg('saga:addpolygonattributestopoints', sitios_muestreo, slope_sitios_PG, "Codigo_Cla", ruta+r"/puntos_pendiente.shp")
        puntos_pendiente = iface.addVectorLayer(ruta+r"/puntos_pendiente.shp", "", "ogr")

        #determinar factor de ajuste por valor de pendiente
        processing.runalg('qgis:fieldcalculator',puntos_pendiente,"ajuste",0,4,2,True, "((pendiente * 0.02)+1)" , ruta+r"/puntos_pendiente1.shp" )
        puntos_pendiente1 = iface.addVectorLayer(ruta+r"/puntos_pendiente1.shp", "", "ogr")

        #actualizar la capa de sitios de muestreo, insertando una columna (tiempo) con el valor de tiempo de desplazamiento
        processing.runalg('saga:addpolygonattributestopoints', puntos_pendiente1, up2000, "tiempo", ruta+r"/puntos_tiempo.shp")
        puntos_tiempo = iface.addVectorLayer(ruta+r"/puntos_tiempo.shp", "", "ogr")

        #determinar tiempo total de desplazamiento, ajustado por pendiente
        processing.runalg('qgis:fieldcalculator',puntos_tiempo,"tiempo_ajustado",1,4,2,True, "ajuste * tiempo" , ruta+r"/sitos_de_muestreo.shp" )
        sitios_de_muestreo = iface.addVectorLayer(ruta+r"/sitios_de_muestreo.shp", "", "ogr")

        QMessageBox.information(self.dlg, "MENSAJE", "todo corre bien hasta aqui" )


"""




















        #agrerar campo "tiempo" a la tabla de atributos de la capa sitios de muestreo
        #layer = iface.activeLayer()
        #provider = layer.dataProvider()
        #field = QgsField("tiempo", QVariant.Double)
        #provider.addAttributes([field])
        #layer.updateFields()




mapcanvas = iface.mapCanvas()

layers = mapcanvas.layers()

feat_p9 = layers[0].getFeatures().next()
feat_p10 = layers[1].getFeatures().next()

diff1 = feat_p9.geometry().difference(feat_p10.geometry()).exportToWkt()
diff2 = feat_p10.geometry().difference(feat_p9.geometry()).exportToWkt()

print diff1
print diff2
#Interseccion de gemotrías
import processing
anillo_500 = diff1
puntos = "C:/Users/toshiba/Downloads/sitios_muestreo.shp"
processing.runalg('qgis:extractbylocation', puntos, anillo_500, , 1, 0)
processing.runalg('qgis:extractbylocation', input, intersect, touches, overlaps, within, output)




















        #corte de los anillos internos
        processing.runalg('qgis:polygonstolines', buffer_vias400, "C:/Users/toshiba/Downloads/contorno_100.shp")
        contorno_100 = iface.addVectorLayer("C:/Users/toshiba/Downloads/contorno_100.shp", "", "ogr")
        QMessageBox.information(self.dlg, "diferencia simetrica", "contorno_100 ") #+ str(type(corte100)))


        processing.runalg('saga:cutshapeslayer', buffer_vias500, 1, contorno_100,  "C:/Users/toshiba/Downloads/pol_cortado.shp")
        contorno_100 = iface.addVectorLayer("C:/Users/toshiba/Downloads/pol_cortado.shp", "", "ogr")
        QMessageBox.information(self.dlg, "poligono cortado", "poligono_cortado") #+ str(type(corte100)))


        qgis:variabledistancebuffer

  		#Generar el buffer de la capa vias

        feat_p9 = buffer_vias500.getFeatures().next()
        feat_p10 = buffer_vias400.getFeatures().next()

        diff1 = feat_p9.geometry().difference(feat_p10.geometry())
        QMessageBox.information(self.dlg,"MENSAJE", "Tipo de dato: " + str(type(diff1)))
        #print [diff1]
        #diff11 = QgsVectorLayer(diff1,"anillo100", "",  "")

        #generación de puntos aleatorios
        def createQgsPoints(coor):
            return [QgsPoint(coor[i], coor[i + 1]) for i in range(0, len(coor), 2)]


                QMessageBox.information(self.dlg,"MENSAJE", "Tipo de dato: " + str(type(vias)))
        geometry = QgsVectorLayer().getGeometry()
        geom = geometry(vias)
        buffer = vias.buffer(100,-1)
        CRS = vias.crs().postgisSrid()
        URI = "Polygon?crs=epsg:"+str(CRS)+"&field=id:integer""&index=yes"
        mem_layer = QgsVectorLayer(URI, "buffer_100", "memory")
        QgsMapLayerRegistry.instance().addMapLayer(mem_layer)
        mem_layer.startEditing()
        feat2 = QgsFeature()
        feat2.setGeometry(buffer)
        feat2.setAttributes([1])
        mem_layer.addFeature(feat2, True)
        mem_layer.commitChanges()

        layer =  QgsVectorLayer('Polygon', 'poly' , "memory")
        pr = layer.dataProvider()
        poly = QgsFeature()
        #points = [point1,QgsPoint(50,150),point2,QgsPoint(100,50)]
        # or points = [QgsPoint(50,50),QgsPoint(50,150),QgsPoint(100,150),QgsPoint(100,50)]
        poly.setGeometry(QgsGeometry.fromPolygon([diff1]))
        pr.addFeatures([poly])
        layer.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        #processing.runandload("qgis:polygonintersections",buffer_vias200, buffer_vias100, "", "", "C:/Users/toshiba/Downloads"  )
        #processing.runalg('', diferencia, diferencia.shp)
        #diferencia = QgsVectorLayer("C:/Users/toshiba/Downloads ", "diferencia", "ogr" )

        crs = QgsCoordinateReferenceSystem(crs, QgsCoordinateReferenceSystem.PostgisCrsId)
        typeString = "%s?crs=%s" % (typeString, crs.authid())
        layer = QgsVectorLayer(typeString, diff1, "memory")
        layer.dataProvider().addAttributes([QgsField("name", QVariant.String)])
        registry = QgsMapLayerRegistry.instance()
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        return layer


        #QgsMapLayerRegistry.instance().addMapLayer(diff1, True)

        #iface.addVectorLayer(diff1, "diff1", "ogr")
        #diff2 = feat_p10.geometry().difference(feat_p9.geometry()).exportToWkt()
        #print diff1

        #Interseccion de gemotrías
        line = buffer_vias500
        grid = buffer_vias400

        for i in grid.getFeatures():
            for l in line.getFeatures():
                if i.geometry().intersects(l.geometry()):
                # add the selection to the layer
                    grid.select(i.id())

        #seleccionar DEM
		#Se leen los vectores que esten el la lista de capas cargada en QGis
        layers = self.iface.legendInterface().layers()

		#Selecciona la capa vial para hacer multibuffer (capa de vías)
        selectedLayerIndex = self.dlg.capacurvas.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        dem = selectedLayer
        #QgsRasterLayer().slopeAtPercent()

    def guardar_clicked(self):
        self.guardar = QtGui.QFileDialog.getSaveFileName(self.dlg, 'Guardar Archivo',".", "ShapeFile (*.shp)")
        self.dlg.save.setText(self.guardar)

          # display file dialog for output shapefile
        self.outShape.clear()
        fileDialog = QFileDialog()
        fileDialog.setConfirmOverwrite(False)
        outName = fileDialog.getSaveFileName(self, "Output Shapefile",".", "Shapefiles (*.shp)")
        outPath = QFileInfo(outName).absoluteFilePath()
        if not outPath.upper().endswith(".SHP"):
           outPath = outPath + ".shp"
        if outName:
            self.outShape.clear()
        self.outShape.insert(outPath)

"""






