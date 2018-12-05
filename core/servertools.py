# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of streamondemand 5.
#
# streamondemand 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand 5.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
# Server management
# ------------------------------------------------------------

import os

from core import config
from core import logger
from core import scrapertools


# Funciónn genérica para encontrar ídeos en una página
def find_video_items(item=None, data=None, channel=""):
    logger.info("streamondemand-pureita-master.core.servertools find_video_items")

    # Descarga la página
    if data is None:
        from core import scrapertools
        data = scrapertools.cache_page(item.url)
        # logger.info(data)

    # Busca los enlaces a los videos
    from core.item import Item
    listavideos = findvideos(data)

    if item is None:
        item = Item()

    itemlist = []
    for video in listavideos:
        # scrapedtitle = " [ "+video[2]+" ] "
        # DrZ3r0
        scrapedtitle = item.title.strip() + " - " + video[0].strip()
        scrapedurl = video[1]
        server = video[2]
        # DrZ3r0
        thumbnail = item.thumbnail
        if not thumbnail:
            if get_server_parameters(server)["thumbnail"]:
                thumbnail = get_server_parameters(server)["thumbnail"]
            else:
                thumbnail = "http://media.tvalacarta.info/servers/server_"+server+".png"
        
        itemlist.append( Item(channel=item.channel, title=scrapedtitle, action="play", server=server, url=scrapedurl, thumbnail=thumbnail, fulltitle=item.fulltitle, show=item.show, plot=item.plot, parentContent=item, folder=False) )

    return itemlist


def guess_server_thumbnail(title):
    logger.info("streamondemand-pureita-master.core.servertools guess_server_thumbnail title=" + title)

    lowcase_title = title.lower()

    if "netu" in lowcase_title:
        logger.info("streamondemand-pureita-master.core.servertools guess_server_thumbnail caso especial netutv")
        return "http://media.tvalacarta.info/servers/server_netutv.png"

    if "ul.to" in lowcase_title:
        logger.info("streamondemand-pureita-master.core.servertools guess_server_thumbnail caso especial ul.to")
        return "http://media.tvalacarta.info/servers/server_uploadedto.png"

    if "waaw" in lowcase_title:
        logger.info("streamondemand-pureita-master.core.servertools guess_server_thumbnail caso especial waaw")
        return "http://media.tvalacarta.info/servers/server_waaw.png"

    if "streamin" in lowcase_title:
        logger.info("streamondemand-pureita-master.core.servertools guess_server_thumbnail caso especial streamin")
        return "http://media.tvalacarta.info/servers/server_streaminto.png"

    servers = get_servers_list()
    for serverid in servers:
        if serverid in lowcase_title:
            logger.info("streamondemand-pureita-master.core.servertools guess_server_thumbnail encontrado " + serverid)
            return "http://media.tvalacarta.info/servers/server_" + serverid + ".png"

    return ""


def findvideosbyserver(data, serverid):
    logger.info("streamondemand-pureita-master.core.servertools findvideosbyserver")
    encontrados = set()
    devuelve = []
    try:
        exec "from servers import " + serverid
        exec "devuelve.extend(" + serverid + ".find_videos(data))"
    except ImportError:
        logger.info("Non esiste il connettore per #" + serverid + "#")
        # import traceback
        # logger.info(traceback.format_exc())
    except:
        logger.info("Errore del connettore #" + serverid + "#")
        import traceback
        logger.info(traceback.format_exc())

    return devuelve


def findvideos(data, skip=False):
    logger.info("streamondemand-pureita-master.core.servertools findvideos")  # en #"+data+"#")
    encontrados = set()
    devuelve = []

    # Ejecuta el findvideos en cada servidor
    server_list = get_servers_list()
    for serverid in server_list:
        try:
            # Sustituye el código por otro "Plex compatible"
            # exec "from servers import "+serverid
            # exec "devuelve.extend("+serverid+".find_videos(data))"
            servers_module = __import__("servers." + serverid)
            server_module = getattr(servers_module, serverid)
            result = server_module.find_videos(data)
            if result and skip: return result
            devuelve.extend(result)
        except ImportError:
            logger.info("No existe conector para #" + serverid + "#")
            # import traceback
            # logger.info(traceback.format_exc())
        except:
            logger.info("Error en el conector #" + serverid + "#")
            import traceback
            logger.info(traceback.format_exc())

    return devuelve


def get_video_urls(server, url):
    '''
    servers_module = __import__("servers."+server)
    server_module = getattr(servers_module,server)
    return server_module.get_video_url( page_url=url)
    '''

    video_urls, puede, motivo = resolve_video_urls_for_playing(server, url)
    return video_urls


def get_channel_module(channel_name):
    if not "." in channel_name:
        channel_module = __import__('channels.%s' % channel_name, None, None, ["channels.%s" % channel_name])
    else:
        channel_module = __import__(channel_name, None, None, [channel_name])
    return channel_module


