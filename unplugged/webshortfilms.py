# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para webshortfilms
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "webshortfilms"
__category__ = "F"
__type__ = "generic"
__title__ = "webshortfilms (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "https://webshortfilms.wordpress.com"


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.webshortfilms mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Best Streaming Shortfilms[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png")]

    return itemlist


def peliculas(item):
    logger.info("streamondemand.webshortfilms peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<h1 class="entry-title"><a href="([^"]+)"[^>]+>(.*?)<.*?<img.*?src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
#        html = scrapertools.cache_page(scrapedurl)
#        start = html.find("</iframe></span>")
#        end = html.find("</a></p>", start)
#        scrapedplot = html[start:end]
#        scrapedplot = re.sub(r'<.*?>', '', scrapedplot)
#        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
#        scrapedthumbnail = ""
        if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     title=scrapedtitle,
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     folder=True))

    # Extrae el paginador
    patronvideos = '<div class="nav-previous"><a href="([^"]+)" ><span class="meta-nav">&larr;'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist

def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

