<<<<<<< HEAD
=======
# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale  videotecaproject
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "videotecaproject"
host = "https://www.videotecaproject.net"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita.videotecaproject mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Menu' >>>[/COLOR]",
                     action="submenu_serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Ultimi Episodi[/COLOR]",
                     action="pelis_new",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Ultimi Episodi ([COLOR azure]Per Data[/COLOR])",
                     action="peliculas_new",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas_tv",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - In corso[/COLOR]",
                     action="peliculas_tvshow",
                     url="%s/tags/Serie In Corso/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Concluse[/COLOR]",
                     action="peliculas_tvshow",
                     url="%s/tags/Serie Terminate/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow][I]Cerca Serie TV...[/I][/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist
		
# =============================================================================================================================================
# TILL 
# =============================================================================================================================================

def submenu_serie(item):
    logger.info("streamondemand-pureita.videotecaproject menu_serie")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Ultimi Episodi ([COLOR azure]Per Data[/COLOR])",
                     action="peliculas_new",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas_tv",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),				 
	            Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange]- Genere[/COLOR]",
                     action="categorias_serie",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange]- Lista A/Z[/COLOR]",
                     action="categorias_az",
                     url=host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange]- HD[/COLOR]",
                     action="peliculas_tvshow",
                     url="%s/tags/Serie HD/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/blueray_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV [COLOR orange]- In Corso[/COLOR]",
                     action="peliculas_tvshow",
                     url="%s/tags/Serie In Corso/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist
	
# =============================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita videotecaproject] " + item.url + " search " + texto)
    item.url = host + "/search/?text=" + texto

    try:
        if item.extra == "movie":
            return peliculas_srcmovie(item)
        else:
            return peliculas_srcserie(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# =============================================================================================================================================

def peliculas_srcserie(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_srcserie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("<strong>", "").replace("</strong>", "")
        scrapetitle = scrapedtitle.replace(" ITA", "")
        if scrapedtitle=="Serie Tv":
          continue
        if "a-b" in scrapedurl or "-e-f" in scrapedurl or "-i-j" in scrapedurl:
          continue
        if "-m-n" in scrapedurl or "-q-r" in scrapedurl or "-w-x" in scrapedurl:
          continue
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapetitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapetitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo="tv"))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima[^"]+" rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(host, matches[0])
        scrapedurl=scrapedurl.replace("&amp;","&")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_srcserie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# =============================================================================================================================================

def categorias_serie(item):
    logger.info("[streamondemand-pureita videotecaproject] categorias_serie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, 'GENERE.png"[^>]+>(.*?)</p>')


    # Extrae las entradas (carpetas)
    # patron = '<a\s*href="([^"]+)" target="_blank"><img alt="" src=".*?[^A-Z]+([^.]+)[^<]+"><\/a>'
    patron = '<a\s*href="([^"]+)".*?<img alt="" src=".*?\/\/+[^\/]+[^.]+\/([^"]+)"[^>]+><\/a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if "ANIMAZIONE" in scrapedtitle:
          continue

        scrapedtitle = scrapedtitle.replace("STORICOBIOGRAFICO", "Storico - Biografico")
        scrapedtitle = scrapedtitle.replace(".png", "")
        scrapedtitle = scrapedtitle.replace("SERIETERMINATE", "Serie - Concluse")
        scrapedtitle = scrapedtitle.replace("SERIEINCORSO", "Serie  - in Corso")
        scrapedtitle = scrapedtitle.title()
        scrapedtitle = scrapedtitle.replace("Seriesd", "Serie SD").replace("Seriehd", "Serie HD")
        scrapedthumbnail=""
        scrapedplot =""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_srcserie",
                 fulltitle=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# =============================================================================================================================================

def categorias_az(item):
    logger.info("[streamondemand-pureita videotecaproject] categorias_az")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<li>\s*<a href="[^"]+">\s*Serie Tv(.*?)</li>\s*</ul>')


    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)">\s*([^\n]+)\s*<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:

        scrapedthumbnail=""
        scrapedplot =""
        #scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_serie",
                 fulltitle=scrapedtitle,
                 title=scrapedtitle,
                 url="".join([host, scrapedurl]),
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png",
                 folder=True))

    return itemlist
	
# =============================================================================================================================================