def get_server_from_url(url):
    encontrado = findvideos(url, True)
    if len(encontrado) > 0:
        devuelve = encontrado[0][2]
    else:
        devuelve = "directo"

    return devuelve


def resolve_video_urls_for_playing(server, url, video_password="", muestra_dialogo=False):
    logger.info("streamondemand-pureita-master.core.servertools resolve_video_urls_for_playing, server=" + server + ", url=" + url)
    video_urls = []
    torrent = False

    server = server.lower()

    # Si el vídeo es "directo", no hay que buscar más
    if server == "directo" or server == "local":
        logger.info("streamondemand-pureita-master.core.servertools server=directo, la url es la buena")

        try:
            import urlparse
            parsed_url = urlparse.urlparse(url)
            logger.info("parsed_url=" + str(parsed_url))
            extension = parsed_url.path[-4:]
        except:
            extension = url[-4:]

        video_urls = [["%s [%s]" % (extension, server), url]]
        return video_urls, True, ""

    # Averigua las URL de los vídeos
    else:

        # Carga el conector
        try:
            # Muestra un diágo de progreso
            if muestra_dialogo:
                from platformcode import platformtools
                progreso = platformtools.dialog_progress("StreamOnDemand PureITA", "Connessione con " + server)
            server_parameters = get_server_parameters(server)

            # Cuenta las opciones disponibles, para calcular el porcentaje
            opciones = []
            if server_parameters["free"] == "true":
                opciones.append("free")
            opciones.extend([premium for premium in server_parameters["premium"] if
                             config.get_setting(premium + "premium") == "true"])
            logger.info("streamondemand-pureita-master.core.servertools opciones disponibles para " + server + ": " + str(
                len(opciones)) + " " + str(opciones))

            # Sustituye el código por otro "Plex compatible"
            # exec "from servers import "+server+" as server_connector"
            servers_module = __import__("servers." + server)
            server_connector = getattr(servers_module, server)

            logger.info("streamondemand-pureita-master.core.servertools servidor de " + server + " importado")

            # Si tiene una función para ver si el vídeo existe, lo comprueba ahora
            if hasattr(server_connector, 'test_video_exists'):
                logger.info("streamondemand-pureita-master.core.servertools invocando a " + server + ".test_video_exists")
                puedes, motivo = server_connector.test_video_exists(page_url=url)

                # Si la funcion dice que no existe, fin
                if not puedes:
                    logger.info("streamondemand-pureita-master.core.servertools test_video_exists dice que el video no existe")
                    if muestra_dialogo: progreso.close()
                    return video_urls, puedes, motivo
                else:
                    logger.info("streamondemand-pureita-master.core.servertools test_video_exists dice que el video SI existe")

            # Obtiene enlaces free
            if server_parameters["free"] == "true":
                if muestra_dialogo:
                    progreso.update((100 / len(opciones)) * opciones.index("free"), "Connessione con " + server)

                logger.info("streamondemand-pureita-master.core.servertools invocando a " + server + ".get_video_url")
                video_urls = server_connector.get_video_url(page_url=url, video_password=video_password)

                # Si no se encuentran vídeos en modo free, es porque el vídeo no existe
                if len(video_urls) == 0:
                    if muestra_dialogo: progreso.close()
                    return video_urls, False, "Non trovo il video su " + server

            # Obtiene enlaces para las diferentes opciones premium
            error_message = []
            for premium in server_parameters["premium"]:
                if config.get_setting(premium + "premium") == "true":
                    if muestra_dialogo:
                        progreso.update((100 / len(opciones)) * opciones.index(premium), "Connessione con " + premium)
                    exec "from servers import " + premium + " as premium_conector"
                    if premium == "realdebrid":
                        debrid_urls = premium_conector.get_video_url(page_url=url, premium=True,
                                                                     video_password=video_password)
                        if not "REAL-DEBRID:" in debrid_urls[0][0]:
                            video_urls.extend(debrid_urls)
                        else:
                            error_message.append(debrid_urls[0][0])
                    elif premium == "alldebrid":
                        alldebrid_urls = premium_conector.get_video_url(page_url=url, premium=True,
                                                                        user=config.get_setting(premium + "user"),
                                                                        password=config.get_setting(
                                                                            premium + "password"),
                                                                        video_password=video_password)
                        if not "Alldebrid:" in alldebrid_urls[0][0]:
                            video_urls.extend(alldebrid_urls)
                        else:
                            error_message.append(alldebrid_urls[0][0])
                    else:
                        video_urls.extend(premium_conector.get_video_url(page_url=url, premium=True,
                                                                         user=config.get_setting(premium + "user"),
                                                                         password=config.get_setting(
                                                                             premium + "password"),
                                                                         video_password=video_password))

            if not video_urls and error_message:
                return video_urls, False, " || ".join(error_message)

            if muestra_dialogo:
                progreso.update(100, "Processo terminato")

            # Cierra el diálogo de progreso
            if muestra_dialogo: progreso.close()

            # Llegas hasta aquí y no tienes ningún enlace para ver, así que no vas a poder ver el vídeo
            if len(video_urls) == 0:
                # ¿Cual es el motivo?

                # 1) No existe -> Ya está controlado
                # 2) No tienes alguna de las cuentas premium compatibles

                # Lista de las cuentas que soportan este servidor
                listapremium = []
                for premium in server_parameters["premium"]:
                    listapremium.append(get_server_parameters(premium)["name"])

                return video_urls, False, "Per il video su " + server + " è necessario<br/>un account " + " o ".join(
                    listapremium)

        except:
            if muestra_dialogo: progreso.close()
            import traceback
            logger.info(traceback.format_exc())
            return video_urls, False, "Si è verificato un errore<br/>con il connettore " + server

    return video_urls, True, ""


