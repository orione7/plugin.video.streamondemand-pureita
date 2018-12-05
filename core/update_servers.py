# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# update_servers.py
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import os
import re
from threading import Thread

from core import config
from core import scrapertools

DEBUG = config.get_setting("debug")

UPDATE_URL_IDX, ACTIVE_IDX, VERSION_IDX, DATE_IDX, CHANGES_IDX = xrange(0, 5)

remote_url = "https://raw.githubusercontent.com/orione7/plugin.video.streamondemand-pureita/master/servers/"
local_folder = os.path.join(config.get_runtime_path(), "servers")


### Procedures
def update_servers():
    xml = scrapertools.cache_page(remote_url + "serverlist.xml")
    remote_dict = read_servers_list(xml)

    with open(os.path.join(local_folder, "serverlist.xml"), 'rb') as f:
        data = f.read()
    local_dict = read_servers_list(data)

    # ----------------------------
    import xbmcgui
    progress = xbmcgui.DialogProgressBG()
    progress.create("Update servers list")
    # ----------------------------

    for index, server_id in enumerate(remote_dict.iterkeys()):
        # ----------------------------
        percentage = index * 100 / len(remote_dict)
        # ----------------------------
        if server_id not in local_dict or remote_dict[server_id][VERSION_IDX] > local_dict[server_id][VERSION_IDX]:
            data = scrapertools.cache_page(remote_dict[server_id][UPDATE_URL_IDX])

            with open(os.path.join(local_folder, server_id + ".py"), 'wb') as f:
                f.write(data)
            # ----------------------------
            progress.update(percentage, ' Update server: ' + server_id)
            # ----------------------------

    for server_id in set(local_dict.keys()) - set(remote_dict.keys()):
        os.remove(os.path.join(local_folder, server_id + ".py"))

    with open(os.path.join(local_folder, "serverlist.xml"), 'wb') as f:
        f.write(xml)

    # ----------------------------
    progress.close()
    # ----------------------------


def read_servers_list(xml):
    ret = {}
    patron = r'<server>\s*<id>([^<]+)</id>\s*<update_url>([^<]+)</update_url>\s*<active>([^<]+)</active>\s*<version>([^<]+)</version>\s*<date>([^<]+)</date>\s*<changes>([^<]+)</changes>\s*</server>\s*'
    for server_id, update_url, active, version, date, changes in re.compile(patron).findall(xml):
        ret[server_id] = [update_url, active, int(version), date, changes]

    return ret


### Run
Thread(target=update_servers).start()
