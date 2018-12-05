# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para bibliotrailer
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "bibliotrailer"
__category__ = "D"
__type__ = "generic"
__title__ = "bibliotrailer (IT)"
__language__ = "IT"


DEBUG = config.get_setting("debug")

sito="http://www.bibliotrailer.it"


def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.bibliotrailer mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Libri in Videoclip - Trailer[/COLOR]", action="peliculas", url="http://www.bibliotrailer.it/search/label/Booktrailer?max-results=8", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Film tratti da libri - Trailer[/COLOR]", action="peliculas", url="http://www.bibliotrailer.it/search/label/Movie%20Trailer?max-results=8", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Videorecensioni Libri[/COLOR]", action="peliculas", url="http://www.bibliotrailer.it/search/label/Videorecensioni?max-results=8", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Videointerviste Autori[/COLOR]", action="peliculas", url="http://www.bibliotrailer.it/search/label/Videointerviste?max-results=8", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Videoconsigli imparare a scrivere[/COLOR]", action="peliculas", url="http://www.bibliotrailer.it/search/label/Videoconsigli?max-results=8", thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"))

    
    return itemlist

def peliculas(item):
    logger.info("streamondemand.bibliotrailer peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<div class=\'post-thumb\'>\s*'
    patron  += '<a href=\'(.*?)\' style=[^:]+:url\((.*?)\)[^>]+>[^>]+>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail in matches:
        scrapedtitle = scrapedurl
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("http://www.bibliotrailer.it/",""))
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("/",": "))
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("-"," "))
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace(".html",""))
        scrapedplot = scrapedtitle
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = '<a href="\'\+f(.*?)\+\'">\'\+pageNaviConf.nextText\+'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]" , url=sito+scrapedurl , folder=True) )

    return itemlist

