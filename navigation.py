# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-pureita
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of streamondemand-pureita.
#
# streamondemand-pureita is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand-pureita is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand-pureita.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------

import os
import sys
import urlparse, urllib, urllib2

import xbmc
import xbmcgui
import xbmcaddon

import channelselector
import plugintools
from core.item import Item
from core import config
from core import scrapertools

config.verify_directories_created()


def get_next_items(item):
    plugintools.log("navigation.get_next_items item=" + item.tostring())

    try:
        # ----------------------------------------------------------------
        #  Main menu
        # ----------------------------------------------------------------
        if item.channel == "navigation":
            # --- Update channels list ---------------------------------------
            from core import config
            if item.action == "mainlist":
                plugintools.log("navigation.get_next_items Main menu")

                if config.get_setting("updatechannels") == "true":
                    try:
                        from core import updater
                        actualizado = updater.updatechannel("channelselector")

                        if actualizado:
                            import xbmcgui
                            advertencia = xbmcgui.Dialog()
                            advertencia.ok("PureITA", config.get_localized_string(30064))
                    except:
                        pass
            # ----------------------------------------------------------------

            if item.action == "mainlist":
                plugintools.log("navigation.get_next_items Main menu")
                itemlist = channelselector.getmainlist("bannermenu")

        elif item.channel == "channelselector":

            if item.action == "channeltypes":
                plugintools.log("navigation.get_next_items Channel types menu")
                itemlist = channelselector.getchanneltypes("bannermenu")

            elif item.action == "listchannels":
                plugintools.log("navigation.get_next_items Channel list menu")
                itemlist = channelselector.filterchannels(item.category, "bannermenu")

        elif item.channel == "configuracion":
            plugintools.open_settings_dialog()
            return []

        else:

            if item.action == "":
                item.action = "mainlist"

            plugintools.log("navigation.get_next_items Channel code (" + item.channel + "." + item.action + ")")

            # --- Update channels files --------------------------------------
            if item.action == "mainlist":
                from core import config
                if config.get_setting("updatechannels") == "true":
                    try:
                        from core import updater
                        actualizado = updater.updatechannel(item.channel)

                        if actualizado:
                            import xbmcgui
                            advertencia = xbmcgui.Dialog()
                            advertencia.ok("plugin", item.channel, config.get_localized_string(30063))
                    except:
                        pass
            # ----------------------------------------------------------------

            try:
                exec "import channels." + item.channel + " as channel"
            except:
                exec "import core." + item.channel + " as channel"

            from platformcode import xbmctools

            if item.action == "play":
                plugintools.log("navigation.get_next_items play")

                # Si el canal tiene una acción "play" tiene prioridad
                if hasattr(channel, 'play'):
                    plugintools.log("streamondemand-pureita.navigation.py Channel has its own 'play' method")
                    itemlist = channel.play(item)
                    if len(itemlist) > 0:
                        item = itemlist[0]

                        # FIXME: Este error ha que tratarlo de otra manera, al dar a volver sin ver el vídeo falla
                        try:
                            xbmctools.play_video(channel=item.channel, server=item.server, url=item.url,
                                                 category=item.category, title=item.title, thumbnail=item.thumbnail,
                                                 plot=item.plot, extra=item.extra, subtitle=item.subtitle,
                                                 video_password=item.password, fulltitle=item.fulltitle,
                                                 Serie=item.show)
                        except:
                            pass

                    else:
                        import xbmcgui
                        ventana_error = xbmcgui.Dialog()
                        ok = ventana_error.ok("plugin", "Nessun File Da Riprodurre")
                else:
                    plugintools.log(
                        "streamondemand-pureita.navigation.py No channel 'play' method, executing core method")

                    # FIXME: Este error ha que tratarlo de otra manera, por al dar a volver sin ver el vídeo falla
                    # Mejor hacer el play desde la ventana
                    try:
                        xbmctools.play_video(channel=item.channel, server=item.server, url=item.url,
                                             category=item.category, title=item.title, thumbnail=item.thumbnail,
                                             plot=item.plot, extra=item.extra, subtitle=item.subtitle,
                                             video_password=item.password, fulltitle=item.fulltitle, Serie=item.show)
                    except:
                        pass

                return []

            elif item.action == "findvideos":
                plugintools.log("navigation.get_next_items findvideos")

                # Si el canal tiene una acción "findvideos" tiene prioridad
                if hasattr(channel, 'findvideos'):
                    plugintools.log("streamondemand-pureita.navigation.py Channel has its own 'findvideos' method")
                    itemlist = channel.findvideos(item)
                else:
                    itemlist = []

                if len(itemlist) == 0:
                    from servers import servertools
                    itemlist = servertools.find_video_items(item)

                if len(itemlist) == 0:
                    itemlist = [Item(title="Nessun video trovato",
                                     thumbnail=os.path.join(plugintools.get_runtime_path(), "resources", "images",
                                                            "thumb_error.png"))]
            # ---------------add_serie_to_library-----------
            elif item.action == "add_serie_to_library":
                plugintools.log("navigation.get_next_items add_serie_to_library")
                from platformcode import library
                import xbmcgui

                # Obtiene el listado desde el que se llamó
                action = item.extra

                # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
                if "###" in item.extra:
                    action = item.extra.split("###")[0]
                    item.extra = item.extra.split("###")[1]

                exec "itemlist = channel." + action + "(item)"

                # Progreso
                pDialog = xbmcgui.DialogProgress()
                ret = pDialog.create('streamondemand-pureita', 'Añadiendo episodios...')
                pDialog.update(0, 'Añadiendo episodio...')
                totalepisodes = len(itemlist)
                plugintools.log("navigation.get_next_items Total Episodios:" + str(totalepisodes))
                i = 0
                errores = 0
                nuevos = 0
                for item in itemlist:
                    i = i + 1
                    pDialog.update(i * 100 / totalepisodes, 'Añadiendo episodio...', item.title)
                    plugintools.log("streamondemand-pureita.navigation.py add_serie_to_library, title=" + item.title)
                    if (pDialog.iscanceled()):
                        return

                    try:
                        # (titulo="",url="",thumbnail="",server="",plot="",canal="",category="Cine",Serie="",verbose=True,accion="strm",pedirnombre=True):
                        # Añade todos menos el que dice "Añadir esta serie..." o "Descargar esta serie..."
                        if item.action != "add_serie_to_library" and item.action != "download_all_episodes":
                            nuevos = nuevos + library.savelibrary(titulo=item.title, url=item.url,
                                                                  thumbnail=item.thumbnail, server=item.server,
                                                                  plot=item.plot, canal=item.channel, category="Series",
                                                                  Serie=item.show.strip(), verbose=False,
                                                                  accion="play_from_library", pedirnombre=False,
                                                                  subtitle=item.subtitle, extra=item.extra)
                    except IOError:
                        import sys
                        for line in sys.exc_info():
                            logger.error("%s" % line)
                        plugintools.log("streamondemand-pureita.navigation.py Error al grabar el archivo " + item.title)
                        errores = errores + 1

                pDialog.close()

                # Actualizacion de la biblioteca
                itemlist = []
                if errores > 0:
                    itemlist.append(
                        Item(title="ERRORE, la serie NON si è aggiunta alla biblioteca o la fatto in modo incompleto"))
                    plugintools.log("navigation.get_next_items No se pudo añadir " + str(errores) + " episodios")
                else:
                    itemlist.append(Item(title="La serie è stata aggiunta alla biblioteca"))
                    plugintools.log("navigation.get_next_items Ningún error al añadir " + str(errores) + " episodios")

                # FIXME:jesus Comentado porque no funciona bien en todas las versiones de XBMC
                # library.update(totalepisodes,errores,nuevos)
                # xbmctools.renderItems(itemlist, params, url, category)

                # Lista con series para actualizar
                from core import config
                nombre_fichero_config_canal = os.path.join(config.get_library_path(), "series.xml")
                if not os.path.exists(nombre_fichero_config_canal):
                    nombre_fichero_config_canal = os.path.join(config.get_data_path(), "series.xml")

                plugintools.log("nombre_fichero_config_canal=" + nombre_fichero_config_canal)
                if not os.path.exists(nombre_fichero_config_canal):
                    f = open(nombre_fichero_config_canal, "w")
                else:
                    f = open(nombre_fichero_config_canal, "r")
                    contenido = f.read()
                    f.close()
                    f = open(nombre_fichero_config_canal, "w")
                    f.write(contenido)
                from platformcode import library
                f.write(library.title_to_folder_name(item.show) + "," + item.url + "," + item.channel + "\n")
                f.close();
                return itemlist
            # --------------------------------------------------------------------
            elif item.action == "download_all_episodes":
                plugintools.log("navigation.get_next_items download_all_episodes")
                download_all_episodes(item, channel)
            # ---------------------------------------------------------------------
            else:

                if item.action == "search":
                    tecleado = plugintools.keyboard_input()
                    if tecleado != "":
                        tecleado = tecleado.replace(" ", "+")
                        itemlist = channel.search(item, tecleado)
                elif item.channel == "novedades" and item.action == "mainlist":
                    itemlist = channel.mainlist(item, "bannermenu")
                elif item.channel == "buscador" and item.action == "mainlist":
                    itemlist = channel.mainlist(item, "bannermenu")
                else:
                    exec "itemlist = channel." + item.action + "(item)"

                for loaded_item in itemlist:

                    if loaded_item.thumbnail == "":
                        if loaded_item.folder:
                            loaded_item.thumbnail = os.path.join(plugintools.get_runtime_path(), "resources", "images",
                                                                 "thumb_folder.png")
                        else:
                            loaded_item.thumbnail = os.path.join(plugintools.get_runtime_path(), "resources", "images",
                                                                 "thumb_nofolder.png")

                if len(itemlist) == 0:
                    itemlist = [Item(title="Nessun Elemento Da Visualizzare",
                                     thumbnail=os.path.join(plugintools.get_runtime_path(), "resources", "images",
                                                            "thumb_error.png"))]

    except:
        import traceback
        plugintools.log("navigation.get_next_items " + traceback.format_exc())
        itemlist = [Item(title="Rimozione Effettuata - Riavviare",
                         thumbnail=os.path.join(plugintools.get_runtime_path(), "resources", "images",
                                                "thumb_error.png"))]

    return itemlist