def is_server_enabled(server):
    try:
        server_parameters = get_server_parameters(server)
        if server_parameters["active"] == "true":
            if not config.get_setting("hidepremium") == "true":
                return True
            else:
                if server_parameters["free"] == "true":
                    return True
                if [premium for premium in server_parameters["premium"] if
                    config.get_setting(premium + "premium") == "true"]:
                    return True
                else:
                    return False
        else:
            return False
    except:
        import traceback
        logger.info(traceback.format_exc())
        return False


def get_server_parameters(server):
    server = scrapertools.find_single_match(server, '([^\.]+)')
    try:
        JSONFile = xml2dict(os.path.join(config.get_runtime_path(), "servers", server + ".xml"))["server"]
        if type(JSONFile["premium"]) == dict: JSONFile["premium"] = JSONFile["premium"]["value"]
        if JSONFile["premium"] == "": JSONFile["premium"] = []
        if type(JSONFile["premium"]) == str and not JSONFile["premium"] == "": JSONFile["premium"] = [
            JSONFile["premium"]]
        return JSONFile
    except:
        logger.info("Error al cargar el servidor: " + server)
        import traceback
        logger.info(traceback.format_exc())
        return {}


def get_servers_list():
    logger.info("streamondemand-pureita-master.core.servertools get_servers_list")
    ServersPath = os.path.join(config.get_runtime_path(), "servers")
    ServerList = {}
    for server in os.listdir(ServersPath):
        if server.endswith(".xml"):
            if is_server_enabled(server):
                server_parameters = get_server_parameters(server)
                ServerList[server_parameters["id"]] = server_parameters

    return ServerList


def xml2dict(file=None, xmldata=None):
    import re, sys, os
    parse = globals().get(sys._getframe().f_code.co_name)

    if xmldata is None and file is None: raise Exception("Non è possibile convertirlo!")
    if xmldata is None:
        if not os.path.exists(file): raise Exception("Il file non esiste!")
        with open(file, "rb") as f:
            xmldata = f.read()

    matches = re.compile("<(?P<tag>[^>]+)>[\n]*[\s]*[\t]*(?P<value>.*?)[\n]*[\s]*[\t]*<\/(?P=tag)\s*>",
                         re.DOTALL).findall(xmldata)

    return_dict = {}
    for tag, value in matches:
        # Si tiene elementos
        if "<" and "</" in value:
            if tag in return_dict:
                if type(return_dict[tag]) == list:
                    return_dict[tag].append(parse(xmldata=value))
                else:
                    return_dict[tag] = [dct[tags[x]]]
                    return_dict[tag].append(parse(xmldata=value))
            else:
                return_dict[tag] = parse(xmldata=value)

        else:
            if tag in return_dict:
                if type(return_dict[tag]) == list:
                    return_dict[tag].append(value)
                else:
                    return_dict[tag] = [return_dict[tag]]
                    return_dict[tag].append(value)
            else:
                return_dict[tag] = value
    return return_dict


def get_server_remote_url(server_name):
    server_parameters = get_server_parameters(server_name)
    remote_server_url = server_parameters["update_url"] + server_name + ".py"
    remote_version_url = server_parameters["update_url"] + server_name + ".xml"

    logger.info("streamondemand-pureita-master.core.servertools remote_server_url=" + remote_server_url)
    logger.info("streamondemand-pureita-master.core.servertools remote_version_url=" + remote_version_url)

    return remote_server_url, remote_version_url


def get_server_local_path(server_name):
    local_server_path = os.path.join(config.get_runtime_path(), 'servers', server_name + ".py")
    local_version_path = os.path.join(config.get_runtime_path(), 'servers', server_name + ".xml")
    local_compiled_path = os.path.join(config.get_runtime_path(), 'servers', server_name + ".pyo")

    logger.info("streamondemand-pureita-master.core.servertools local_servers_path=" + local_server_path)
    logger.info("streamondemand-pureita-master.core.servertools local_version_path=" + local_version_path)
    logger.info("streamondemand-pureita-master.core.servertools local_compiled_path=" + local_compiled_path)

    return local_server_path, local_version_path, local_compiled_path