def peliculas_new(item):
    logger.info("[streamondemand-pureita videoproject] peliculas_new")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<span style=[^>]+><span style[^>]+>'
    patron += '<span style="font-family[^>]+><strong>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle in matches:
        if "x" in scrapedtitle or "ITA" in scrapedtitle:
          continue
        if scrapedtitle=="":
          continue		  
        scrapetitle=scrapedtitle
        scrapedtitle=scrapedtitle.replace("°", "")			
        scrapedtitle=re.sub(r'(\d+)', lambda m : m.group(1).zfill(2), scrapedtitle)

        #scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 fulltitle=scrapetitle,
                 action="peliculas_date",
                 title="[COLOR yellow]" + scrapedtitle + "[/COLOR]",
                 url=item.url,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png",
                 folder=True))
				 
    # Extrae las entradas (carpetas)
    patron = '<span[^>]+><span style[^>]+>'
    patron += '<span style[^>]+>([^<]+)<\/span><\/span><\/span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle in matches:
        if "x" in scrapedtitle or "ITA" in scrapedtitle:
          continue
        if scrapedtitle=="":
          continue
        scrapetitle=scrapedtitle
        scrapedtitle=scrapedtitle.replace("°", "")		
        scrapedtitle=re.sub(r'(\d+)', lambda m : m.group(1).zfill(2), scrapedtitle)
		  
        #scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 fulltitle=scrapetitle,
                 action="peliculas_date",
                 title="[COLOR yellow]" + scrapedtitle + "[/COLOR]",
                 url=item.url,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png",
                 folder=True))

				 
    itemlist.sort(key=lambda x: x.title)
    itemlist.reverse()
    return itemlist
	
# =============================================================================================================================================

def pelis_new(item):
    logger.info("[streamondemand-pureita videotecaproject] pelis_new")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	 				 
    patron = '<p style[^>]+>(?:<span[^>]+|)<a href="([^"]+)[^>]+>'
    patron += '(?:<span[^>]+><span[^>]+>|)(?:<strong>|)(?:<span[^>]+>|)(?:&nbsp;<\/span>|)'
    patron += '<img alt=""\s*src="([^"]+)"[^>]+>[^=]+=[^=]+=[^>]+>[^>]+>[^=]+=[^=]+=[^>]+>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace('<span style="display: none;">&nbsp;</span>', "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace(".S.", ".").replace("</span>", "")
        #scrapedtitle = scrapedtitle.title()
        if "videotecaproject" in scrapedtitle:
          continue
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        stitle=''.join(i for i in scrapedtitle if not i.isdigit())
        stitle = stitle.replace(" x e", "").replace("x ITA", "").replace(" da x a", "").replace("()", "")
        stitle = stitle.replace("Episodio", "").replace("Stagioni", "").replace("da  a", "").replace(" e  ITA", "").replace("Forced Sub", "")
        stitle = stitle.replace("+", "").replace("-ENG", "").replace("ENG", "").replace("SUB", "").replace("</span>", "")
        stitle = stitle.replace("ITA", "").replace("Stagione", "").replace(" x", "").strip()
        if "100" in scrapedtitle:
          stitle=stitle+" 100"			
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=stitle,
                 show=stitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 
				 
    patron = '<br>\s*(?:<span[^>]+><span[^>]+><strong>|)\s*<a href="([^"]+)"[^>]+>'
    patron += '<img alt=""\s*(?:height="\d+"|)\s*src="([^"]+)"[^>]+><br>\s*<br>\s*'
    patron += '(?:<strong>|)(?:<span[^>]+><span[^>]+>|)(?:<strong>|)([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace('<span style="display: none;">&nbsp;</span>', "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace(".S.", ".").replace("</span>", "")
        #scrapedtitle = scrapedtitle.title()
        if "videotecaproject" in scrapedtitle:
          continue
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        stitle=''.join(i for i in scrapedtitle if not i.isdigit())
        stitle = stitle.replace(" x e", "").replace("x ITA", "").replace(" da x a", "").replace("()", "")
        stitle = stitle.replace("Episodio", "").replace("Stagioni", "").replace("da  a", "").replace(" e  ITA", "").replace("Forced Sub", "")
        stitle = stitle.replace("+", "").replace("-ENG", "").replace("ENG", "").replace("SUB", "").replace("</span>", "")
        stitle = stitle.replace("ITA", "").replace("Stagione", "").replace(" x", "").strip()
        if "100" in scrapedtitle:
          stitle=stitle+" 100"			
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=stitle,
                 show=stitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    itemlist.sort(key=lambda x: x.title)
    return itemlist