def get_window_for_item(item):
    plugintools.log("navigation.get_window_for_item item.channel=" + item.channel + ", item.action==" + item.action)
    from core import config

    skin_selector = config.get_setting("skin_selector")
    if skin_selector == "":
        skin_selector = "0"

    if skin_selector == "0":

        # El menú principal va con banners + titulo
        if item.channel == "navigation" or (item.channel == "novedades" and item.action == "mainlist") or (
                item.channel == "buscador" and item.action == "mainlist") or (
                item.channel == "channelselector" and item.action == "channeltypes"):
            import window_channels
            window = window_channels.ChannelWindow("banner.xml", plugintools.get_runtime_path(), 'Default', '1080i')

        # El listado de canales va con banners sin título
        elif item.channel == "channelselector" and item.action == "listchannels":
            import window_channels
            window = window_channels.ChannelWindow("channels.xml", plugintools.get_runtime_path(), 'Default', '1080i')

        # El resto va con el aspecto normal
        else:
            import window_menu
            window = window_menu.MenuWindow("content.xml", plugintools.get_runtime_path(), 'Default', '1080i')

    if skin_selector == "1":

        # El menú principal va con banners + titulo
        if item.channel == "navigation" or (item.channel == "novedades" and item.action == "mainlist") or (
                item.channel == "buscador" and item.action == "mainlist") or (
                item.channel == "channelselector" and item.action == "channeltypes"):
            import window_channels
            window = window_channels.ChannelWindow("banner-1.xml", plugintools.get_runtime_path(), 'Default', '1080i')

        # El listado de canales va con banners sin título
        elif item.channel == "channelselector" and item.action == "listchannels":
            import window_channels
            window = window_channels.ChannelWindow("channels-1.xml", plugintools.get_runtime_path(), 'Default', '1080i')

        # El resto va con el aspecto normal
        else:
            import window_menu
            window = window_menu.MenuWindow("content-1.xml", plugintools.get_runtime_path(), 'Default', '1080i')

    return window


