# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function

# ----------------------------------------------------------------------------
# Name:         InfosSpatialite
# Purpose:      Use OGR to read into Spatialite databases (ie SQLite with
#               geospatial extension)
#
# Author:       Julien Moura (https://github.com/Guts/)
#
# Python:       2.7.x
# Created:      16/11/2014
# Updated:      17/11/2014
# Licence:      GPL 3
# ----------------------------------------------------------------------------

# ############################################################################
# ######### Libraries #############
# #################################
# Standard library
from collections import OrderedDict  # Python 3 backported
import logging
from os import path   # files and folder managing
from time import localtime, strftime

# 3rd party libraries
from osgeo import ogr
from osgeo import gdal
from gdalconst import *

# ############################################################################
# ######## Classes #############
# ###############################


class OGRErrorHandler(object):
    def __init__(self):
        """Callable error handler.

        see: http://trac.osgeo.org/gdal/wiki/PythonGotchas#Exceptionsraisedincustomerrorhandlersdonotgetcaught
        and http://pcjericks.github.io/py-gdalogr-cookbook/gdal_general.html#install-gdal-ogr-error-handler
        """
        self.err_level = gdal.CE_None
        self.err_type = 0
        self.err_msg = ''

    def handler(self, err_level, err_type, err_msg):
        """Makes errors messages more readable."""
        # available types
        err_class = {gdal.CE_None: 'None',
                     gdal.CE_Debug: 'Debug',
                     gdal.CE_Warning: 'Warning',
                     gdal.CE_Failure: 'Failure',
                     gdal.CE_Fatal: 'Fatal'
                     }
        # getting type
        err_type = err_class.get(err_type, 'None')

        # cleaning message
        err_msg = err_msg.replace('\n', ' ')

        # disabling OGR exceptions raising to avoid future troubles
        ogr.DontUseExceptions()

        # propagating
        self.err_level = err_level
        self.err_type = err_type
        self.err_msg = err_msg

        # end of function
        return self.err_level, self.err_type, self.err_msg


