# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-pureita 5.4.1
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of streamondemand-pureita .
#
# streamondemand is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand .  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------
# platformtools
# ------------------------------------------------------------
# Herramientas responsables de adaptar los diferentes 
# cuadros de dialogo a una plataforma en concreto,
# en este caso Kodi.
# version 2.0
# ------------------------------------------------------------

import sys

import xbmc
import xbmcgui

from core import config


def dialog_ok(heading, line1, line2="", line3=""):
    dialog = xbmcgui.Dialog()
    return dialog.ok(heading, line1, line2, line3)


def dialog_notification(heading, message, icon=0, time=5000, sound=True):
    dialog = xbmcgui.Dialog()
    l_icono = xbmcgui.NOTIFICATION_INFO, xbmcgui.NOTIFICATION_WARNING, xbmcgui.NOTIFICATION_ERROR
    dialog.notification(heading, message, l_icono[icon], time, sound)


def dialog_yesno(heading, line1, line2="", line3="", nolabel="No", yeslabel="Si", autoclose=""):
    dialog = xbmcgui.Dialog()
    if autoclose:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel, autoclose)
    else:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def dialog_select(heading, _list):
    return xbmcgui.Dialog().select(heading, _list)


def dialog_progress(heading, line1, line2="", line3=""):
    dialog = xbmcgui.DialogProgress()
    dialog.create(heading, line1, line2, line3)
    return dialog


def dialog_progress_bg(heading, message=""):
    dialog = xbmcgui.DialogProgressBG()
    dialog.create(heading, message)
    return dialog


def dialog_input(default="", heading="", hidden=False):
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    else:
        return None


def dialog_numeric(_type, heading, default=""):
    dialog = xbmcgui.Dialog()
    dialog.numeric(_type, heading, default)
    return dialog


def itemlist_refresh():
    xbmc.executebuiltin("Container.Refresh")


def itemlist_update(item):
    xbmc.executebuiltin("Container.Update(" + sys.argv[0] + "?" + item.tourl() + ")")


def render_items(itemlist, parentitem):
    # Por implementar (traer de xbmctools)
    pass


def is_playing():
    return xbmc.Player().isPlaying()


def play_video(item):
    # Por implementar (traer de xbmctools)
    pass


def show_channel_settings(list_controls=None, dict_values=None, caption="", callback=None, item=None,
                          custom_button=None):
    """
    Muestra un cuadro de configuracion personalizado para cada canal y guarda los datos al cerrarlo.
    
    Parametros: ver descripcion en xbmc_config_menu.SettingsWindow
    @param list_controls: lista de elementos a mostrar en la ventana.
    @type list_controls: list
    @param dict_values: valores que tienen la lista de elementos.
    @type dict_values: dict
    @param caption: titulo de la ventana
    @type caption: str
    @param callback: función que se llama tras cerrarse la ventana.
    @type callback: str
    @param item: item para el que se muestra la ventana de configuración.
    @type item: Item
    @param custom_button: botón personalizado, que se muestra junto a "OK" y "Cancelar".
    @type custom_button: dict

    @return: devuelve la ventana con los elementos
    @rtype: SettingsWindow
    """
    from xbmc_config_menu import SettingsWindow
    return SettingsWindow("ChannelSettings.xml", config.get_runtime_path())\
        .start(list_controls=list_controls, dict_values=dict_values, title=caption, callback=callback, item=item,
                 custom_button=custom_button)


def show_video_info(data, caption="", callback=None, item=None):
    """
    Muestra una ventana con la info del vídeo. Opcionalmente se puede indicar el titulo de la ventana mendiante
    el argumento 'caption'.

    Si se pasa un item como argumento 'data' usa el scrapper Tmdb para buscar la info del vídeo
        En caso de peliculas:
            Coge el titulo de los siguientes campos (en este orden)
                  1. contentTitle (este tiene prioridad 1)
                  2. fulltitle (este tiene prioridad 2)
                  3. title (este tiene prioridad 3)
            El primero que contenga "algo" lo interpreta como el titulo (es importante asegurarse que el titulo este en
            su sitio)

        En caso de series:
            1. Busca la temporada y episodio en los campos contentSeason y contentEpisodeNumber
            2. Intenta Sacarlo del titulo del video (formato: 1x01)

            Aqui hay dos opciones posibles:
                  1. Tenemos Temporada y episodio
                    Muestra la información del capitulo concreto
                    Se puede navegar con las flechas para cambiar de temporada / eìsodio
                    Flecha Arriba: Aumentar temporada
                    Flecha Abajo: Disminuir temporada
                    Flecha Derecha: Aumentar eìsodio
                    Flecha Izquierda: Disminuir eìsodio
                  2. NO Tenemos Temporada y episodio
                    En este caso muestra la informacion generica de la serie

    Si se pasa como argumento 'data' un dict() muestra en la ventana directamente la información pasada (sin usar el
    scrapper)
        Formato:
            En caso de peliculas:
                dict({
                         "type"           : "movie",
                         "title"          : "Titulo de la pelicula",
                         "original_title" : "Titulo original de la pelicula",
                         "date"           : "Fecha de lanzamiento",
                         "language"       : "Idioma original de la pelicula",
                         "rating"         : "Puntuacion de la pelicula",
                         "genres"         : "Generos de la pelicula",
                         "thumbnail"      : "Ruta para el thumbnail",
                         "fanart"         : "Ruta para el fanart",
                         "overview"       : "Sinopsis de la pelicula"
                      }
            En caso de series:
                dict({
                         "type"           : "tv",
                         "title"          : "Titulo de la serie",
                         "episode_title"  : "Titulo del episodio",
                         "date"           : "Fecha de emision",
                         "language"       : "Idioma original de la serie",
                         "rating"         : "Puntuacion de la serie",
                         "genres"         : "Generos de la serie",
                         "thumbnail"      : "Ruta para el thumbnail",
                         "fanart"         : "Ruta para el fanart",
                         "overview"       : "Sinopsis de la del episodio o de la serie",
                         "seasons"        : "Numero de Temporadas",
                         "season"         : "Temporada",
                         "episodes"       : "Numero de episodios de la temporada",
                         "episode"        : "Episodio"
                      }
    Si se pasa como argumento 'data' un listado de dict() con la estructura anterior, muestra los botones 'Anterior' y
    'Siguiente' para ir recorriendo la lista. Ademas muestra los botones 'Aceptar' y 'Cancelar' que llamaran a la
    funcion 'callback' del canal desde donde se realiza la llamada pasandole como parametros el elemento actual (dict())
    o None respectivamente.

    @param data: información para obtener datos del scraper.
    @type data: item, dict, list(dict)
    @param caption: titulo de la ventana.
    @type caption: str
    @param callback: función que se llama después de cerrarse la ventana de información
    @type callback: str
    @param item: elemento del que se va a mostrar la ventana de información
    @type item: Item
    """

    from xbmc_info_window import InfoWindow
    return InfoWindow("InfoWindow.xml", config.get_runtime_path()).Start(data, caption=caption, callback=callback,
                                                                         item=item)
