"""script para convertir shp de seccion geologica2d a 3d"""
#-------------------------------------------------------------------------------
# Name:        Exportar a 3d
# Purpose:     Exportar pligono 2d a 3d, a partir de linea de seccion
# Author:      Ing. Juan Bernnales
# Created:     10/08/2013
# Copyright:   (c) Ing. Juan Bernnales 2013
# Licence:     <O.1>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
try:
    from osgeo import ogr, gdal
except ImportError:
    import ogr, gdal
import os
import numpy as np
import re
import math
from subprocess import call

def geomtip2nom( tipe ):
    """determinar tipo de geometria"""
    if tipe == ogr.wkbUnknown:
        return 'wkbUnknown'
    elif tipe == ogr.wkbPoint:
        return 'wkbPoint25D'
    elif tipe == ogr.wkbLineString:
        return 'wkbLineString25D'
    elif tipe == ogr.wkbPolygon:
        return 'wkbPolygon25D'
    else:
        return 'wkbUnknown'

def ltrs(esp):
    """devuelve un string"""
    return gdal.EscapeString(esp, gdal.CPLES_XML)

def hvrt(are, rel, sch):
    """crear archivo vrt"""
    outfile = are[:-4] + "3d.vrt"
    layer_list = [os.path.basename(are)[:-4]]
    src_ds = ogr.Open(are, update = 0)
    #crear vrt
    vrt = '<OGRVRTDataSource>\n'
    for name in layer_list:
        layer = src_ds.GetLayerByName(name)
        layerdef = layer.GetLayerDefn()
        vrt += '    <OGRVRTLayer name="%s">\n' % ltrs(name + '3d')
        vrt += '        <SrcDataSource relativeToVRT' + \
                        '="%s" shared="%d">%s</SrcDataSource>\n' \
                        % (rel,not sch,ltrs(are[:-4] + '3d.csv'))
        vrt += '        <GeometryType>%s</GeometryType>\n' \
                        % geomtip2nom(layerdef.GetGeomType())
        vrt += '        <GeometryField>encoding="WKT" ' + \
                        'field="WKT"</GeometryField>\n'
        srs = layer.GetSpatialRef()
        if srs is not None:
            vrt += '        <LayerSRS>%s</LayerSRS>\n' \
                   % (ltrs(srs.ExportToWkt()))

        # Procesar todos los campos.
        for fld_index in range(layerdef.GetFieldCount()):
            src_fd = layerdef.GetFieldDefn( fld_index )
            if src_fd.GetType() == ogr.OFTInteger:
                tipe = 'Integer'
            elif src_fd.GetType() == ogr.OFTString:
                tipe = 'String'
            elif src_fd.GetType() == ogr.OFTReal:
                tipe = 'Real'
            elif src_fd.GetType() == ogr.OFTStringList:
                tipe = 'StringList'
            elif src_fd.GetType() == ogr.OFTIntegerList:
                tipe = 'IntegerList'
            elif src_fd.GetType() == ogr.OFTRealList:
                tipe = 'RealList'
            elif src_fd.GetType() == ogr.OFTBinary:
                tipe = 'Binary'
            elif src_fd.GetType() == ogr.OFTDate:
                tipe = 'Date'
            elif src_fd.GetType() == ogr.OFTTime:
                tipe = 'Time'
            elif src_fd.GetType() == ogr.OFTDateTime:
                tipe = 'DateTime'
            else:
                tipe = 'String'
            vrt += '        <Field name="%s" type="%s"' \
                   % (ltrs(src_fd.GetName()), tipe)
            if not sch:
                vrt += ' src="%s"' % ltrs(src_fd.GetName())
            if src_fd.GetWidth() > 0:
                vrt += ' width="%d"' % src_fd.GetWidth()
            if src_fd.GetPrecision() > 0:
                vrt += ' precision="%d"' % src_fd.GetPrecision()
            vrt += '/>\n'
        vrt += '    </OGRVRTLayer>\n'
    vrt += '</OGRVRTDataSource>\n'
    #guardar en archivo
    open(outfile,'w').write(vrt)
    return outfile

def clin(lin):
    """calcular angulo y obtener coords"""
    capa = lin.GetLayer(0)
    carac = capa.GetFeature(0)
    geom = carac.GetGeometryRef()
    lx1 = geom.GetX(0)
    lx2 = geom.GetX(1)
    ly1 = geom.GetY(0)
    ly2 = geom.GetY(1)
    angl = math.atan2((ly2-ly1),(lx2-lx1)) * (180/np.pi)
    return lx1, ly1, angl

################################################################################

def leerwkt(wkt, linx1, liny1, ang):
    """calcular coords 3d"""
    nums = re.findall(r'\d+(?:\.\d*)?', wkt.rpartition(',')[0])
    coords = zip(*[iter(nums)] * 2)
    crdtrd = []
    for coord in coords:
        xtrsd = linx1 + (math.cos((ang * np.pi/180)) * float(coord[0]))
        ytrsd = liny1 + (math.sin((ang * np.pi/180)) * float(coord[0]))
        prof = float(coord[1])
        crdtrd.append(str(xtrsd) + ' ' + str(ytrsd) + ' ' + str(prof))
    poltrsd = "POLYGON ((" + "," .join(crdtrd) + "))"
    return poltrsd
################################################################################
def leera(polig, linsec1):
    """leer archivo shp, exportarlo a formato WKT y guardar en archivo csv"""
    #crear archivos
    arcsv = open(polig[:-4] + '.csv','w')
    arcsv3d = open(polig[:-4] + '3d.csv', 'w')
    #abrir archivos
    datsen = ogr.GetDriverByName('ESRI Shapefile').Open(polig, 0)
    # obtener las coordenadas iniciales de la linea y el angulo
    x1l, y1l, angulo = clin(ogr.GetDriverByName(
                                            'ESRI Shapefile').Open(linsec1, 0))
    # obtener capa
    capas = datsen.GetLayer(0)
    #obtener nombre de los campos y guardalos en archivo
    arcsv.write('WKT')
    arcsv3d.write('WKT')
    for i in range(capas.GetLayerDefn().GetFieldCount()):
        arcsv.write(',' + str(capas.GetLayerDefn().GetFieldDefn(i).GetName()))
        arcsv3d.write(',' + str(capas.GetLayerDefn().GetFieldDefn(i).GetName()))
    arcsv.write("\n")
    arcsv3d.write("\n")
    for capa in capas:
        atrb = capa.GetGeometryRef().ExportToWkt()
        atrb3d = leerwkt(atrb, x1l, y1l, angulo)
        arcsv.write("\"" + atrb + "\"")
        arcsv3d.write("\"" + atrb3d + "\"")
        for col in range(capa.GetFieldCount()):
            arcsv.write(',' + str(capa.GetField(col)))
            arcsv3d.write(',' + str(capa.GetField(col)))
        arcsv.write("\n")
        arcsv3d.write("\n")
    #limpiar
    del capas, datsen
    arcsv3d.close()
    arcsv.close()
    try:
        os.remove(polig[:-4] + '.csv')
    except OSError, err:
        print ("Error: %s - %s." % (err.filename, err.strerror))

    return polig[:-4] + '3d.csv'
################################################################################

POLSEC = r"C:\PROGSCRIPT\CONVERSION\QGIS\LT3_geol.shp"
LINSEC = r"C:\PROGSCRIPT\CONVERSION\QGIS\LT3.shp"

WKT3D = leera(POLSEC, LINSEC)
VRTAR = hvrt(POLSEC, 1, 0)

RUTA = os.path.dirname(POLSEC)
COMANDO = r"C:\Python27\Lib\site-packages\osgeo\ogr2ogr.exe"
FORMATO = "ESRI Shapefile"
call([COMANDO, "-f", FORMATO, RUTA, VRTAR])
print "La conversion del archivo: "+ POLSEC +" fue exitosa"