class ReadSpaDB():
    def __init__(self, spadbpath, dico_spadb, tipo, txt=''):
        """Use OGR functions to extract basic informations about
        geographic vector file
        and store into dictionaries.

        spapath = path to the Spatialite DB
        dico_spadb = dictionary for global informations
        dico_fields = dictionary for the fields' informations
        li_fieds = ordered list of fields
        tipo = format
        text = dictionary of text in the selected language
        """
        # handling ogr specific exceptions
        ogrerr = OGRErrorHandler()
        errhandler = ogrerr.handler
        gdal.PushErrorHandler(errhandler)
        ogr.UseExceptions()
        self.alert = 0

        # counting alerts
        self.alert = 0

        # opening GDB
        try:
            spadb = ogr.Open(spadbpath, 0)
        except Exception:
            self.erratum(dico_spadb, spadbpath, u'err_corrupt')
            self.alert = self.alert + 1
            return None

        # GDB name and parent folder
        dico_spadb['name'] = path.basename(spadb.GetName())
        dico_spadb['folder'] = path.dirname(spadb.GetName())
        # layers count and names
        dico_spadb['layers_count'] = spadb.GetLayerCount()
        li_layers_names = []
        li_layers_idx = []
        dico_spadb['layers_names'] = li_layers_names
        dico_spadb['layers_idx'] = li_layers_idx

        # cumulated size
        total_size = path.getsize(spadbpath)
        dico_spadb[u"total_size"] = self.sizeof(total_size)

        # global dates
        dico_spadb[u'date_actu'] = strftime('%d/%m/%Y',
                                          localtime(path.getmtime(spadbpath)))
        dico_spadb[u'date_crea'] = strftime('%d/%m/%Y',
                                          localtime(path.getctime(spadbpath)))
        # total fields count
        total_fields = 0
        dico_spadb['total_fields'] = total_fields
        # total objects count
        total_objs = 0
        dico_spadb['total_objs'] = total_objs
        # parsing layers
        for layer_idx in range(spadb.GetLayerCount()):
            # dictionary where will be stored informations
            dico_layer = OrderedDict()
            # parent GDB
            dico_layer['gdb_name'] = path.basename(spadb.GetName())
            # getting layer object
            layer = spadb.GetLayerByIndex(layer_idx)
            # layer name
            li_layers_names.append(layer.GetName())
            # layer index
            li_layers_idx.append(layer_idx)
            # getting layer globlal informations
            self.infos_basics(layer, dico_layer, txt)
            # storing layer into the GDB dictionary
            dico_spadb['{0}_{1}'.format(layer_idx,
                                        dico_layer.get('title'))] = dico_layer
            # summing fields number
            total_fields += dico_layer.get(u'num_fields')
            # summing objects number
            total_objs += dico_layer.get(u'num_obj')
            # deleting dictionary to ensure having cleared space
            del dico_layer
        # storing fileds and objects sum
        dico_spadb['total_fields'] = total_fields
        dico_spadb['total_objs'] = total_objs

        # warnings messages
        dico_spadb['err_gdal'] = ogrerr.err_type, ogrerr.err_msg

    def infos_basics(self, layer_obj, dico_layer, txt):
        u"""Get the global informations about the layer."""
        # title
        try:
            dico_layer[u'title'] = unicode(layer_obj.GetName())
        except UnicodeDecodeError:
            layerName = layer_obj.GetName().decode('latin1', errors='replace')
            dico_layer[u'title'] = layerName

        # features count
        dico_layer[u'num_obj'] = layer_obj.GetFeatureCount()

        if layer_obj.GetFeatureCount() == 0:
            u""" if layer doesn't have any object, return an error """
            dico_layer[u'error'] = u'err_nobjet'
            self.alert = self.alert + 1
        else:
            # getting geography and geometry informations
            srs = layer_obj.GetSpatialRef()
            self.infos_geos(layer_obj, srs, dico_layer, txt)

        # getting fields informations
        dico_fields = OrderedDict()
        layer_def = layer_obj.GetLayerDefn()
        dico_layer['num_fields'] = layer_def.GetFieldCount()
        self.infos_fields(layer_def, dico_fields)
        dico_layer['fields'] = dico_fields

        # end of function
        return dico_layer

    def infos_geos(self, layer_obj, srs, dico_layer, txt):
        u"""Get the informations about geography and geometry."""
        # SRS
        srs.AutoIdentifyEPSG()
        # srs type
        srsmetod = [(srs.IsCompound(), txt.get('srs_comp')),
                    (srs.IsGeocentric(), txt.get('srs_geoc')),
                    (srs.IsGeographic(), txt.get('srs_geog')),
                    (srs.IsLocal(), txt.get('srs_loca')),
                    (srs.IsProjected(), txt.get('srs_proj')),
                    (srs.IsVertical(), txt.get('srs_vert'))]
        # searching for a match with one of srs types
        for srsmet in srsmetod:
            if srsmet[0] == 1:
                typsrs = srsmet[1]
            else:
                continue
        # in case of not match
        try:
            dico_layer[u'srs_type'] = unicode(typsrs)
        except UnboundLocalError:
            typsrs = txt.get('srs_nr')
            dico_layer[u'srs_type'] = unicode(typsrs)

        # handling exceptions in srs names'encoding
        try:
            if srs.GetAttrValue(str('PROJCS')) != 'unnamed':
                dico_layer[u'srs'] = unicode(srs.GetAttrValue(str('PROJCS'))).replace('_', ' ')
            else:
                dico_layer[u'srs'] = unicode(srs.GetAttrValue(str('PROJECTION'))).replace('_', ' ')
        except UnicodeDecodeError:
            if srs.GetAttrValue(str('PROJCS')) != 'unnamed':
                dico_layer[u'srs'] = srs.GetAttrValue(str('PROJCS')).decode('latin1').replace('_', ' ')
            else:
                dico_layer[u'srs'] = srs.GetAttrValue(str('PROJECTION')).decode('latin1').replace('_', ' ')
        finally:
            dico_layer[u'EPSG'] = unicode(srs.GetAttrValue(str("AUTHORITY"), 1))

        # World SRS default
        if dico_layer[u'EPSG'] == u'4326' and dico_layer[u'srs'] == u'None':
            dico_layer[u'srs'] = u'WGS 84'
        else:
            pass

        # first feature and geometry type
        try:
            first_obj = layer_obj.GetNextFeature()
            geom = first_obj.GetGeometryRef()
        except AttributeError as e:
            print(e, layer_obj.GetName(), layer_obj.GetFeatureCount())
            first_obj = layer_obj.GetNextFeature()
            geom = first_obj.GetGeometryRef()

        # geometry type human readable
        if geom.GetGeometryName() == u'POINT':
            dico_layer[u'type_geom'] = txt.get('geom_point')
        elif u'LINESTRING' in geom.GetGeometryName():
            dico_layer[u'type_geom'] = txt.get('geom_ligne')
        elif u'POLYGON' in geom.GetGeometryName():
            dico_layer[u'type_geom'] = txt.get('geom_polyg')
        else:
            dico_layer[u'type_geom'] = geom.GetGeometryName()

        # spatial extent (bounding box)
        dico_layer[u'Xmin'] = round(layer_obj.GetExtent()[0], 2)
        dico_layer[u'Xmax'] = round(layer_obj.GetExtent()[1], 2)
        dico_layer[u'Ymin'] = round(layer_obj.GetExtent()[2], 2)
        dico_layer[u'Ymax'] = round(layer_obj.GetExtent()[3], 2)

        # end of function
        return dico_layer

    def infos_fields(self, layer_def, dico_fields):
        u"""Get the informations about fields definitions."""
        for i in range(layer_def.GetFieldCount()):
            champomy = layer_def.GetFieldDefn(i)  # fields ordered
            dico_fields[champomy.GetName()] = champomy.GetTypeName(),\
                                              champomy.GetWidth(),\
                                              champomy.GetPrecision()
        # end of function
        return dico_fields

    def sizeof(self, os_size):
        u"""Return size in different units depending on size.

        see http://stackoverflow.com/a/1094933
        """
        for size_cat in ['octets', 'Ko', 'Mo', 'Go']:
            if os_size < 1024.0:
                return "%3.1f %s" % (os_size, size_cat)
            os_size /= 1024.0
        return "%3.1f %s" % (os_size, " To")

    def erratum(self, dico_spadb, spadbpath, mess):
        """Errors handler."""
        # local variables
        dico_spadb[u'name'] = path.basename(spadbpath)
        dico_spadb[u'folder'] = path.dirname(spadbpath)
        try:
            def_couche = self.layer.GetLayerDefn()
            dico_spadb[u'num_fields'] = def_couche.GetFieldCount()
        except AttributeError:
            mess = mess
        finally:
            dico_spadb[u'error'] = mess
            dico_spadb[u'layers_count'] = 0
        # End of function
        return dico_spadb

