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

UPDATE_URL_IDX, VERSION_IDX = xrange(0, 2)

remote_url = "https://raw.githubusercontent.com/orione7/plugin.video.streamondemand-pureita/master/channels/"
local_folder = os.path.join(config.get_runtime_path(), "channels")


### Procedures
def update_channels():
    with open(os.path.join(local_folder, "channelslist.xml"), 'rb') as f:
        xml = f.read()
    local_dict = read_channels_list(xml)

    xml = scrapertools.cache_page(remote_url + "channelslist.xml")
    remote_dict = read_channels_list(xml)

    # ----------------------------
    import xbmcgui
    progress = xbmcgui.DialogProgressBG()
    progress.create("Update channels list")
    # ----------------------------

    for index, channel_id in enumerate(remote_dict.iterkeys()):
        # ----------------------------
        percentage = index * 100 / len(remote_dict)
        # ----------------------------
        if channel_id not in local_dict or remote_dict[channel_id][VERSION_IDX] > local_dict[channel_id][VERSION_IDX]:
            data = scrapertools.cache_page(remote_dict[channel_id][UPDATE_URL_IDX])

            with open(os.path.join(local_folder, channel_id + ".py"), 'wb') as f:
                f.write(data)
            # ----------------------------
            progress.update(percentage, ' Update channel: ' + channel_id)
            # ----------------------------

    for channel_id in set(local_dict.keys()) - set(remote_dict.keys()):
        os.remove(os.path.join(local_folder, channel_id + ".py"))

    with open(os.path.join(local_folder, "channelslist.xml"), 'wb') as f:
        f.write(xml)

    # ----------------------------
    progress.close()
    # ----------------------------


def read_channels_list(xml):
    ret = {}
    patron = r"<channel>\s*<id>([^<]+)</id>.*?<update_url>([^<]+)</update_url>.*?<version>([^<]+)</version>.*?</channel>"
    for channel_id, update_url, version in re.compile(patron, re.DOTALL).findall(xml):
        ret[channel_id] = [update_url, int(version)]

    return ret


### Run
Thread(target=update_channels).start()

