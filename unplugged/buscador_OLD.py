# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------

import Queue
import glob
import imp
import os
import re
import threading
import time

from core import channeltools
from core import config
from core import logger
from core.item import Item
from lib.fuzzywuzzy import fuzz

__channel__ = "buscador"

logger.info("streamondemand-pureita-master.channels.buscador init")

DEBUG = config.get_setting("debug")

TIMEOUT_TOTAL = 90


def isGeneric():
    return True


def mainlist(item, preferred_thumbnail="squares"):
    logger.info("streamondemand-pureita-master.channels.buscador mainlist")

    itemlist = [
        Item(channel=__channel__,
             action="search",
             category="film",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/bannermenu/banner_search_violaP.png",
             title="[COLOR yellow]Nuova ricerca film...[/COLOR]"),
        Item(channel=__channel__,
             action="search",
             category="serie",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/bannermenu/banner_search_violaP.png",
             title="[COLOR yellow]Nuova ricerca serie tv...[/COLOR]"),
    ]

    saved_searches_list = get_saved_searches(item.channel)

    for saved_search_text in saved_searches_list:
        itemlist.append(
                Item(channel=__channel__,
                     action="do_search",
                     title=' "' + saved_search_text + '"',
                     extra=saved_search_text))

    if len(saved_searches_list) > 0:
        itemlist.append(
                Item(channel=__channel__,
                     action="clear_saved_searches",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/bannermenu/banner_deletesearch_violaP.png",
                     title="[COLOR red]Elimina cronologia ricerche[/COLOR]"))

    return itemlist


# Al llamar a esta función, el sistema pedirá primero el texto a buscar
# y lo pasará en el parámetro "tecleado"
def search(item, tecleado):
    logger.info("streamondemand-pureita-master.channels.buscador search")

    if tecleado != "":
        save_search(item.channel, tecleado)

    item.extra = tecleado
    return do_search(item)


# Esta es la función que realmente realiza la búsqueda
def do_search(item):
    logger.info("streamondemand-pureita-master.channels.buscador do_search")

    tecleado = item.extra
    mostra = tecleado.replace("+", " ")

    itemlist = []

    channels_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')
    logger.info("streamondemand-pureita-master.channels.buscador channels_path=" + channels_path)

    channel_language = config.get_setting("channel_language")
    logger.info("streamondemand-pureita-master.channels.buscador channel_language=" + channel_language)
    if channel_language == "":
        channel_language = "all"
        logger.info("streamondemand-pureita-master.channels.buscador channel_language=" + channel_language)

    if config.is_xbmc():
        show_dialog = True

    try:
        import xbmcgui
        progreso = xbmcgui.DialogProgressBG()
        progreso.create("Ricerca di " + mostra.title())
    except:
        show_dialog = False

    def worker(infile, queue):
        channel_result_itemlist = []
        try:
            basename_without_extension = os.path.basename(infile)[:-4]
            # http://docs.python.org/library/imp.html?highlight=imp#module-imp
            obj = imp.load_source(basename_without_extension, infile[:-4]+".py")
            logger.info("streamondemand-pureita-master.channels.buscador cargado " + basename_without_extension + " de " + infile)
            channel_result_itemlist.extend(obj.search(Item(extra=item.category), tecleado))
            for local_item in channel_result_itemlist:
                local_item.title = " [COLOR azure] " + local_item.title + " [/COLOR] [COLOR orange]su[/COLOR] [COLOR green]" + basename_without_extension + "[/COLOR]"
                local_item.viewmode = "list"
        except:
            import traceback
            logger.error(traceback.format_exc())
        queue.put(channel_result_itemlist)

    channel_files = glob.glob(channels_path)

    channel_files_tmp = []
    for infile in channel_files:

        basename_without_extension = os.path.basename(infile)[:-4]

        channel_parameters = channeltools.get_channel_parameters(basename_without_extension)

        # No busca si es un canal inactivo
        if channel_parameters["active"] != "true":
            continue

        # No busca si es un canal excluido de la busqueda global
        if channel_parameters["include_in_global_search"] != "true":
            continue

        # No busca si es un canal para adultos, y el modo adulto está desactivado
        if channel_parameters["adult"] == "true" and config.get_setting("adult_mode") == "false":
            continue

        # No busca si el canal es en un idioma filtrado
        if channel_language != "all" and channel_parameters["language"] != channel_language:
            continue

        channel_files_tmp.append(infile)

    channel_files = channel_files_tmp

    result = Queue.Queue()
    threads = [threading.Thread(target=worker, args=(infile, result)) for infile in channel_files]

    start_time = int(time.time())

    for t in threads:
        t.daemon = True  # NOTE: setting dameon to True allows the main thread to exit even if there are threads still running
        t.start()

    number_of_channels = len(channel_files)
    completed_channels = 0
    while completed_channels < number_of_channels:

        delta_time = int(time.time()) - start_time
        if len(itemlist) <= 0:
            timeout = None  # No result so far,lets the thread to continue working until a result is returned
        elif delta_time >= TIMEOUT_TOTAL:
            break  # At least a result matching the searched title has been found, lets stop the search
        else:
            timeout = TIMEOUT_TOTAL - delta_time  # Still time to gather other results

        if show_dialog:
            progreso.update(completed_channels * 100 / number_of_channels)

        try:
            result_itemlist = result.get(timeout=timeout)
            completed_channels += 1
        except:
            # Expired timeout raise an exception
            break

        for item in result_itemlist:
            title = item.fulltitle

            # Clean up a bit the returned title to improve the fuzzy matching
            title = re.sub(r'\(.*\)', '', title)  # Anything within ()
            title = re.sub(r'\[.*\]', '', title)  # Anything within []

            # Check if the found title fuzzy matches the searched one
            if fuzz.WRatio(mostra, title) > 85: itemlist.append(item)

    if show_dialog:
        progreso.close()

    itemlist = sorted(itemlist, key=lambda item: item.fulltitle)

    return itemlist


def save_search(channel, text):
    saved_searches_limit = (10, 20, 30, 40,)[int(config.get_setting("saved_searches_limit"))]

    if os.path.exists(os.path.join(config.get_data_path(), "saved_searches.txt")):
        f = open(os.path.join(config.get_data_path(), "saved_searches.txt"), "r")
        saved_searches_list = f.readlines()
        f.close()
    else:
        saved_searches_list = []

    saved_searches_list.append(text)

    if len(saved_searches_list) >= saved_searches_limit:
        # Corta la lista por el principio, eliminando los más recientes
        saved_searches_list = saved_searches_list[-saved_searches_limit:]

    f = open(os.path.join(config.get_data_path(), "saved_searches.txt"), "w")
    for saved_search in saved_searches_list:
        f.write(saved_search + "\n")
    f.close()


def clear_saved_searches(item):
    f = open(os.path.join(config.get_data_path(), "saved_searches.txt"), "w")
    f.write("")
    f.close()


def get_saved_searches(channel):
    if os.path.exists(os.path.join(config.get_data_path(), "saved_searches.txt")):
        f = open(os.path.join(config.get_data_path(), "saved_searches.txt"), "r")
        saved_searches_list = f.readlines()
        f.close()
    else:
        saved_searches_list = []

    # Invierte la lista, para que el último buscado salga el primero
    saved_searches_list.reverse()

    trimmed = []
    for saved_search_text in saved_searches_list:
        trimmed.append(saved_search_text.strip())

    return trimmed
