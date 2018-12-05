# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para animesubita
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import sys

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "animesubita"
__category__ = "A"
__type__ = "generic"
__title__ = "animesubita"
__language__ = "IT"

host = "http://www.animesubita.info/"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'],
    ['Accept-Encoding', 'gzip, deflate']
]


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.animesubita mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Anime - Novita'[/COLOR]",
                     action="novedades",
                     url=host,
                     thumbnail="http://repository-butchabay.googlecode.com/svn/branches/eden/skin.cirrus.extended.v2/extras/moviegenres/Anime.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime - Per Genere[/COLOR]",
                     action="genere",
                     url=host + "cerca-per-genere/",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie concluse[/COLOR]",
                     action="concluse",
                     url=host + "serie-concluse/",
                     thumbnail="http://i60.tinypic.com/i6xe1g.jpg"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime - Lista A-Z[/COLOR]",
                     action="categorias",
                     url=host + "lista-anime-streaming/",
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/A-Z.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Anime...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def novedades(item):
    logger.info("streamondemand.animesubita peliculas")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<div class="video-item">.*?<div class="item-thumbnail">.*?<a href="([^"]+)" title="([^"]+)"><img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(
                Item(channel=__channel__,
                     action="findvid",
                     title=scrapedtitle,
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     viewmode="movie_with_plot"))

    return itemlist


def categorias(item):
    logger.info("streamondemand.animesubita categorias")

    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)

    # The categories are the options for the combo
    patron = '<li><a title="([^"]+)" href="([^"]+)">.*?</a> <span class="mctagmap_count">.*?</span></li>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="episodios",
                     title=scrapedtitle,
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     url=scrapedurl))

    return itemlist


def concluse(item):
    logger.info("streamondemand.animesubita categorias")

    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)

    # The categories are the options for the combo
    patron = '<li class="jcl_category "><a href="([^"]+)">([^"]+)</a></li>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="episodios",
                     title=scrapedtitle,
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     url=scrapedurl))

    return itemlist


def genere(item):
    logger.info("streamondemand.animesubita categorias")

    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)

    # The categories are the options for the combo
    patron = '<li><a title="([^"]+)" href="([^"]+)">.*?</a></li>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
                Item(channel=__channel__,
                     action="generedisplay",
                     title=scrapedtitle,
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     url=scrapedurl))

    return itemlist


def generedisplay(item):
    logger.info("streamondemand.animesubita categorias")

    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)

    # The categories are the options for the combo
    patron = '<a href="([^"]+)"> <img src="([^"]+)" alt="([^"]+)" title=".*?">'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
                Item(channel=__channel__,
                     action="episodios",
                     title=scrapedtitle,
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail))

    return itemlist


def selection(item):
    logger.info("streamondemand.animesubita peliculas")

    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<div class="item-head">.*?<h3><a href="([^"]+)".*?rel=.*?title="([^"]+)">.*?</h3>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="episodios2",
                     title=scrapedtitle,
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     url=scrapedurl))

    return itemlist


def episodios2(item):
    logger.info("streamondemand.animesubita peliculas")

    itemlist = []

    # Descarga la pagina
    headers.append(['Referer', item.url])

    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<div class="item-head">\s*<h3><a href="([^"]+)".*?>([^"]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="findvid",
                     title=scrapedtitle,
                     fulltitle=item.fulltitle,
                     show=item.show,
                     url=scrapedurl))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
                Item(channel=__channel__,
                     title=item.title,
                     url=item.url,
                     action="add_serie_to_library",
                     extra="episodios",
                     show=item.show))

    return itemlist


def episodios(item):
    logger.info("streamondemand.animesubita episodios")

    itemlist = []

    # Descarga la pagina
    headers.append(['Referer', item.url])

    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)"> <img src="([^"]+)" alt="([^"]+)".*?'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="findvid",
                     title=scrapedtitle,
                     fulltitle=item.fulltitle,
                     show=item.show,
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
                Item(channel=__channel__,
                     title=item.title,
                     url=item.url,
                     action="add_serie_to_library",
                     extra="episodios",
                     show=item.show))

    return itemlist


def search(item, texto):
    logger.info("[animesubita.py] " + item.url + " search " + texto)

    item.url = host + "?s=" + texto

    try:
        return selection(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def findvid(item):
    logger.info("streamondemand.channels.animesubita findvideos")

    headers.append(['Referer', item.url])

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    patron = 'return\s*gnarty_player\((\d+)\);'
    matches = re.compile(patron, re.DOTALL).findall(data)
    url = host + 'wp-admin/admin-ajax.php'
    html = []
    for vid in matches:
        html.append(scrapertools.cache_page(url, post='action=loadPlayer&id=' + vid, headers=headers))

    html = ''.join(html)

    itemlist = servertools.find_video_items(data=html)

    if len(itemlist) == 0:
        itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
