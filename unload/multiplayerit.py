# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para multiplayerit
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[multiplayerit.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    # URL del vídeo
    for url in re.findall(r'file: "(.*?\.mp4)"', data):
        video_urls.append([".mp4" + " [multiplayerit]", url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://multiplayer.it/video/embed/UIZ/
    patronvideos  = '(http://multiplayer.it/video/embed/[0-9a-zA-Z/]+)'
    logger.info("[multiplayerit.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[multiplayerit]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'multiplayerit' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
    patronvideos = r'.netaddiction.it/embed/([a-zA-Z0-9_-]+)'
    logger.info("[netaddiction.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[netaddiction]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'netaddiction' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)


    return devuelve
