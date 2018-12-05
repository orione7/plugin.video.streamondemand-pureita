# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para documoo
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# by dentaku65, DrZ3r0
# ------------------------------------------------------------
import urlparse, urllib2, urllib, re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "documoo"
__category__ = "F,D"
__type__ = "generic"
__title__ = "documoo (IT)"
__language__ = "IT"

sito = "http://documoo.tv/"

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.documoo mainlist")
    itemlist = [#Item(channel=__channel__,
                     #title="[COLOR azure]Documentari random[/COLOR]",
                     #action="random",
                     #url=sito,
                     #thumbnail="http://dc584.4shared.com/img/XImgcB94/s7/13feaf0b538/saquinho_de_pipoca_01"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie[/COLOR]",
                     action="categorias",
                     url=sito,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def peliculas(item):
    logger.info("streamondemand.documoo peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="thumb">\s*'
    patron += '<a href="(.*?)"[^t]+title="(.*?)">\s*'
    patron += '<img[^s]+src="(.*?)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        #scrapedthumbnail = ""
        #response = urllib2.urlopen(scrapedurl)
        #html = response.read()
        #start = html.find('<meta property="og:type" content="article" />')
        #end = html.find('<meta property="og:site_name" content="Documoo" />', start)
        #scrapedplot = html[start:end]
        #scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        #scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 viewmode="movie_with_plot",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = '</span><a href=\'(.*?)\' class="inactive">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Avanti >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def random(item):
    logger.info("streamondemand.documoo peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<a href="(.*?)" rel="bookmark" title="(.*?)"><img[^s]+src="(.*?)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        #scrapedthumbnail = ""
        #response = urllib2.urlopen(scrapedurl)
        #html = response.read()
        #start = html.find("<li itemprop=\"description\">")
        #end = html.find("<ul id=\"tab-contact\" class=\"hide\">", start)
        #scrapedplot = html[start:end]
        #scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        #scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 url=scrapedurl,
                 viewmode="movie_with_plot",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist


def categorias(item):
    logger.info("streamondemand.documoo categorias")
    itemlist = []

    data = scrapertools.cache_page(item.url)
    logger.info(data)

    # Narrow search by selecting only the combo
    start = data.find('<ul class="sub-menu sub-menu-2">')
    end = data.find('<li id="menu-item-18011"', start)
    bloque = data[start:end]

    # The categories are the options for the combo  
    patron = '<li[^>]+><a href="(.*?)"><span[^>]+>(.*?)</span></a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for url, titulo in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(titulo)
        scrapedurl = urlparse.urljoin(item.url, url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot))

    return itemlist


def search(item, texto):
    logger.info("[documoo.py] " + item.url + " search " + texto)
    item.url = "http://www.documoo.tv/?s="+texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def play(item):
    logger.info("[documoo.py] play")
    itemlist = []
    video_url = ""
    server = None

    data = scrapertools.cache_page(item.url)
    url = scrapertools.find_single_match(data, '<iframe\s+(?:width="[^"]*"\s*height="[^"]*"\s*)?src="([^"]+)"')

    if 'youtu' in url:
        data = scrapertools.cache_page(url)
        vid = scrapertools.find_single_match(data, '\'VIDEO_ID\'\s*:\s*"([^"]+)')
        if vid != "":
            video_url = "http://www.youtube.com/watch?v=%s" % vid
            server = 'youtube'
    elif 'rai.tv' in url:
        data = scrapertools.cache_page(url)
        video_url = scrapertools.find_single_match(data, '<meta\s+name="videourl_m3u8"\s*content="([^"]+)"')

    if video_url != "":
        item.url = video_url
        item.server = server
        itemlist.append(item)

    return itemlist