# Parse XBMC params - based on script.module.parsedom addon    
def get_params():
    plugintools.log("get_params")

    param_string = sys.argv[2]

    plugintools.log("get_params " + str(param_string))

    commands = {}

    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')

        for command in split_commands:
            plugintools.log("get_params command=" + str(command))
            if len(command) > 0:
                if "=" in command:
                    split_command = command.split('=')
                    key = split_command[0]
                    value = split_command[1]  # urllib.unquote_plus()
                    commands[key] = value
                else:
                    commands[command] = ""

    plugintools.log("get_params " + repr(commands))
    return commands


# Extract parameters from sys.argv
def extract_parameters():
    plugintools.log("streamondemand-pureita.navigation.py extract_parameters")
    # Imprime en el log los parámetros de entrada
    plugintools.log("streamondemand-pureita.navigation.py sys.argv=%s" % str(sys.argv))

    # Crea el diccionario de parametros
    # params = dict()
    # if len(sys.argv)>=2 and len(sys.argv[2])>0:
    #    params = dict(part.split('=') for part in sys.argv[ 2 ][ 1: ].split('&'))
    params = get_params()
    plugintools.log("streamondemand-pureita.navigation.py params=%s" % str(params))

    if (params.has_key("channel")):
        channel = urllib.unquote_plus(params.get("channel"))
    else:
        channel = ''

    # Extrae la url de la página
    if (params.has_key("url")):
        url = urllib.unquote_plus(params.get("url"))
    else:
        url = ''

    # Extrae la accion
    if (params.has_key("action")):
        action = params.get("action")
    else:
        action = "selectchannel"

    # Extrae el server
    if (params.has_key("server")):
        server = params.get("server")
    else:
        server = ""

    # Extrae la categoria
    if (params.has_key("category")):
        category = urllib.unquote_plus(params.get("category"))
    else:
        if params.has_key("channel"):
            category = params.get("channel")
        else:
            category = ""

    # Extrae el título de la serie
    if (params.has_key("show")):
        show = params.get("show")
    else:
        show = ""

    # Extrae el título del video
    if params.has_key("title"):
        title = urllib.unquote_plus(params.get("title"))
    else:
        title = ""

    # Extrae el título del video
    if params.has_key("fulltitle"):
        fulltitle = urllib.unquote_plus(params.get("fulltitle"))
    else:
        fulltitle = ""

    if params.has_key("thumbnail"):
        thumbnail = urllib.unquote_plus(params.get("thumbnail"))
    else:
        thumbnail = ""

    if params.has_key("fanart"):
        fanart = urllib.unquote_plus(params.get("fanart"))
    else:
        fanart = ""

    if params.has_key("plot"):
        plot = urllib.unquote_plus(params.get("plot"))
    else:
        plot = ""

    if params.has_key("extradata"):
        extra = urllib.unquote_plus(params.get("extradata"))
    else:
        extra = ""

    if params.has_key("subtitle"):
        subtitle = urllib.unquote_plus(params.get("subtitle"))
    else:
        subtitle = ""

    if params.has_key("viewmode"):
        viewmode = urllib.unquote_plus(params.get("viewmode"))
    else:
        viewmode = ""

    if params.has_key("password"):
        password = urllib.unquote_plus(params.get("password"))
    else:
        password = ""

    if params.has_key("show"):
        show = urllib.unquote_plus(params.get("show"))
    else:
        if params.has_key("Serie"):
            show = urllib.unquote_plus(params.get("Serie"))
        else:
            show = ""

    return params, fanart, channel, title, fulltitle, url, thumbnail, plot, action, server, extra, subtitle, viewmode, category, show, password