# =============================================================================================================================================

def peliculas_tv(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_tv")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '</table>(.*?)<div class="widget-footer"></div>')
	
    # Extrae las entradas (carpetas)
    patron = '<a href="(http.*?[^.]+[^\/]+\/[^\/]+\/([^"]+))".*?src="([^"]+)" style="[^>]+>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle, scrapedthumbnail  in matches:
        scrapedplot = ""
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("-", " ").replace("ita1/", "")
        scrapedtitle = scrapedtitle.replace("/", "").replace("ita", "")
        scrapedtitle = scrapedtitle.title()
        scrapedtitle = scrapedtitle.strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
   
    return itemlist

# =============================================================================================================================================

def peliculas_tvshow(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_srcserie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("<strong>", "").replace("</strong>", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        #scrapedtitle = re.sub(r"([0-9])", r" \1", scrapedtitle)
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapetitle = scrapedtitle.replace(" ITA", "")
        scrapetitle = scrapetitle.replace(" ENG SUB", "")

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapetitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapetitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo="tv"))
				 
    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tvshow",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
   
    return itemlist

# =============================================================================================================================================

def peliculas_serie(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_serie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">([^<]+)</a></h3>.*?'
    patron += '<div class="article-content">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedthumbnail = ""
        scrapedplot = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace(" Ita", "").replace(" ITA", "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace("-", " ")
        scrapedtitle = scrapedtitle.replace("/", "").replace(":", " ")


        #scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_serie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# =============================================================================================================================================

def peliculas_date(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_date")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	 
    bloque = scrapertools.get_match(data, '%s(.*?)</(?:br|)(?:td|)>' % item.fulltitle)
	 				 

				 
    #patron = '<a href="([^"]+)"[^>]+><img alt="".*?'
    #patron += 'src="([^"]+)" [^>]+>.*?<br>\s*<br>\s*.*?<strong>(.*?)<\/strong>'
    patron = '<p style[^>]+>(?:<span[^>]+|)<a href="([^"]+)[^>]+>'
    patron += '(?:<span[^>]+><span[^>]+>|)(?:<strong>|)(?:<span[^>]+>|)(?:&nbsp;<\/span>|)'
    patron += '<img alt=""\s*src="([^"]+)"[^>]+>[^=]+=[^=]+=[^>]+>[^>]+>[^=]+=[^=]+=[^>]+>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace('<span style="display: none;">&nbsp;</span>', "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace(".S.", ".").replace("</span>", "")
        #scrapedtitle = scrapedtitle.title()
        if "videotecaproject" in scrapedtitle:
          continue
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        stitle=''.join(i for i in scrapedtitle if not i.isdigit())
        stitle = stitle.replace(" x e", "").replace("x ITA", "").replace(" da x a", "").replace("()", "")
        stitle = stitle.replace("Episodio", "").replace("Stagioni", "").replace("da  a", "").replace(" e  ITA", "").replace("Forced Sub", "")
        stitle = stitle.replace("+", "").replace("-ENG", "").replace("ENG", "").replace("SUB", "").replace("</span>", "")
        stitle = stitle.replace("ITA", "").replace("Stagione", "").replace(" x", "").strip()
        if "100" in scrapedtitle:
          stitle=stitle+" 100"			
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=stitle,
                 show=stitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 
				 
    patron = '<br>\s*(?:<span[^>]+><span[^>]+><strong>|)\s*<a href="([^"]+)"[^>]+>'
    patron += '<img alt=""\s*(?:height="\d+"|)\s*src="([^"]+)"[^>]+><br>\s*<br>\s*'
    patron += '(?:<strong>|)(?:<span[^>]+><span[^>]+>|)(?:<strong>|)([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace('<span style="display: none;">&nbsp;</span>', "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace(".S.", ".").replace("</span>", "")
        #scrapedtitle = scrapedtitle.title()
        if "videotecaproject" in scrapedtitle:
          continue
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        stitle=''.join(i for i in scrapedtitle if not i.isdigit())
        stitle = stitle.replace(" x e", "").replace("x ITA", "").replace(" da x a", "").replace("()", "")
        stitle = stitle.replace("Episodio", "").replace("Stagioni", "").replace("da  a", "").replace(" e  ITA", "").replace("Forced Sub", "")
        stitle = stitle.replace("+", "").replace("-ENG", "").replace("ENG", "").replace("SUB", "").replace("</span>", "")
        stitle = stitle.replace("ITA", "").replace("Stagione", "").replace(" x", "").strip()
        if "100" in scrapedtitle:
          stitle=stitle+" 100"			
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=stitle,
                 show=stitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
			 
    return itemlist	
	
# =============================================================================================================================================
	
def episodios(item):
    logger.info("[streamondemand-pureita videotecaproject] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, '(?:Stagione.*?|)(?:Miniserie ITA.*?|)</span>(.*?)<footer class="widget-footer">')
	
    patron = '<p(.*?)</span>(?:</strong>|)</span>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for puntata in matches:
        puntata = puntata + '<span style="font-size: 14px;">'

        scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank">([^<]+)<')

        if scrapedtitle=="":
           scrapedtitle=scrapertools.find_single_match(puntata, '<span[^>]+>([^<]+)')
        if "Wstream" in scrapedtitle:
          continue
	
        #if '<span style="font-weight: 700;">' in puntata:
          #scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank">([^<]+)<')

        if "Stagione" in puntata:
          scrapedtitle=scrapertools.find_single_match(puntata, '<span style="font-weight: 700;">([^<]+)<')
          if not "Stagione" in scrapedtitle:
            scrapedtitle=scrapertools.find_single_match(puntata, '<span style="font-family:\s*tahoma,\s*geneva,\s*sans-serif;">([^<]+)')
          	  
        if "Stagione" in scrapedtitle:
           scrapedtitle = "[COLOR yellow]" + scrapedtitle + "[/COLOR]"
        #if not "x" in scrapedtitle and not "Stagione" in scrapedtitle and not "Openload" in scrapedtitle and not "Parte" in scrapedtitle:
          #continue
        if "Wstream" in scrapedtitle:
          continue		  
        if "Trama:" in scrapedtitle:
          continue
        if scrapedtitle.startswith(item.show):
          continue
        if scrapedtitle=="":
          continue
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=puntata,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                 folder=True))

    patron = 'div>(.*?)</span></'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for puntata in matches:
        scrapedtitle=scrapertools.find_single_match(puntata, '<a\s*href="http.*?:\/\/.*?\/[^.]+[^\d+]+([^\.]+)[^>]+>')
        #scrapedtitle=scrapedtitle.replace("E", "x")
        if not "x" in scrapedtitle:
          scrapedtitle=scrapertools.find_single_match(puntata, '<strong>([^<]+)<\/strong>')

        if scrapedtitle=="":
          scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank">([^<]+)</a>')
          if scrapedtitle=="":
            scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank"><strong><span style="font-size:14px;"><span style="font-family:tahoma,geneva,sans-serif;">([^<]+)')

        if "/" in scrapedtitle:
          scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank">([^<]+)</a>')
        if "Wstream" in scrapedtitle:
          scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank">([^<]+)\s*<span')
        if "Stagione" in scrapedtitle:
           scrapedtitle = "[COLOR yellow]" + scrapedtitle + "[/COLOR]"
        #if not "x" in scrapedtitle and not "Stagione" in scrapedtitle and not "Openload" in scrapedtitle and not "Parte" in scrapedtitle:
          #continue
		  
        if "Trama:" in scrapedtitle:
          continue
        if scrapedtitle.startswith(item.show):
          continue
        if scrapedtitle=="":
          continue
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=puntata,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR]  " + item.plot,
                 folder=True))
				
			 
    return itemlist
	
