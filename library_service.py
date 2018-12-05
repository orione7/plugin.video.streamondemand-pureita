# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand-pureita by Pelisalacarta
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of streamondemand-pureita by Pelisalacarta.
#
# streamondemand-pureita by Pelisalacarta is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand-pureita by Pelisalacarta is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand-pureita by Pelisalacarta.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------
# Service for updating new episodes on library series
#------------------------------------------------------------

# -- Update channels from repository streamondemand-PureITA Alfa------
try:
    from core import update_channels
except:
    logger.info("streamondemand-pureita.library_service Error in update_channels")
# ----------------------------------------------------------------------

# -- Update servertools and servers from repository streamondemand-PureITA Alfa------
try:
    from core import update_servers
except:
    logger.info("streamondemand-pureita.library_service Error en update_servers")
# ----------------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os
import sys
import xbmc,time

from core import scrapertools
from core import config
from core import logger
from core.item import Item
from servers import servertools

logger.info("streamondemand-pureita.library_service Actualizando series...")
from platformcode import library
from platformcode import launcher
import xbmcgui
import imp

directorio = os.path.join(config.get_library_path(),"SERIES")
logger.info ("directorio="+directorio)

if not os.path.exists(directorio):
    os.mkdir(directorio)

nombre_fichero_config_canal = os.path.join( config.get_library_path() , "series.xml" )
if not os.path.exists(nombre_fichero_config_canal):
    nombre_fichero_config_canal = os.path.join( config.get_data_path() , "series.xml" )

try:

    if config.get_setting("updatelibrary")=="true":
        config_canal = open( nombre_fichero_config_canal , "r" )
        
        for serie in config_canal.readlines():
            logger.info("streamondemand-pureita.library_service serie="+serie)
            serie = serie.split(",")
        
            ruta = os.path.join( config.get_library_path() , "SERIES" , serie[0] )
            logger.info("streamondemand-pureita.library_service ruta =#"+ruta+"#")
            if os.path.exists( ruta ):
                logger.info("streamondemand-pureita.library_service Actualizando "+serie[0])
                item = Item(url=serie[1], show=serie[0])
                try:
                    itemlist = []

                    pathchannels = os.path.join(config.get_runtime_path() , 'channels' ,serie[2].strip() + '.py')
                    logger.info("streamondemand-pureita.library_service Cargando canal  " + pathchannels + " " + serie[2].strip())
                    obj = imp.load_source(serie[2].strip(), pathchannels )
                    itemlist = obj.episodios(item)

                except:
                    import traceback
                    logger.error(traceback.format_exc())
                    itemlist = []
            else:
                logger.info("streamondemand-pureita.library_service No actualiza "+serie[0]+" (no existe el directorio)")
                itemlist=[]

            for item in itemlist:
                #logger.info("item="+item.tostring())
                try:
                    item.show=serie[0].strip()
                    library.savelibrary( titulo=item.title , url=item.url , thumbnail=item.thumbnail , server=item.server , plot=item.plot , canal=item.channel , category="Series" , Serie=item.show , verbose=False, accion="play_from_library", pedirnombre=False, subtitle=item.subtitle )
                except:
                    logger.info("streamondemand-pureita.library_service Capitulo no valido")

        import xbmc
        xbmc.executebuiltin('UpdateLibrary(video)')
    else:
        logger.info("No actualiza la biblioteca, está desactivado en la configuración de streamondemand-pureita")

except:
    logger.info("streamondemand-pureita.library_service No hay series para actualizar")