def episodio_ya_descargado(show_title, episode_title):
    ficheros = os.listdir(".")

    for fichero in ficheros:
        # plugintools.log("fichero="+fichero)
        # if fichero.lower().startswith(show_title.lower()) and scrapertools.find_single_match(fichero,"(\d+x\d+)")==episode_title:
        if fichero.lower().startswith(show_title.lower()) and episode_title in fichero:
            plugintools.log("encontrado!")
            return True

    return False


def download_all_episodes(item, channel, first_episode="", preferred_server="vidspot", filter_language=""):
    plugintools.log("streamondemand-pureita.navigation.py download_all_episodes, show=" + item.show)
    show_title = item.show

    # Obtiene el listado desde el que se llamó
    action = item.extra

    # Esta marca es porque el item tiene algo más aparte en el atributo "extra"
    if "###" in item.extra:
        action = item.extra.split("###")[0]
        item.extra = item.extra.split("###")[1]

    exec "episode_itemlist = channel." + action + "(item)"

    # Ordena los episodios para que funcione el filtro de first_episode
    episode_itemlist = sorted(episode_itemlist, key=lambda Item: Item.title)

    from servers import servertools
    from core import downloadtools

    # Para cada episodio
    if first_episode == "":
        empezar = True
    else:
        empezar = False

    for episode_item in episode_itemlist:
        if episode_item.action == "add_serie_to_library" or episode_item.action == "download_all_episodes":
            continue

        try:
            plugintools.log("streamondemand-pureita.navigation.py download_all_episodes, episode=" + episode_item.title)
            # episode_title = scrapertools.get_match(episode_item.title,"(\d+x\d+)")
            episode_title = episode_item.title
            episode_title = re.sub(r"\[COLOR [^]]*\]", "", episode_title)
            episode_title = re.sub(r"\[/COLOR\]", "", episode_title)
            plugintools.log("streamondemand-pureita.navigation.py download_all_episodes, episode=" + episode_title)
        except:
            import traceback
            plugintools.log(traceback.format_exc())
            continue

        if first_episode != "" and episode_title == first_episode:
            empezar = True

        if episodio_ya_descargado(show_title, episode_title):
            continue

        if not empezar:
            continue

        # Extrae los mirrors
        try:
            # mirrors_itemlist = channel.findvideos(episode_item)
            exec "mirrors_itemlist = channel." + episode_item.action + "(episode_item)"
        except:
            mirrors_itemlist = servertools.find_video_items(episode_item)
        print mirrors_itemlist

        descargado = False

        for mirror_item in mirrors_itemlist:
            plugintools.log("streamondemand-pureita.navigation.py download_all_episodes, mirror=" + mirror_item.title)

            if hasattr(channel, 'play'):
                video_items = channel.play(mirror_item)
            else:
                video_items = [mirror_item]

            if len(video_items) > 0:
                video_item = video_items[0]

                # Comprueba que esté disponible
                video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing(video_item.server,
                                                                                        video_item.url,
                                                                                        video_password="",
                                                                                        muestra_dialogo=False)

                # Lo añade a la lista de descargas
                if puedes:
                    plugintools.log(
                        "streamondemand-pureita.navigation.py download_all_episodes, downloading mirror started...")
                    # El vídeo de más calidad es el último
                    # mediaurl = video_urls[len(video_urls)-1][1]
                    devuelve = downloadtools.downloadbest(video_urls,
                                                          show_title + " " + episode_title + " [" + video_item.server + "]",
                                                          continuar=False)
                    if devuelve == 0:
                        plugintools.log("streamondemand-pureita.navigation.py download_all_episodes, download ok")
                        descargado = True
                        break
                    elif devuelve == -1:
                        try:
                            import xbmcgui
                            advertencia = xbmcgui.Dialog()
                            resultado = advertencia.ok("plugin", "Download interrotto")
                        except:
                            pass
                        return
                    else:
                        plugintools.log(
                            "streamondemand-pureita.navigation.py download_all_episodes, download error, try another mirror")
                        continue

                else:
                    plugintools.log(
                        "streamondemand-pureita.navigation.py download_all_episodes, downloading mirror not available... trying next")

        if not descargado:
            plugintools.log(
                "streamondemand-pureita.navigation.py download_all_episodes, EPISODIO NO DESCARGADO " + episode_title)
        return itemlist
