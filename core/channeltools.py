# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand-pureita - XBMC Plugin
#------------------------------------------------------------
# channeltools
# Herramientas para trabajar con canales
#------------------------------------------------------------

import os,sys,re,traceback

import config
import logger
import scrapertools

def is_adult(channel_name):
    logger.info("streamondemand-pureita.core.channeltools is_adult channel_name="+channel_name)

    channel_parameters = get_channel_parameters(channel_name)

    return channel_parameters["adult"]=="true"

def get_channel_parameters(channel_name):
    logger.info("streamondemand-pureita.core.channeltools get_channel_parameters channel_name="+channel_name)

    channel_xml = os.path.join( config.get_runtime_path() , 'channels' , channel_name+".xml" )

    if os.path.exists(channel_xml):
        logger.info("streamondemand-pureita.core.channeltools get_channel_parameters "+channel_name+".xml found")

        infile = open( channel_xml , "rb" )
        data = infile.read()
        infile.close();

        # TODO: Pendiente del json :)
        channel_parameters = {}
        channel_parameters["title"] = scrapertools.find_single_match(data,"<name>([^<]*)</name>")
        channel_parameters["channel"] = scrapertools.find_single_match(data,"<id>([^<]*)</id>")
        channel_parameters["active"] = scrapertools.find_single_match(data,"<active>([^<]*)</active>")
        channel_parameters["adult"] = scrapertools.find_single_match(data,"<adult>([^<]*)</adult>")
        channel_parameters["language"] = scrapertools.find_single_match(data,"<language>([^<]*)</language>")
        channel_parameters["thumbnail"] = scrapertools.find_single_match(data,"<thumbnail>([^<]*)</thumbnail>")
        channel_parameters["bannermenu"] = scrapertools.find_single_match(data,"<bannermenu>([^<]*)</bannermenu>")
        channel_parameters["fanart"] = scrapertools.find_single_match(data,"<fanart>([^<]*)</fanart>")
        channel_parameters["include_in_global_search"] = scrapertools.find_single_match(data,"<include_in_global_search>([^<]*)</include_in_global_search>")
        channel_parameters["type"] = "generic"

        category_list = []
        matches = scrapertools.find_multiple_matches(data, "<category>([^<]*)</category>")
        for match in matches:
            category_list.append(match)

        channel_parameters["categories"] = category_list

        logger.info("streamondemand-pureita.core.channeltools get_channel_parameters channel_parameters="+repr(channel_parameters) )

    else:
        logger.info("streamondemand-pureita.core.channeltools get_channel_parameters "+channel_name+".xml NOT found")

        channel_parameters = {}
        channel_parameters["adult"] = "false"

    return channel_parameters
