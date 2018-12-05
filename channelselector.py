# -*- coding: utf-8 -*-
import urlparse,urllib2,urllib,re
import os
import sys
import urlparse
from core import config
from core import logger
from core.item import Item

DEBUG = True
CHANNELNAME = "channelselector"

def getmainlist(preferred_thumb=""):
    logger.info("channelselector.getmainlist")
    itemlist = []

    # Obtiene el idioma, y el literal
    idioma = config.get_setting("languagefilter")
    logger.info("channelselector.getmainlist idioma=%s" % idioma)
    langlistv = [config.get_localized_string(30025),config.get_localized_string(30026),config.get_localized_string(30027),config.get_localized_string(30028),config.get_localized_string(30029)]
    try:
        idiomav = langlistv[int(idioma)]
    except:
        idiomav = langlistv[0]

    # Añade los canales que forman el menú principal
    itemlist.append( Item( title=config.get_localized_string(30121) , channel="channelselector" , action="listchannels" , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_all_blueP2.png") ) )
    #itemlist.append( Item(title=config.get_localized_string(30118) , channel="channelselector" , action="channeltypes", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_canales.png") ) )
    itemlist.append( Item(title=config.get_localized_string(30119) , channel="channelselector" , action="channeltypes", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_category_blueP2.png") ) )
    itemlist.append( Item(title=config.get_localized_string(50002) , channel="novedades" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_novita_blueP2.png") ) )
    #itemlist.append( Item(title=config.get_localized_string(30103) , channel="buscador" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_buscar.png")) )
    #itemlist.append( Item(title="The Movie Database" , channel="database" , action="mainlist" , thumbnail= "http://www.userlogos.org/files/logos/Vyp3R/TMDb.png" ) )
    itemlist.append( Item(title="Ricerca Globale" , channel="biblioteca" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_search_blueP2.png")) )
    #itemlist.append( Item(title="Biblioteca" , channel="buscador" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_biblioteca.png")) )
    #itemlist.append( Item(title="Biblioteca Registi" , channel="bibliotecaregisti" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_biblioteca.png")) )
    #itemlist.append( Item(title="Biblioteca Attori" , channel="bibliotecaattori" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_biblioteca.png")) )
    itemlist.append( Item(title="Oggi in TV" , channel="filmontv" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_oggitv_blueP2.png")) )
    #itemlist.append( Item(title="Contenuti Vari" , channel="novedades" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_novedades.png") ) )
    itemlist.append( Item(title=config.get_localized_string(40103) , channel="youtube" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_youtube_blue2.png")) )
    #if config.is_xbmc(): itemlist.append( Item(title=config.get_localized_string(30128) , channel="trailertools" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_trailers.png")) )
    itemlist.append( Item(title=config.get_localized_string(30102) , channel="favoritos" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_favorite_blueP2.png")) )
    #itemlist.append( Item(title=config.get_localized_string(30131) , channel="libreria" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_biblioteca.png")) )
    if config.get_platform()=="rss":itemlist.append( Item(title="pyLOAD (Beta)" , channel="pyload" , action="mainlist" , thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"pyload.png")) )
    itemlist.append( Item(title=config.get_localized_string(30101) , channel="descargas" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_download_blueP2.png")) )

    if "xbmceden" in config.get_platform():
        itemlist.append( Item(title=config.get_localized_string(30100) , channel="configuracion" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_settings_blueP2.png"), folder=False) )
    else:
        itemlist.append( Item(title=config.get_localized_string(30100) , channel="configuracion" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_settings_blueP2.png")) )

    #if config.get_setting("fileniumpremium")=="true":
    #   itemlist.append( Item(title="Torrents (Filenium)" , channel="descargasfilenium" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(),"torrents.png")) )

    #if config.get_library_support():
    if config.get_platform()!="rss": itemlist.append( Item(title=config.get_localized_string(30104) , channel="ayuda" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_help_blueP2.png")) )
    return itemlist

# TODO: (3.1) Pasar el código específico de XBMC al laucher
def mainlist(params,url,category):
    logger.info("channelselector.mainlist")

    # Verifica actualizaciones solo en el primer nivel
    if config.get_platform()!="boxee":
        try:
            from core import updater
        except ImportError:
            logger.info("channelselector.mainlist No disponible modulo actualizaciones")
        else:
            if config.get_setting("updatecheck2") == "true":
                logger.info("channelselector.mainlist Verificar actualizaciones activado")
                try:
                    updater.checkforupdates()
                except:
                    import xbmcgui
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Impossibile connettersi","Non è stato possibile verificare","la disponibilità di aggiornamenti")
                    logger.info("channelselector.mainlist Fallo al verificar la actualización")
                    pass
            else:
                logger.info("channelselector.mainlist Verificar actualizaciones desactivado")

    itemlist = getmainlist()
    for elemento in itemlist:
        logger.info("channelselector.mainlist item="+elemento.title)
        addfolder(elemento.title , elemento.channel , elemento.action , thumbnail=elemento.thumbnail, folder=elemento.folder)

    # Label (top-right)...
    import xbmcplugin
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

    if config.get_setting("forceview")=="true":
        # Confluence - Thumbnail
        import xbmc
        xbmc.executebuiltin("Container.SetViewMode(500)")

def channeltypes(params,url,category):
    logger.info("channelselector.mainlist channeltypes")
    categoria=category.decode('latin1').encode('utf-8')
    if config.get_localized_string(30119) in categoria:
        lista = getchanneltypes()
        for item in lista:
            addfolder(item.title,item.channel,item.action,item.category,item.thumbnail,item.thumbnail)
       
        # Label (top-right)...
        import xbmcplugin
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

        if config.get_setting("forceview")=="true":
            # Confluence - Thumbnail
            import xbmc
            xbmc.executebuiltin("Container.SetViewMode(500)")
    else:
        listchannels({'action': 'listchannels', 'category': '%2a', 'channel': 'channelselector'},'','*')

def getchanneltypes(preferred_thumb=""):
    logger.info("channelselector getchanneltypes")
    itemlist = []
    #itemlist.append( Item( title=config.get_localized_string(30121) , channel="channelselector" , action="listchannels" , category="*"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_canales_todos.png")))
    itemlist.append( Item( title="Top Channels" , channel="channelselector" , action="listchannels" , category="B"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_topchannels_blueP2.png")))
    itemlist.append( Item( title=config.get_localized_string(30122) , channel="channelselector" , action="listchannels" , category="F"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_movie_blueP2.png")))
    itemlist.append( Item( title=config.get_localized_string(30123) , channel="channelselector" , action="listchannels" , category="S"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_tvshow_blueP2.png")))
    itemlist.append( Item( title=config.get_localized_string(30124) , channel="channelselector" , action="listchannels" , category="A"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_anime_blueP2.png")))
    itemlist.append( Item( title="Saghe" , channel="saghe", action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_saghe_blueP2.png") ) )
    itemlist.append( Item( title=config.get_localized_string(30125) , channel="channelselector" , action="listchannels" , category="D"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_documentary_blueP2.png")))
    itemlist.append( Item( title=".NET Lover", channel="netlover" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"netlover.png") ) )
    #itemlist.append( Item( title="Contenuti Vari" , channel="novedades" , action="mainlist", thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_novedades.png") ) )
    itemlist.append( Item( title=config.get_localized_string(30136) , channel="channelselector" , action="listchannels" , category="VOS" , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_original_blueP2.png")))
    #itemlist.append( Item( title="Torrent" , channel="channelselector" , action="listchannels" , category="T" , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_torrent_blueP.png")))
    itemlist.append( Item( title="Film 3D" , channel="channelselector" , action="listchannels" , category="3" , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"banner_3d_blueP2.png")))
    #itemlist.append( Item( title=config.get_localized_string(30126) , channel="channelselector" , action="listchannels" , category="M"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_canales_musica.png")))
    #itemlist.append( Item( title="Bittorrent" , channel="channelselector" , action="listchannels" , category="T"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_canales_torrent.png")))
    #itemlist.append( Item( title=config.get_localized_string(30127) , channel="channelselector" , action="listchannels" , category="L"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_canales_latino.png")))
    #if config.get_setting("enableadultmode") == "true": itemlist.append( Item( title=config.get_localized_string(30126) , channel="channelselector" , action="listchannels" , category="X"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_canales_adultos.png")))
    #itemlist.append( Item( title=config.get_localized_string(30127) , channel="channelselector" , action="listchannels" , category="G"   , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"thumb_canales_servidores.png")))
    #itemlist.append( Item( title=config.get_localized_string(30134) , channel="channelselector" , action="listchannels" , category="NEW" , thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"novedades.png")))
    return itemlist
'''
def channeltypes(params,url,category):
    logger.info("channelselector.mainlist channeltypes")

    lista = getchanneltypes()
    for item in lista:
        addfolder(item.title,item.channel,item.action,item.category,item.thumbnail,item.thumbnail)

    # Label (top-right)...
    import xbmcplugin
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

    if config.get_setting("forceview")=="true":
        # Confluence - Thumbnail
        import xbmc
        xbmc.executebuiltin("Container.SetViewMode(500)")
'''
def listchannels(params,url,category):
    logger.info("channelselector.listchannels")

    lista = filterchannels(category)
    for channel in lista:
        if channel.type=="xbmc" or channel.type=="generic":
            if channel.channel=="personal":
                thumbnail=config.get_setting("personalchannellogo")
            elif channel.channel=="personal2":
                thumbnail=config.get_setting("personalchannellogo2")
            elif channel.channel=="personal3":
                thumbnail=config.get_setting("personalchannellogo3")
            elif channel.channel=="personal4":
                thumbnail=config.get_setting("personalchannellogo4")
            elif channel.channel=="personal5":
                thumbnail=config.get_setting("personalchannellogo5")
            else:
                thumbnail=channel.thumbnail
                if thumbnail == "":
                    thumbnail=urlparse.urljoin(get_thumbnail_path(),channel.channel+".png")
            addfolder(channel.title , channel.channel , "mainlist" , channel.channel, thumbnail = thumbnail)

    # Label (top-right)...
    import xbmcplugin
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=category )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

    if config.get_setting("forceview")=="true":
        # Confluence - Thumbnail
        import xbmc
        xbmc.executebuiltin("Container.SetViewMode(500)")

def filterchannels(category,preferred_thumb=""):
    returnlist = []

    if category=="NEW":
        channelslist = channels_history_list()
        for channel in channelslist:
            channel.thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),channel.channel+".png")
            channel.plot = channel.category.replace("VOS","Versione con audio originale e sottotitoli").replace("F","Film").replace("S","Serie TV").replace("D","Documentari").replace("A","Anime").replace("B","Best").replace(",",", ")
            returnlist.append(channel)
    else:
        try:
            idioma = config.get_setting("languagefilter")
            logger.info("channelselector.filterchannels idioma=%s" % idioma)
            langlistv = ["","ES","EN","IT","PT"]
            idiomav = langlistv[int(idioma)]
            logger.info("channelselector.filterchannels idiomav=%s" % idiomav)
        except:
            idiomav=""

        channelslist = channels_list()

        for channel in channelslist:
            # Pasa si no ha elegido "todos" y no está en la categoría elegida
            if category<>"*" and category not in channel.category:
                #logger.info(channel[0]+" no entra por tipo #"+channel[4]+"#, el usuario ha elegido #"+category+"#")
                continue
            # Pasa si no ha elegido "todos" y no está en el idioma elegido
            if channel.language<>"" and idiomav<>"" and idiomav not in channel.language:
                #logger.info(channel[0]+" no entra por idioma #"+channel[3]+"#, el usuario ha elegido #"+idiomav+"#")
                continue
            if channel.thumbnail == "":
                channel.thumbnail = urlparse.urljoin(get_thumbnail_path(preferred_thumb),channel.channel+".png")
            channel.plot = channel.category.replace("VOS","Versione con audio originale e sottotitoli").replace("F","Film").replace("S","Serie TV").replace("D","Documentari").replace("A","Anime").replace("B","Best").replace(",",", ")
            returnlist.append(channel)

    return returnlist

def channels_history_list():
    itemlist = []
    return itemlist

def channels_list():
    itemlist = []

    #itemlist.append( Item( viewmode="movie", title="Inserisci un URL..."         , channel="tengourl"   , language="" , category="" , type="generic"  ))
    if config.get_setting("personalchannel")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname") , channel="personal" , language="" , category="" , type="generic"  ))
    if config.get_setting("personalchannel2")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname2") , channel="personal2" , language="" , category="" , type="generic"  ))
    if config.get_setting("personalchannel3")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname3") , channel="personal3" , language="" , category="" , type="generic"  ))
    if config.get_setting("personalchannel4")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname4") , channel="personal4" , language="" , category="" , type="generic"  ))
    if config.get_setting("personalchannel5")=="true":
        itemlist.append( Item( title=config.get_setting("personalchannelname5") , channel="personal5" , language="" , category="" , type="generic"  ))
    #itemlist.append( Item( title="[COLOR red]SkyStreaming[/COLOR]"        , channel="iptv"       , language="IT"    , category="B,F"       , type="generic"))
    itemlist.append( Item( title="[COLOR azure]AltaDefinizione01_zone[/COLOR]"      , channel="altadefinizione01_zone"           , language="IT"    , category="F,B"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]AltaDefinizione_Video[/COLOR]" , channel="altadefinizione01_video" , language="IT" , category="B,F" , type="generic"))
    itemlist.append( Item( title="[COLOR azure]AltaDefinizione01_biz[/COLOR]"      , channel="altadefinizione01_biz"           , language="IT"    , category="F,S,VOS"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]AltaDefinizione_HD[/COLOR]"      , channel="altadefinizione_hd"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]AltaDefinizione_due[/COLOR]"      , channel="altadefinizione_due"           , language="IT"    , category="B,F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]AltadefinizioneHD/COLOR]" , channel="altadefinizionehd" , language="IT" , category="F" , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Altadefinizione.club[/COLOR]" , channel="altadefinizioneclub" , language="IT" , category="F,S" , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Altadefinizione_bid[/COLOR]" , channel="altadefinizione_bid" , language="IT" , category="B,F,S" , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Altadefinizione.one[/COLOR]" , channel="altadefinizioneone" , language="IT" , category="F" , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Altadefinizione01_wiki[/COLOR]" , channel="altadefinizione01_wiki" , language="IT" , category="F" , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]AltadefinizioneZone[/COLOR]" , channel="altadefinizionezone" , language="IT" , category="F" , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Altadefinizione.click[/COLOR]" , channel="altadefinizioneclick" , language="IT" , category="F" , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Altadefinizione.pink[/COLOR]" , channel="altadefinizione_pink" , language="IT" , category="F" , type="generic"))	
    #itemlist.append( Item( title="[COLOR azure]AltaStreaming[/COLOR]" , channel="altastreaming" , language="IT" , category="F" , type="generic"))
    itemlist.append( Item( title="[COLOR azure]AnimeForce[/COLOR]"   , channel="animeforce"           , language="IT"    , category="A"   , type="generic"))    
    itemlist.append( Item( title="[COLOR azure]AnimeHD-ITA[/COLOR]"   , channel="animehdita"           , language="IT"    , category="A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Animestream.it[/COLOR]"   , channel="animestream"           , language="IT"    , category="A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]AnimeTubeIta.com[/COLOR]"   , channel="animetubeita"           , language="IT"    , category="A"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Animevision[/COLOR]"   , channel="animevision"           , language="IT"    , category="A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]BleachAnimeManga[/COLOR]"   , channel="bleachanimemanga"           , language="IT"    , category="A"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]AnimeSenzaLimiti[/COLOR]"      , channel="animesenzalimiti"           , language="IT"    , category="A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Asian Sub-Ita[/COLOR]"      , channel="asiansubita"           , language="IT"    , category="F,S,VOS"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]BreakingBadITA Streaming[/COLOR]"      , channel="breakingbadita"           , language="IT"    , category="S"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Casa-Cinema[/COLOR]"         , channel="casacinema"           , language="IT"    , category="B,F,S,A,VOS"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]cb01_video[/COLOR]"         , channel="cb01_video"           , language="IT"    , category="F"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]CineBlog 01[/COLOR]"         , channel="cineblog01"           , language="IT"    , category="B,F,S,VOS,3"   , type="generic"  ))
    itemlist.append( Item( title="[COLOR azure]CineBlogRun[/COLOR]"         , channel="cineblogrun"           , language="IT"    , category="F,VOS"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]CineBlog01_show[/COLOR]"         , channel="cineblog01_show"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]CB01_wiki[/COLOR]"         , channel="cb01_wiki"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]CineBlog01.FM[/COLOR]"       , channel="cineblogfm"           , language="IT"    , category="F,S"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Cb01anime[/COLOR]"         , channel="cb01anime"           , language="IT"    , category="A"   , type="generic"  ))
    #itemlist.append( Item( title="[COLOR azure]cineblogrun[/COLOR]"         , channel="cineblogrun"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Cinemagratis[/COLOR]"        , channel="cinemagratis"       , language="IT"    , category="F"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Chimerarevo[/COLOR]"        , channel="chimerarevo"       , language="IT"    , category="D"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Cinefilm[/COLOR]"          , channel="cinefilm"           , language="IT"    , category="F,S"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Cinemalibero[/COLOR]"          , channel="cinemalibero"           , language="IT"    , category="F,S,A,VOS"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Cinemano[/COLOR]"          , channel="cinemano"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Cinemastreaming.net[/COLOR]"        , channel="cinemastreaming"       , language="IT"    , category="F"       , type="generic"	))
    #itemlist.append( Item( title="[COLOR azure]Cinefilm[/COLOR]"          , channel="cinefilm"           , language="IT"    , category="F,S"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Cinemasubito[/COLOR]"        , channel="cinemasubito"       , language="IT"    , category="F,S,VOS"       , type="generic"	))
    #itemlist.append( Item( title="[COLOR azure]CineSuggestions[/COLOR]"        , channel="cinesuggestions"       , language="IT"    , category="F"       , type="generic"	))
    #itemlist.append( Item( title="[COLOR azure]Corsaro Nero[/COLOR]"        , channel="corsaronero"       , language="IT"    , category="T"       , type="generic"	))
    itemlist.append( Item( title="[COLOR azure]Cucinarefacile[/COLOR]"        , channel="cucinarefacile"       , language="IT"    , category="D"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Darkstream[/COLOR]"        , channel="darkstream"       , language="IT"    , category="F"       , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Documentari_DSDA[/COLOR]"  , channel="documentari_dsda"           , language="IT"    , category="D"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]DocumentariStreamingDB[/COLOR]"  , channel="documentaristreamingdb"           , language="IT"    , category="D"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]DreamSub[/COLOR]"      , channel="dreamsub"           , language="IT"    , category="S,A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Effetto Lunatico[/COLOR]"       , channel="effettolunatico"           , language="IT"    , category="F"    , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Eurostreaming[/COLOR]"       , channel="eurostreaming"           , language="IT"    , category="F,S"    , type="generic"))
    itemlist.append( Item( title="[COLOR azure]EuroStreaming Video[/COLOR]"       , channel="eurostreaming_video"           , language="IT"    , category="F,S,A"    , type="generic"))
    itemlist.append( Item( title="[COLOR azure]FastSubITA[/COLOR]"        , channel="fastsubita"       , language="IT"    , category="S,VOS"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]FFilms[/COLOR]"          , channel="ffilms"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Fastvideo.tv[/COLOR]"        , channel="filmitaliatv"       , language="IT"    , category="F"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]FilmGratis[/COLOR]"       , channel="filmgratis"           , language="IT"    , category="F"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]FilmStreaming4[/COLOR]"       , channel="filmstreaming4"           , language="IT"    , category="F, S"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]filmhdfull[/COLOR]"          , channel="filmhdfull"           , language="IT"    , category="F,S,B"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]filmhd[/COLOR]"          , channel="filmhd"           , language="IT"    , category="F,S,B"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Filmhdstreaming[/COLOR]"          , channel="filmhdstreaming"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Filmissimi[/COLOR]"          , channel="filmissimi"           , language="IT"    , category="F"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Filmperevolvere[/COLOR]"       , channel="filmperevolvere"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]FilmStream[/COLOR]"          , channel="filmstream"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]FilmStream_biz[/COLOR]"          , channel="filmstream_biz"           , language="IT"    , category="F"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]FilmStreaming01[/COLOR]"          , channel="filmstreaming01"           , language="IT"    , category="F"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]FilmStreamingHD[/COLOR]"       , channel="filmstreaminghd"           , language="IT"    , category="B,F,S"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]FilmStreamingGratis[/COLOR]"       , channel="filmstreaminggratis"           , language="IT"    , category="F"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]FilmStreamingIta[/COLOR]"       , channel="filmstreamingita"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]FilmStreamingZone[/COLOR]"          , channel="filmstreamingzone"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]FilmZStreaming[/COLOR]"          , channel="filmzstreaming"           , language="IT"    , category="F"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Film per tutti[/COLOR]"      , channel="filmpertutti"           , language="IT"    , category="B,F,S,A"    , type="generic"     ))
    #itemlist.append( Item( title="[COLOR azure]Film Senza Limiti[/COLOR]"   , channel="filmsenzalimiti"       , language="IT"    , category="F,S,B"        , type="generic"     ))
    itemlist.append( Item( title="[COLOR azure]Filmsenzalimiti[/COLOR]"   , channel="filmsenzalimiti_blue"       , language="IT"    , category="F,B"        , type="generic"     ))
    itemlist.append( Item( title="[COLOR azure]Filmsenzalimiti_info[/COLOR]"   , channel="filmsenzalimiti_info"       , language="IT"    , category="F,S,B"        , type="generic"     ))
    #itemlist.append( Item( title="[COLOR azure]FilmZStreaming[/COLOR]"          , channel="FilmZStreaming"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]filmserietv[/COLOR]"          , channel="filmserietv"           , language="IT"    , category="F,S"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]FuturamaITA Streaming[/COLOR]"      , channel="futuramaita"           , language="IT"    , category="S"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Guardaserie.net[/COLOR]"     , channel="guardaserie"       , language="IT"    , category="S,B"        , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Guarda_Serie[/COLOR]"         , channel="guarda_serie"           , language="IT"    , category="S"    , type="generic"))
    itemlist.append( Item( title="[COLOR azure]GuardaSerie_click[/COLOR]"         , channel="guardaserie_click"           , language="IT"    , category="S"    , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]GuardaSerie_stream[/COLOR]"         , channel="guardaserie_stream"           , language="IT"    , category="F,S"    , type="generic"))
    itemlist.append( Item( title="[COLOR azure]GuardareFilm[/COLOR]"         , channel="guardarefilm"           , language="IT"    , category="F,S,A"    , type="generic"))
    itemlist.append( Item( title="[COLOR azure]GuardaFilm[/COLOR]"     , channel="guardafilm"       , language="IT"    , category="F,B"        , type="generic"))
    #itemlist.append( Item( title="[COLOR red]TEST ESTERO[/COLOR] [COLOR azure]Guardaserie.net[/COLOR]"     , channel="guardaserietest"       , language="IT"    , category="S"        , type="generic"))
    itemlist.append( Item( title="[COLOR azure]GuardoGratis[/COLOR]"         , channel="guardogratis"           , language="IT"    , category="F,S,A"    , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]GriffinITA Streaming[/COLOR]"      , channel="griffinita"           , language="IT"    , category="S"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Hubberfilm[/COLOR]"          , channel="hubberfilm"           , language="IT"    , category="F,S,A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]ildocumento.it[/COLOR]"      , channel="ildocumento"           , language="IT"    , category="D"   , type="generic"))
    itemlist.append( Item( title="[COLOR white]HDBlog.it[/COLOR]"        , channel="hdblog"       , language="IT"    , category="D"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR white]HDGratis.net[/COLOR]"        , channel="hdgratis"       , language="IT"    , category="F"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]HD-Streaming.it[/COLOR]"        , channel="hdstreamingit"       , language="IT"    , category="F,3"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]Hokuto no Ken[/COLOR]", channel="hokutonoken", language="IT"  , type="generic" , category="A"))
    itemlist.append( Item( title="[COLOR azure]IlGenioDelloStreaming[/COLOR]"      , channel="ilgeniodellostreaming"           , language="IT"    , category="F"   , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]Imovie[/COLOR]"      , channel="imovie"           , language="IT"    , category="f"   , type="generic" ))
    itemlist.append( Item( title="[COLOR azure]IlGiramondo[/COLOR]"      , channel="ilgiramondo"           , language="IT"    , category="D"   , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]Istreaming[/COLOR]"      , channel="istreaming"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]ItaFilm.tv[/COLOR]"      , channel="itafilmtv"           , language="IT"    , category="B,F,S,A"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Italia-Film.co[/COLOR]"      , channel="italiafilm"           , language="IT"    , category="B,F,S,A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]ItaliaFilm01[/COLOR]"      , channel="italiafilm01"           , language="IT"    , category="F,A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Italian-Stream [/COLOR]"        , channel="italianstream"       , language="IT"    , category="F,S"       , type="generic"))
    itemlist.append( Item( title="[COLOR azure]ItaliaFilm.Video HD[/COLOR]"      , channel="italiafilmvideohd"           , language="IT"    , category="F"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Italia Serie[/COLOR]"        , channel="italiaserie"           , language="IT"    , category="F,S,A"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]italiaserie_uno[/COLOR]"        , channel="italiaserie_uno"           , language="IT"    , category="S"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]ItaStreaming[/COLOR]"      , channel="itastreaming" , language="IT" , category="F,S,A" , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]ItFlix_stream[/COLOR]"      , channel="itflix_stream" , language="IT" , category="F,B" , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]LiberoITA[/COLOR]"       , channel="liberoita"           , language="IT"    , category="F,S,A"   , type="generic"))
    #itemlist.append( Item(title="[COLOR azure]LeserieTV[/COLOR]"    , channel="leserietv"       , language="IT"    , category="B,S"     , type="generic" ))
    #itemlist.append( Item(title="[COLOR azure]LinkStreaming[/COLOR]"    , channel="linkstreaming"       , language="IT"    , category="B,F,S"     , type="generic" ))	
    itemlist.append( Item( title="[COLOR azure]Majintoon[/COLOR]"      , channel="majintoon"           , language="IT"    , category="A,S"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Megavideo One[/COLOR]"        , channel="megavideo_one"       , language="IT"    , category="F"       , type="generic"	))
    #itemlist.append( Item( title="[COLOR azure]Misterstreaming[/COLOR]"        , channel="misterstreaming"       , language="IT"    , category="F,S"       , type="generic"	))
    itemlist.append( Item(title="[COLOR azure]MondoLunaticoHD[/COLOR]"    , channel="mondolunatico_hd"       , language="IT"    , category="F"     , type="generic" ))
    #itemlist.append( Item(title="[COLOR azure]MondoLunatico[/COLOR]"    , channel="mondolunatico"       , language="IT"    , category="F"     , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]Mondo lunatico New[/COLOR]"        , channel="mondolunatico_new"       , language="IT"    , category="F"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Naruto[/COLOR]" , channel="naruto" , language="IT" , category="A" , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Pastebin[/COLOR]"   , channel="pastebin"           , language="IT"    , category="F,S,A,VOS"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Pianeta Streaming[/COLOR]"   , channel="pianetastreaming"           , language="IT"    , category="F,S,A"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Pirate Streaming[/COLOR]"    , channel="piratestreaming"           , language="IT"    , category="B,F,S,A"   , type="generic"  ))
    #itemlist.append( Item( title="[COLOR azure]Play Cinema[/COLOR]"    , channel="playcinema"           , language="IT"    , category="F"   , type="generic"  ))
    #itemlist.append( Item( title="[COLOR azure]Portale HD[/COLOR]"   , channel="portalehd"           , language="IT"    , category="F,B,3"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Ricette Video[/COLOR]"        , channel="ricettevideo"       , language="IT"    , category="D"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]SabWap[/COLOR]"        , channel="sabwap"       , language="IT"    , category="F"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]Corsi Programmazione[/COLOR]"        , channel="programmazione"       , language="IT"    , category="D"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Saint Seiya[/COLOR]"     , channel="saintseiya"       , language="IT"    , category="A"        ))
    #itemlist.append( Item( title="[COLOR azure]Scambio Etico - TNT Village[/COLOR]"     , channel="scambioetico"       , language="IT"    , category="T" ))
    #itemlist.append( Item( title="[COLOR azure]Scambiofile[/COLOR]"     , channel="scambiofile"       , language="IT"    , category="T" ))
    itemlist.append( Item( title="[COLOR azure]Serie HD[/COLOR]"     , channel="seriehd"       , language="IT"    , category="B,S"        , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]serietvhd_stream[/COLOR]"     , channel="serietvhd_stream"       , language="IT"    , category="B,S"        , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Serietvonline[/COLOR]"     , channel="serietvonline"       , language="IT"    , category="B,S"        , type="generic"))
    itemlist.append( Item( title="[COLOR azure]Serie TV Sub ITA[/COLOR]"    , channel="serietvsubita"         , language="IT" , category="S,VOS"        , type="generic" , extra="Series"))
    itemlist.append( Item( title="[COLOR azure]SerieTVU[/COLOR]"      , channel="serietvu"           , language="IT"    , category="S"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Solo-Streaming[/COLOR]"      , channel="solostreaming"           , language="IT"    , category="F,S,A,VOS"   , type="generic" , extra="Series" ))
    #itemlist.append( Item( title="[COLOR azure]soloserie[/COLOR]"      , channel="soloserie"           , language="IT"    , category="F,S,B,VOS"   , type="generic" , extra="Series"))
    itemlist.append( Item( title="[COLOR azure]SoloStreaming_co[/COLOR]"      , channel="solostreaming_co"           , language="IT"    , category="F,S,A"   , type="generic"))
    itemlist.append( Item( title="[COLOR azure]StreamingHD[/COLOR]"      , channel="streaminghd"           , language="IT"    , category="F,S"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]StorieDellArte[/COLOR]"    , channel="storiedellarte"         , language="IT" , category="D"        , type="generic" , extra="Series" ))
    #itemlist.append( Item( title="[COLOR azure]StreamBlog[/COLOR]"    , channel="streamblog"         , language="IT" , category="S,F,A"        , type="generic" , extra="Series"))
    #itemlist.append( Item( title="[COLOR azure]StreamingItaliano[/COLOR]"    , channel="streamingitaliano"         , language="IT" , category="F"        , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]StreamingLove[/COLOR]"    , channel="streaminglove"         , language="IT" , category="F"        , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]StreamingPopcorn[/COLOR]"    , channel="streamingpopcorn"         , language="IT" , category="F"        , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]SubZero[/COLOR]"    , channel="subzero"         , language="IT" , category="T"        , type="generic" ))
    itemlist.append( Item( title="[COLOR azure]Tantifilm[/COLOR]"        , channel="tantifilm"       , language="IT"    , category="F,3"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]TheLordOfStreaming[/COLOR]"        , channel="thelordofstreaming"       , language="IT"    , category="B,F,S"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]Toonitalia[/COLOR]"        , channel="toonitalia"       , language="IT"    , category="A"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]UMSFunSub[/COLOR]"      , channel="umsfunsub"           , language="IT"    , category="A"   , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]VediSerie[/COLOR]"        , channel="vediserie"       , language="IT"    , category="B,S"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]VedoHD[/COLOR]"        , channel="vedohd"       , language="IT"    , category="B,F"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]VedoVedo[/COLOR]"        , channel="vedovedo"       , language="IT"    , category="B,S"       , type="generic" ))
    itemlist.append( Item( title="[COLOR azure]VideotecaProject[/COLOR]"        , channel="videotecaproject"       , language="IT"    , category="B,F,S"       , type="generic" ))
    #itemlist.append( Item( title="[COLOR azure]Wstreaming[/COLOR]"        , channel="wstreaming"       , language="IT"    , category="F"       , type="generic"))
    #itemlist.append( Item( title="[COLOR azure]Tuttolooneytunes[/COLOR]"        , channel="tuttolooneytunes"       , language="IT"    , category="A,D"       , type="generic"))

    return itemlist

def addfolder(nombre,channelname,accion,category="",thumbnailname="",thumbnail="",folder=True):
    if category == "":
        try:
            category = unicode( nombre, "utf-8" ).encode("iso-8859-1")
        except:
            pass
   

    import xbmc
    import xbmcgui
    import xbmcplugin
    listitem = xbmcgui.ListItem( nombre , iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
    itemurl = '%s?channel=%s&action=%s&category=%s' % ( sys.argv[ 0 ] , channelname , accion , category )
    xbmcplugin.addDirectoryItem( handle = int(sys.argv[ 1 ]), url = itemurl , listitem=listitem, isFolder=folder)
def get_thumbnail_path(preferred_thumb=""):

    WEB_PATH = ""
    
    if preferred_thumb=="":
        thumbnail_type = config.get_setting("thumbnail_type")
        if thumbnail_type=="":
            thumbnail_type="2"
        
        if thumbnail_type=="0":
            WEB_PATH = "https://raw.githubusercontent.com/orione7/Pelis_images/master/posters/"
        elif thumbnail_type=="1":
            WEB_PATH = "https://raw.githubusercontent.com/orione7/Pelis_images/master/banners/"
        elif thumbnail_type=="2":
            WEB_PATH = "https://raw.githubusercontent.com/orione7/Pelis_images/master/squares/"
    else:
        WEB_PATH = "https://raw.githubusercontent.com/orione7/Pelis_images/master/"+preferred_thumb+"/"

    return WEB_PATH
