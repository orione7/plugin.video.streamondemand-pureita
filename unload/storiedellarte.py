# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para storiedellarte
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "storiedellarte"
__category__ = "D"
__type__ = "generic"
__title__ = "storiedellarte (IT)"
__language__ = "IT"


DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.storiedellarte mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="[COLOR azure]Video Art[/COLOR]", action="peliculas", url="http://storiedellarte.com/category/video", thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"))

    
    return itemlist

def peliculas(item):
    logger.info("streamondemand.storiedellarte peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron  = '<article class="[^>]+>\s*'
    patron  += '<a href="(.*?)"[^>]+><img src="(.*?)"[^>]+>[^>]+>[^>]+>\s*'
    patron  += '<h2[^>]+>[^>]+>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle)
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle.replace("Video: ",""))
        response = urllib2.urlopen(scrapedurl)
        html = response.read()
        start = html.find("<div class=\"pf-content\">")
        end = html.find("</div>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        #scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle, url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    # Extrae el paginador
    patronvideos  = 'a class="next page-numbers" href="(.*?)">Next &rarr;'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="[COLOR orange]Avanti >>[/COLOR]" , url=scrapedurl , folder=True) )

    return itemlist

