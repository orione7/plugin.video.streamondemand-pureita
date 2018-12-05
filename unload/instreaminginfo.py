# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para instreaminginfo
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import sys
import time
import urllib2
import urlparse
 
from core import config
from core import logger
from core import scrapertools
from core.item import Item
from servers import servertools
 
__channel__ = "instreaminginfo"
__category__ = "F"
__type__ = "generic"
__title__ = "instreaming.info (IT)"
__language__ = "IT"
 
DEBUG = config.get_setting("debug")
 
host = "http://altadefinizione.me"
 
headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host],
    ['Connection', 'keep-alive']
]
 
def isGeneric():
    return True
 
def mainlist(item):
    logger.info("streamondemand.cinemano mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     extra="film",
                     url="%s/news/" %host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film Per Categoria[/COLOR]",
                     action="categorias",
                     extra="film",
                     url="%s/news/" %host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas",
                     extra="serie",
                     url="%s/genere/serie-tv/" %host,
                     thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png"),
               Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]
 
    return itemlist
 
def categorias(item):
    itemlist = []
 
    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)
 
    # Extrae las entradas (carpetas)
    patron = '<li class="cat-item cat-item-[^>]+><a href="(.*?)"[^>]+>(.*?)</a>\s*</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
 
    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if DEBUG: logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 extra="film",
                 thumbnail="http://xbmc-repo-ackbarr.googlecode.com/svn/trunk/dev/skin.cirrus%20extended%20v2/extras/moviegenres/All%20Movies%20by%20Genre.png",
                 folder=True))
 
    return itemlist
 
def search(item, texto):
    logger.info("[instreaminginfo.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
 
def peliculas(item):
    logger.info("streamondemand.instreaminginfo peliculas")
    itemlist = []
 
    # Descarga la pagina
    data = anti_cloudflare(item.url)
 
    ## ------------------------------------------------
    cookies = ""
    matches = re.compile('(.instreaming.info.*?)\n', re.DOTALL).findall(config.get_cookie_data())
    for cookie in matches:
        name = cookie.split('\t')[5]
        value = cookie.split('\t')[6]
        cookies += name + "=" + value + ";"
    headers.append(['Cookie', cookies[:-1]])
    import urllib
    _headers = urllib.urlencode(dict(headers))
    ## ------------------------------------------------
 
 
    # Extrae las entradas (carpetas)
    patron = '<div class="item">\s*<a href="([^"]+)">\s*[^>]+>\s*<img src="([^"]+)" alt="([^"]+)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)
 
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        ## ------------------------------------------------
        #scrapedthumbnail += "|" + _headers
        ## ------------------------------------------------
        tmdbtitle1 = scrapedtitle.split("[")[0]
        tmdbtitle = tmdbtitle1.split("(")[0]
        try:
           if item.extra == "film": plot, fanart, poster, extrameta = info(tmdbtitle)
           if item.extra == "serie": plot, fanart, poster, extrameta = info(tmdbtitle)
 
           itemlist.append(
               Item(channel=__channel__,
                    thumbnail=poster,
                    fanart=fanart if fanart != "" else poster,
                    extrameta=extrameta,
                    plot=str(plot),
                    action="episodios" if item.extra == "serie" else "findvideos",
                    title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                    url=scrapedurl,
                    fulltitle=scrapedtitle,
                    show=scrapedtitle,
                    folder=True))
        except:
           itemlist.append(
               Item(channel=__channel__,
                    action="episodios" if item.extra == "serie" else "findvideos",
                    fulltitle=scrapedtitle,
                    show=scrapedtitle,
                    title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                    url=scrapedurl,
                    thumbnail=scrapedthumbnail,
                    plot=scrapedplot,
                    folder=True))
 
    # Extrae el paginador
 
    next_page = scrapertools.find_single_match(data, '<link rel="next" href="(.*?)" />')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png"))
 
    return itemlist
 
def episodios(item):
    logger.info("instreaminginfo.py episodi")
    itemlist = []

    data = anti_cloudflare(item.url)
    patron = '<a href="#" id="tv" onclick="setURL(.*?)".*?>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
 
    for scrapedurl, scrapedtitle in matches:
        scrapedurl = scrapertools.decodeHtmlentities(scrapedurl)
    
        itemlist.append(
                Item(channel=__channel__,
                     action="find_video_items",
                     title=scrapedtitle,
                     thumbnail=item.thumbnail,
                     url=scrapedurl))
 
    return itemlist
   
def findvideos(item):
    logger.info("[instreaminginfo.py] findvideos")

    data = anti_cloudflare(item.url)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR green][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

def find_video_items(item=None, data=None, channel=""):
    logger.info("[launcher.py] findvideos")

    data=item.url

    # Descarga la página
    if data is None:
        from core import scrapertools
        data = scrapertools.cache_page(item.url)
        #logger.info(data)
    
    # Busca los enlaces a los videos
    from core.item import Item
    from servers import servertools
    listavideos = servertools.findvideos(data)

    if item is None:
        item = Item()

    itemlist = []
    for video in listavideos:
        scrapedtitle = item.title.strip() + " - " + video[0].strip()
        scrapedurl = video[1]
        server = video[2]
        
        itemlist.append( Item(channel=item.channel, title=item.title , action="play" , server=server, page=item.page, url=scrapedurl, thumbnail=item.thumbnail, show=item.show , plot=item.plot , folder=False) )

    return itemlist

   
def anti_cloudflare(url):
    # global headers

    try:
        resp_headers = scrapertools.get_headers_from_response(url, headers=headers)
        resp_headers = dict(resp_headers)
    except urllib2.HTTPError, e:
        resp_headers = e.headers

    if 'refresh' in resp_headers:
        time.sleep(int(resp_headers['refresh'][:1]))

        urlsplit = urlparse.urlsplit(url)
        h = urlsplit.netloc
        s = urlsplit.scheme
        scrapertools.get_headers_from_response(s + '://' + h + "/" + resp_headers['refresh'][7:], headers=headers)

    return scrapertools.cache_page(url, headers=headers)

def info(title):
    logger.info("streamondemand.instreaminginfo info")
    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=title, tipo= "movie", include_adult="false", idioma_busqueda="it")
        count = 0
        if oTmdb.total_results > 0:
           extrameta = {}
           extrameta["Year"] = oTmdb.result["release_date"][:4]
           extrameta["Genre"] = ", ".join(oTmdb.result["genres"])
           extrameta["Rating"] = float(oTmdb.result["vote_average"])
           fanart=oTmdb.get_backdrop()
           poster=oTmdb.get_poster()
           plot=oTmdb.get_sinopsis()
           return plot, fanart, poster, extrameta
    except:
        pass
