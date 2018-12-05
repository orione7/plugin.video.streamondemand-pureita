# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para walkingdeadstreamingita.altervista.org
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "walkingdeadita"
__category__ = "S"
__type__ = "generic"
__title__ = "TheWalkingDeadITA Streaming"
__language__ = "IT"

host = "http://walkingdeadstreamingita.altervista.org/"

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("[walkingdeadita.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(host)

    patronvideos = '<li><a href="([^"]+)"><span class="catTitle">([^<]+)<\/span>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)
    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = host + match.group(1)
        
        if 'Stagione 1' in scrapedtitle:
            thumbnail="http://www.impawards.com/tv/posters/walking_dead_ver4_xlg.jpg"
        if 'Stagione 2' in scrapedtitle:
            thumbnail="http://ecx.images-amazon.com/images/I/91XpP2iw6qL._SL1500_.jpg"
        if 'Stagione 3' in scrapedtitle:
            thumbnail="http://ecx.images-amazon.com/images/I/81OLwBqWEiL._SL1500_.jpg"
        if 'Stagione 4' in scrapedtitle:
            thumbnail="http://www.destroythebrain.com/wp-content/uploads/2014/06/af61610ORN-walking-dead-S4-sd-ocard1.jpg"
        if 'Stagione 5' in scrapedtitle:
            thumbnail="http://www.tribute.ca/tribute_objects/images/movies/The_Walking_Dead_Season_5/TheWalkingDeadSeason5.jpg"
        if 'Stagione 6' in scrapedtitle:
            thumbnail="http://www.avoir-alire.com/IMG/arton30744.jpg?1436604230"
        if 'Webisodes 1' in scrapedtitle:
            thumbnail="http://cdn.movieweb.com/img.albums/TVqoB6yqvgC1tv_1_600.jpg"
        if 'Webisodes 2' in scrapedtitle:
            thumbnail="http://cdn.movieweb.com/img.albums/TVqoB6yqvgC1tv_1_600.jpg"
        if 'Webisodes 3' in scrapedtitle:
            thumbnail="http://cdn.movieweb.com/img.albums/TVqoB6yqvgC1tv_1_600.jpg"
            
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")

        # Añade al listado de XBMC
        itemlist.append(
            Item(channel=__channel__,
                 action="listepisodes",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=thumbnail,
                 fanart="http://images2.alphacoders.com/240/240942.jpg"))

    return itemlist


def listepisodes(item):
    logger.info("[walkingdeadita.py] episodeslist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patronvideos = '<h3 class="catItemTitle">\s*<a href="([^"]+)">([^<]+)<\/a>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(2)).strip()
        scrapedurl = host + match.group(1)
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")

        # Añade al listado de XBMC
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://i.imgur.com/irAU6Mr.png?1",
                 fanart="http://images2.alphacoders.com/240/240942.jpg"))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title= "[COLOR azure]Aggiungi [/COLOR]" + item.title + "[COLOR azure] alla libreria di Kodi[/COLOR]",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="listepisodes",
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="[COLOR azure]Scarica tutti gli episodi della serie[/COLOR]",
                 url=item.url,
                 action="download_all_episodes",
                 extra="listepisodes",
                 show=item.show))

    return itemlist
