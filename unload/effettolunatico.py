# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para effettolunatico
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import sys
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "effettolunatico"
__category__ = "F"
__type__ = "generic"
__title__ = "Effetto Lunatico"
__language__ = "IT"

host = "http://effettolunatico.altervista.org"

headers = [
    ['Host', 'effettolunatico.altervista.org'],
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', 'http://effettolunatico.altervista.org/forum/forum.php'],
    ['Connection', 'keep-alive'],
    ['Upgrade-Insecure-Requests', '1'],
    ['Cache-Control', 'max-age=0']
]

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.effettolunatico mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url="%s/forum/vbtube.php?do=cat&id=2&o=0&page=0" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__, 
                     title="[COLOR yellow]Cerca...[/COLOR]", 
                     action="search", 
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def search(item, texto):
    logger.info("[effettolunatico.py] " + item.url + " search " + texto)
    item.url = host + "/forum/vbtube.php?do=search&startid=0&mstr=" + texto + "&securitytoken=guest"
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def peliculas(item):
    logger.info("streamondemand.effettolunatico peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<td[^>]+><a href="([^"]+)"><img src="([^"]+)"[^>]+>[^>]+>[^>]+>\s*[^>]+>[^>]+>\s*[^>]+>[^>]+><b>(.*?)</b>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.replace("]...", "]"))
        html = scrapertools.cache_page(scrapedurl, headers=headers)
        start = html.find("Trama del film")
        end = html.find("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=ISO-8859-1\" />", start)
        scrapedplot = re.sub(r'<[^>]*>', '', html[start:end])
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
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

    # Extrae el paginador
    patronvideos = '<span class="prev_next"><a rel="next" href="([^"]+)" title="Pagina successiva[^>]+>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        scrapedurl = scrapedurl.replace(" ", "%20").replace("&amp;", "&")
        scrapedurl = scrapertools.decodeHtmlentities(scrapedurl)
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo>>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist
