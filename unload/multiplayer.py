# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para multiplayer
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "multiplayer"
__category__ = "D"
__type__ = "generic"
__title__ = "multiplayer (IT)"
__language__ = "IT"


DEBUG = config.get_setting("debug")

sito="http://multiplayer.it"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', 'http://www.multiplayer.it/'],
    ['Connection', 'keep-alive']
]

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.multiplayer mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Recensioni Videogame[/COLOR]", action="peliculas", url="http://multiplayer.it/video/videorecensione/", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))

    
    return itemlist

def peliculas(item):
    logger.info("streamondemand.multiplayer peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron  = '<div class="video_thumb_wrapper">\s*'
    patron  += '<a href="(.*?)"[^>]+>\s*'
    patron  += '<img src="(.*?)" alt="(.*?)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("Video di ",""))
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle, url=sito+scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<li><a href="(.*?)" rel="pagina" class="page_link"><span class="next">&nbsp</span></a></li>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]" , url=sito+scrapedurl , folder=True) )

    return itemlist