# =============================================================================================================================================
# TILL 1182
# =============================================================================================================================================
	
def findvideos(item):
    logger.info("[streamondemand-pureita videotecaproject] findvideos")
    itemlist = []

    patron = '<a href="(([^.]+).*?)"\s*target="_blank">'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("https://", "").replace("http://", "")
        #if "vcrypt" in scrapedtitle:
          #continue
        scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title,
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 
    patron = '<a href="([^"]+)\s*" target="_blank">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("https://", "").replace("http://", "")
        scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure][[COLOR orange]" + scrapedtitle + "[/COLOR]] " + item.title,
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 
    return itemlist

# =============================================================================================================================================	
	
def play(item):
    itemlist=[]

    data = item.url
    if 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url
		
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.show])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist


# =============================================================================================================================================
# =============================================================================================================================================
# =============================================================================================================================================

'''	
def menu_movie(item):
    logger.info("streamondemand-pureita.videotecaproject menu_movie")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Raccomandati[/COLOR]",
                     action="peliculas_list",
                     url="%s/film/versione-temporanea/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Ultimi Aggiornati[/COLOR]",
                     action="peliculas",
                     url="%s/film/ultimi-200-film-inseriti/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Genere[/COLOR]",
                     action="categorias",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- HD[/COLOR]",
                     action="peliculas_srcmovie",
                     url=host + "/tags/Film%20HD/",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- 3D[/COLOR]",
                     action="peliculas_srcmovie",
                     url=host + "/tags/Film%203D/",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_3D_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Lista A/Z[/COLOR]",
                     action="peliculas_list",
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]


    return itemlist

# =============================================================================================================================================

def categorias(item):
    logger.info("[streamondemand-pureita videotecaproject] serie_az")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, 'GENERE.png"[^>]+>(.*?)</p>')


    # Extrae las entradas (carpetas)
    # patron = '<a\s*href="([^"]+)" target="_blank"><img alt="" src=".*?[^A-Z]+([^.]+)[^<]+"><\/a>'
    patron = '<a\s*href="([^"]+)".*?<img alt="" src=".*?\/\/+[^\/]+[^.]+\/([^"]+)"[^>]+><\/a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        #if "ANIMAZIONE" in scrapedtitle:
          #continue

        scrapedtitle = scrapedtitle.replace("STORICOBIOGRAFICO", "Storico - Biografico")
        scrapedtitle = scrapedtitle.replace(".png", "")
        scrapedtitle = scrapedtitle.replace("FILMHD", "Film HD").replace("FILM3D", "Film 3D")
        scrapedtitle = scrapedtitle.replace("FILMSD", "Film SD")
        scrapedtitle = scrapedtitle.title()
        scrapedthumbnail=""
        scrapedplot =""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_srcmovie",
                 fulltitle=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist
	
# =============================================================================================================================================

def peliculas_list(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_list")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">([^<]+)</a></h3>\s*<span class="article-date">[^<]+</span>\s*'
    patron += '</header>\s*<div class="article-content">(.*?)<\/div>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedthumbnail = ""
        scrapedplot = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace("https://www.videotecaproject.eu/news/", "")
        scrapedtitle = scrapedtitle.replace(":", " ")
        scrapedtitle = scrapedtitle.replace("/", "")
        scrapedtitle =scrapedtitle.title()

        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_film",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# =============================================================================================================================================
	
def peliculas(item):
    logger.info("streamondemand-pureita majintoon lista_animation")
    itemlist = []
    minpage = 14
	
    p = 1
    if '{}' in item.url:
       item.url, p = item.url.split('{}')
       p = int(p)

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<a\s*href="((http[^"]+))".*?>\s*<img\s*src="([^"]+)"\s*style[^>]+>\s*<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedtitle, scrapedthumbnail) in enumerate(matches):
        if (p - 1) * minpage > i: continue
        if i >= p * minpage: break
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("https://www.videotecaproject.eu/news/", "")

        scrapedtitle = scrapedtitle.replace("-", " ").replace("1/", "")
        scrapedtitle = scrapedtitle.replace(":", " - ").replace("2/", "")
        scrapedtitle = scrapedtitle.replace("3/", "").replace("/", "")
        scrapedtitle = re.sub(r"([0-9])", r" \1", scrapedtitle)
        scrapedtitle = re.sub('(?<=\d) (?=\d)', '', scrapedtitle)

        scrapedtitle = scrapedtitle.title()
        scrapedtitle = scrapedtitle.strip()
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("A ", "")
        scrapedtitle = scrapedtitle.replace("Sub Ita", "(Sub Ita)")       
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_film",
                 contentType="movie",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 extra="tv",
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo="movie"))
				 
    # Extrae el paginador
    if len(matches) >= p * minpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# =============================================================================================================================================
	
def peliculas_srcmovie(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_srcmovie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("<strong>", "").replace("</strong>", "")
        scrapedtitle = scrapedtitle.replace(" ITA", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        #scrapedtitle = re.sub(r"([0-9])", r" \1", scrapedtitle)

        if "serie" in scrapedurl or "ita" in scrapedurl:
         continue


        if "-A-B-" in scrapedtitle or "-E-F" in scrapedtitle or "-I-J" in scrapedtitle:
          continue
        if "-M-N" in scrapedtitle or "-Q-R" in scrapedtitle or "-W-X" in scrapedtitle:
          continue
        if not "ITA" in scrapedtitle or not  "serie" in scrapedurl:
         continue
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_film" if not "film" in scrapedurl else "peliculas_list",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_srcmovie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
   
    return itemlist
	
# =============================================================================================================================================


def categorias_old(item):
    logger.info("[streamondemand-pureita videotecaproject] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data


    # Extrae las entradas (carpetas)
    patron = '<a href="[^"]+">\s*([^\n]+)\s*<\/a>\s*<ul class="level2">\s*<li class="first">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle in matches:
        scrapedthumbnail=""
        scrapedplot =""
        scrapedurl =""
        scrapedtitle = scrapedtitle.strip()
        itemlist.append(
            Item(channel=__channel__,
                 action="listmovie",
                 fulltitle=scrapedtitle,
                 title=scrapedtitle,
                 url=host,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# =============================================================================================================================================

def listmovie(item):
    logger.info("[streamondemand-pureita videotecaproject] categorias_list")
    itemlist = []
    minpage = 14
	
    p = 1
    if '{}' in item.url:
       item.url, p = item.url.split('{}')
       p = int(p)
	
    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '%s(.*?)</ul>\s*</li>' % item.fulltitle)
				 
    patron = '<a href="([^"]+)">\s*([^\n]+)\s*<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * minpage > i: continue
        if i >= p * minpage: break
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapedtitle.replace(" Ita", "").replace(" ITA", "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace("-", " ")
        scrapedtitle = scrapedtitle.replace("/", "").replace(":", " ")

        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="peliculas_listmovie",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url="".join([host, scrapedurl]),
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))
				 
    # Extrae el paginador
    if len(matches) >= p * minpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="listmovie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# =============================================================================================================================================

def peliculas_old(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a\s*href="((http[^"]+))".*?>\s*<img\s*src="([^"]+)"\s*style[^>]+>\s*<\/a>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace("https://www.videotecaproject.eu/news/", "")

        #scrapedtitle = ''.join(' ' + char if char.isupper() else char.strip() for char in text).strip()
        scrapedtitle = scrapedtitle.replace("-", " ")
        scrapedtitle = scrapedtitle.replace(":", " ")
        scrapedtitle = scrapedtitle.replace("/", "")
        scrapedtitle = re.sub(r"([0-9])", r" \1", scrapedtitle)
        scrapedtitle = re.sub('(?<=\d) (?=\d)', '', scrapedtitle)
        scrapedtitle =scrapedtitle.title()
        #scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        #scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_film",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    return itemlist

# =============================================================================================================================================
	
def peliculas_listmovie(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">([^<]+)</a></h3>.*?'
    patron += '<div class="article-content">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedthumbnail = ""
        scrapedplot = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace(" Ita", "").replace(" ITA", "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace("-", " ")
        scrapedtitle = scrapedtitle.replace("/", "").replace(":", " ")

        scrapedtitle =scrapedtitle.strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_film",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    return itemlist
	
def findvideos_film(item):
    logger.info("[streamondemand-pureita videotecaproject] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data


    # Extrae las entradas (carpetas)
    patron = '<a href="([^\/]+\/\/([^.]+)[^"]+)" target="_blank"><img alt=""\s*src="([^"]+)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        if "www" in scrapedtitle:
          continue
        quality=" ([COLOR yellow]SD[/COLOR])"
        if "1080p" in scrapedurl or  "full hd " in scrapedthumbnail:
           quality=" ([COLOR yellow]Full HD[/COLOR])"
        if "720p" in scrapedurl or "hd." in scrapedthumbnail:
           quality=" ([COLOR yellow]HD[/COLOR])"
        if "3D" in scrapedurl or "3D.png" in scrapedthumbnail:
           quality=" ([COLOR yellow]3D[/COLOR])"          
        scrapedplot =""
        scrapedtitle = scrapedtitle.strip()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=scrapedtitle,
                 title="[COLOR azure]" + item.title + quality + " [[COLOR orange]" + scrapedtitle.capitalize() + "[/COLOR]]",
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    patron = '<p style="text-align: center;"><iframe allowfullscreen="true" frameborder[^>]+ src="([^\/]+\/\/([^.]+)[^"]+)" [^>]+></iframe></p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "www" in scrapedtitle:
          continue
        quality=" ([COLOR yellow]SD[/COLOR])" 
        if "1080p" in scrapedurl:
           quality=" ([COLOR yellow]Full HD[/COLOR])"
        if "720p" in scrapedurl:
           quality=" ([COLOR yellow]HD[/COLOR])"
                    
        scrapedplot =""
        scrapedtitle = scrapedtitle.strip()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=scrapedtitle,
                 title="[COLOR azure]" + item.title + quality + " [[COLOR orange]" + scrapedtitle.capitalize() + "[/COLOR]]",
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 			 
    return itemlist
	
# =============================================================================================================================================
def peliculas_date(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_date")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	 
    bloque = scrapertools.get_match(data, '%s(.*?)</(?:br|)(?:td|)>' % item.fulltitle)
	 				 
    patron = 'src="([^"]+)"[^>]+>[^>]+>[^>]+>\s*[^>]+>[^>]+>[^>]+>.*?'
    patron += '<strong><a href="([^"]+)"[^>]+>([^<]+)(?:</a>|)(?:<span|)'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedthumbnail, scrapedurl, scrapedtitle  in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace(".S.", ".")
        #scrapedtitle = scrapedtitle.title()
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        stitle=''.join(i for i in scrapedtitle if not i.isdigit())
        stitle = stitle.replace(" x e", "").replace("x ITA", "").replace(" da x a", "").replace("()", "")
        stitle = stitle.replace("Episodio", "").replace("Stagioni", "").replace("da  a", "").replace(" e  ITA", "")
        stitle = stitle.replace("ITA", "").replace("Stagione", "").replace(" x", "").strip()
        if "100" in scrapedtitle:
          stitle=stitle+" 100"			
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=stitle,
                 show=stitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 
    #patron = '<a href="([^"]+)"[^>]+><img alt="".*?'
    #patron += 'src="([^"]+)" [^>]+>.*?<br>\s*<br>\s*.*?<strong>(.*?)<\/strong>'
    patron = '<a href="([^"]+)[^>]+>(?:<span[^>]+>.*?|)<img alt="".*?src="([^"]+)[^>]+>(?:<span[^>]+>[^>]+>|)'
    patron += '.*?<br>\s*<br>\s*.*?<strong>(.*?)<\/strong>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace('<span style="display: none;">&nbsp;</span>', "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace(".S.", ".")
        #scrapedtitle = scrapedtitle.title()
        if "videotecaproject" in scrapedtitle:
          continue
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        stitle=''.join(i for i in scrapedtitle if not i.isdigit())
        stitle = stitle.replace(" x e", "").replace("x ITA", "").replace(" da x a", "").replace("()", "")
        stitle = stitle.replace("Episodio", "").replace("Stagioni", "").replace("da  a", "").replace(" e  ITA", "")
        stitle = stitle.replace("ITA", "").replace("Stagione", "").replace(" x", "").strip()
        if "100" in scrapedtitle:
          stitle=stitle+" 100"			
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=stitle,
                 show=stitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 
    patron = '<a href="([^"]+)[^>]+>(?:<span[^>]+>.*?|)<img alt="".*?'
    patron += 'src="([^"]+)[^>]+>(?:<span[^>]+>[^>]+>|).*?'
    patron += '<\/a><\/p>\s*<p\s*style[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>([^<]+)'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace('<span style="display: none;">&nbsp;</span>', "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace(" &amp; ", " ").replace(".S.", ".")
        #scrapedtitle = scrapedtitle.title()
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        stitle=''.join(i for i in scrapedtitle if not i.isdigit())
        stitle = stitle.replace(" x e", "").replace("x ITA", "").replace("da x a", "").replace("()", "")
        stitle = stitle.replace("Episodio", "").replace("Stagioni", "").replace("da  a", "").replace(" e ITA", "")
        stitle = stitle.replace("ITA", "").replace("Stagione", "").replace(" x", "").strip()
        if "100" in scrapedtitle:
          stitle=stitle+" 100"	
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=stitle,
                 show=stitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
    return itemlist	
	
# =============================================================================================================================================
'''
>>>>>>> 936c940443d66985bf10575e38517a4816c6c709