# ###########################################################################
# #### Stand alone program ########
# #################################

if __name__ == '__main__':
    u"""
    standalone execution for tests. Paths are relative considering a test
    within the official repository (https://github.com/Guts/DicoGIS)
    """
    from os import chdir
    # sample files
    chdir(r'..\..\test\datatest\FileGDB')
    # test text dictionary
    textos = OrderedDict()
    textos['srs_comp'] = u'Compound'
    textos['srs_geoc'] = u'Geocentric'
    textos['srs_geog'] = u'Geographic'
    textos['srs_loca'] = u'Local'
    textos['srs_proj'] = u'Projected'
    textos['srs_vert'] = u'Vertical'
    textos['geom_point'] = u'Point'
    textos['geom_ligne'] = u'Line'
    textos['geom_polyg'] = u'Polygon'

    # listing samples Spatialite DB
    li_spadb = [
                r'Spatialite_Test.sqlite'
               ]

    # recipient datas
    dico_spadb = OrderedDict()

    # read GDB
    for spadbpath in li_spadb:
        dico_spadb.clear()
        if path.isfile(spadbpath):
            print("\n{0}: ".format(spadbpath))
            ReadSpaDB(spadbpath,
                      dico_spadb,
                      'Spatialite DB',
                      textos)
            # print results
            print(dico_spadb)
        else:
            pass
