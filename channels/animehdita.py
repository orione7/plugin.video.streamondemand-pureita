<<<<<<< HEAD
=======
# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-PureITA / XBMC Plugin
# Canale  animehdita
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import config, httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "animehdita"
host        = "http://www.animehdita.org/"
headers     = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita.animehdita mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Anime[COLOR orange] - Novità[/COLOR]",
                     action="lista_novita",
                     url=(host),
                     thumbnail=thumbnail_anime,
                     fanart=thumbnail_fanart),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime[COLOR orange] -  Complete[/COLOR]",
                     action="lista_completa",
                     url=("%s/category/anime/anime-conclusi/" % host),
                     thumbnail=thumbnail_anime,
                     fanart=thumbnail_fanart),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime[COLOR orange] - Lista[/COLOR]",
                     action="lista_novita",
                     url=("%s/category/anime/" % host),
                     thumbnail=thumbnail_anime_lista,
                     fanart=thumbnail_fanart),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra='serie',
                     thumbnail=thumbnail_cerca)]
    return itemlist
	
# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("streamondemand-pureita.animehdita search " + texto)
	
    item.url = host + "/?s=" + texto

    try:
        return peliculas_search(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
	
# ==============================================================================================================================================================================

def peliculas_search(item):
    logger.info("streamondemand-pureita.animehdita lista_serie")
    itemlist = []

    data = httptools.downloadpage(item.url).data									 
    patron = '<\/div><a href="([^"]+)"><img width="\d+"\s*height="\d+"\s*'
    patron += 'src="([^"]+)"\s*class="[^"]+"\s*alt=""\s*title="([^"]+)"\s*\/><\/a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(Item(channel=__channel__,
                                     action="episodios",
                                     title=scrapedtitle,
                                     fulltitle=scrapedtitle,
                                     url=scrapedurl,
                                     thumbnail=scrapedthumbnail,
                                     fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                                     show=scrapedtitle,
                                     folder=True),tipo='tv'))
									 
    patron = '<link rel="next" href="([^"]+)" />'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_search",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail=thumbnail_successivo))

    return itemlist
	
# ==============================================================================================================================================================================

def lista_novita(item):
    logger.info("streamondemand-pureita.animehdita lista_novita")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    blocco = scrapertools.find_single_match(data, '<link rel="canonical" href="[^>]+" (.*?)</div></div></div></div></div></div></div>')
    patron = '<a href="([^"]+)"><img[^>]+src="([^"]+)" class="[^>]+title=".*?" \/>'
    patron += '<\/a><h3><a href="[^"]+">([^"]+)<span class="loop-subtitle">.*?<\/span><\/a><\/h3>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        scrapetitle = re.sub(r"([0-9-(-)])", r"", scrapedtitle).replace(" Ep ", "")
        itemlist.append(infoSod(Item(channel=__channel__,
                                     action="episodios",
                                     title=scrapedtitle,
                                     fulltitle=scrapetitle,
                                     url=scrapedurl,
                                     thumbnail=scrapedthumbnail,
                                     fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                                     show=item.fulltitle,
                                     folder=True),tipo='tv'))
								 
    patron = '<link rel="next" href="([^"]+)" />'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_novita",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail=thumbnail_successivo))

    return itemlist

# ==============================================================================================================================================================================

def lista_completa(item):
    logger.info("streamondemand-pureita.animehdita lista_novita")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    blocco = scrapertools.find_single_match(data, '<link rel="canonical" href="[^>]+" (.*?)</div></div></div></div></div></div></div>')
    patron = '<a href="([^"]+)"><img[^>]+src="([^"]+)" class="[^>]+title=".*?" \/>'
    patron += '<\/a><h3><a href="[^"]+">([^"]+)<span class="loop-subtitle">.*?<\/span><\/a><\/h3>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(Item(channel=__channel__,
                                     action="episodios",
                                     title=scrapedtitle,
                                     fulltitle=scrapedtitle,
                                     url=scrapedurl,
                                     thumbnail=scrapedthumbnail,
                                     fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                                     show=item.fulltitle,
                                     folder=True),tipo='tv'))
								 
    patron = '<link rel="next" href="([^"]+)" />'
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_novita",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail=thumbnail_successivo))

    return itemlist

# ==============================================================================================================================================================================

def episodios(item):
    logger.info("streamondemand-pureita.animehdita episodios")
    itemlist = []
			 
    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, '<p><b>TRAMA</b>(.*?)</div></div>')

    patron = '<tr>(.*?)<\/a>\s*<\/td>\s*<\/tr>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for puntata in matches:
        scrapedtitle=scrapertools.find_single_match(puntata, '<td class="td-numero">([^<]+)')
        if not "Episodio" in scrapedtitle:
           scrapedtitle=scrapertools.find_single_match(puntata, '<a target="_blank" href="[^"]+">([^<]+)')
        if "Streamango HD" in scrapedtitle:
           scrapedtitle=scrapertools.find_single_match(puntata, '<td class="td-link">(.*?): ')
        #if scrapedtitle=="":
           #scrapedtitle=scrapertools.find_single_match(puntata, '<td class="td-link"><a target="_blank" href="[^>]+">([^<]+)')
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios_all",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=puntata,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                 folder=True))
		 
    return itemlist

"""
    patron = '([^<]+)<a target="_blank" href="([^"]+)">Streamango HD</a>'
    data = httptools.downloadpage(item.url, headers=headers).data

    blocco = scrapertools.find_single_match(data, '<p><b>TRAMA</b>:<br />(.*?)</div></div>')
    patron='([^<]+)<a target="_blank" href="([^"]+)">Streamango HD</a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for scrapedtitle, scrapedurl in matches:
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(Item(channel=__channel__,
                                     action="findvideos",
                                     title=scrapedtitle,
                                     fulltitle=scrapedtitle,
                                     url=scrapedurl,
                                     fanart=item.fanart if item.fanart != "" else item.scrapedthumbnail,
                                     show=item.fulltitle,
                                     folder=True),tipo='tv'))	"""
# ==============================================================================================================================================================================

def episodios_all(item):
    logger.info("streamondemand-pureita animehdita episodios_all")
    itemlist = []

    patron = 'href="([^"]+)">([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(item.url)
	

    for scrapedurl,scrapedserver in matches:
        #logger.debug(scrapedurl)
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.scrapedtitle,
                 show=item.scrapedtitle,
                 title="[COLOR blue]" + item.title + " [/COLOR][COLOR orange]" + scrapedserver + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    return itemlist
	
# ==============================================================================================================================================================================

def play(item):
    itemlist=[]

    data = httptools.downloadpage(item.url, headers=headers).data
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    logger.debug(data)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
	
# ==============================================================================================================================================================================

thumbnail_fanart="https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
thumbnail_anime_az= "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/return_home_P.png"
thumbnail_anime_genre="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_genre_P.png"
thumbnail_animation="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation_P.png"
thumbnail_anime_lista="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_lista_P.png"
thumbnail_anime="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_P.png"
thumbnail_cerca="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"
thumbnail_successivo="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"
>>>>>>> 936c940443d66985bf10575e38517a4816c6c709
