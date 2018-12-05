# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Canal para streamtime
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import re
import sys
import urlparse
import urllib2
import urllib

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "streamtime"
__category__ = "F"
__type__ = "generic"
__title__ = "streamtime"
__language__ = "IT"

host = "http://streamtime.altervista.org/"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'],
    ['Accept', 'application/json, text/javascript, */*; q=0.01'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Host', 'streamtime.altervista.org'],
    ['Referer', host],
    ['Connection', 'keep-alive'],
    ['X-Requested-With', 'XMLHttpRequest']
]


DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.streamtime mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist

def search(item, texto):
    logger.info("[streamtime.py] " + item.url + " search " + texto)
    item.url = host + "/search.php?name=" + texto + "&type=film"
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def peliculas(item):
    logger.info("streamondemand.streamtime peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<a id="single-item" href="(.*?)" value="(.*?)" type="film">\s*<img title="(.*?)" src="(.*?)">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedid, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedurl = scrapedurl.replace(scrapedurl, "http://streamtime.altervista.org/get_links.php?type=film&id="+scrapedid)
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

