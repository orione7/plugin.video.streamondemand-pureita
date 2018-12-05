# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Search in the TMDB (tmdb.org) for movies, persons, etc.
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import hashlib
import os
import re
import time
import urllib
import urllib2

try:
    import json
except:
    import simplejson as json

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from core import logger
from core import config
from core.item import Item
from unicodedata import normalize

__channel__ = "database"
__category__ = "F"
__type__ = "generic"
__title__ = "Database"

DEBUG = config.get_setting("debug")

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_DATA_PATH = xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID).decode("utf-8")
HOME = xbmcgui.Window(10000)

TMDB_URL_BASE = 'http://api.themoviedb.org/3/'
TMDB_KEY = '34142515d9d23817496eeb4ff1d223d0'
TMDB_IMAGES_BASEURL = 'http://image.tmdb.org/t/p/'
INCLUDE_ADULT = 'true' if config.get_setting("enableadultmode") else 'false'
LANGUAGE_ID = 'it'

def Nls(code, default=''):
    local_string = ADDON.getLocalizedString(code)
    if local_string == '': local_string = default
    return local_string.encode('utf-8', 'ignore')

NLS_Search_by_Title = Nls(30980, 'Search by Title')
NLS_Search_by_Person = Nls(30981, 'Search by Person')
NLS_Search_by_Company = Nls(30982, 'Search by Company')
NLS_Now_Playing = Nls(30983, 'Now Playing')
NLS_Popular = Nls(30984, 'Popular')
NLS_Top_Rated = Nls(30985, 'Top Rated')
NLS_Search_by_Collection = Nls(30986, 'Search by Collection')
NLS_List_by_Genre = Nls(30987, 'Genre')
NLS_Search_by_Year = Nls(30988, 'Search by Year')
NLS_Library = Nls(30991, 'Library')
NLS_Next_Page = Nls(30992, 'Next Page')
NLS_Looking_For = Nls(30993, 'Looking for %s...')
NLS_Searching_In = Nls(30994, 'Searching in %s...')
NLS_Found_So_Far = Nls(30995, '%d found so far: %s')

TMDb_genres = {}

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.channels.database mainlist")

    itemlist = []
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s[/COLOR]" % NLS_Now_Playing, action="list_movie", url="movie/now_playing?", plot="1"))
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s[/COLOR]" % NLS_Popular, action="list_movie", url="movie/popular?", plot="1"))
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s[/COLOR]" % NLS_Top_Rated, action="list_movie", url="movie/top_rated?", plot="1"))
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s[/COLOR]" % NLS_List_by_Genre, action="list_genres"))
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s...[/COLOR]" % NLS_Search_by_Title, action="search", url="search_movie_by_title"))
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s...[/COLOR]" % NLS_Search_by_Collection, action="search", url="search_collection_by_name"))
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s...[/COLOR]" % NLS_Search_by_Person, action="search", url="search_person_by_name"))
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s...[/COLOR]" % NLS_Search_by_Year, action="search", url="search_movie_by_year"))
    itemlist.append(Item(channel=__channel__, title="[COLOR azure]%s...[/COLOR]" % NLS_Search_by_Company, action="search", url="search_company_by_name"))

    return itemlist

def list_movie(item):
    logger.info("streamondemand.channels.database list_movie '%s/%s'"%(item.url, item.plot))

    results = [ 0, 0]
    page = int(item.plot)
    itemlist = build_movie_list(item, tmdb_get_data('%spage=%d&' % (item.url, page), results=results))
    if page < results[0]:
        itemlist.append(Item(
            channel=item.channel,
            title="[COLOR orange]%s (%d/%d)[/COLOR]" % (NLS_Next_Page, page * len(itemlist), results[1]),
            action="list_movie",
            url=item.url,
            plot="%d" % (page+1)))

    return itemlist

def list_genres(item):
    logger.info("streamondemand.channels.database list_genres")

    tmdb_genre(1)
    itemlist = []
    for genre_id, genre_name in TMDb_genres.iteritems():
        itemlist.append(Item(channel=item.channel, title=genre_name, action="list_movie", url='genre/%d/movies?' % genre_id, plot="1"))

    return itemlist

# Do not change the name of this function otherwise launcher.py won't create the keyboard dialog required to enter the search terms
def search(item, search_terms):
    if item.url == '': return []

    return globals()[item.url](item, search_terms) if item.url in globals() else []

def search_movie_by_title(item, search_terms):
    logger.info("streamondemand.channels.database search_movie_by_title '%s'"%(search_terms))

    return list_movie(Item(channel=item.channel, url='search/movie?query=%s&' % url_quote_plus(search_terms), plot="1"))

def search_movie_by_year(item, search_terms):
    logger.info("streamondemand.channels.database search_movie_by_year '%s'"%(search_terms))

    year = url_quote_plus(search_terms)
    return list_movie(Item(channel=item.channel, url='discover/movie?primary_release_year=%s&' % year, plot="1")) if len(year) == 4 else []

def search_person_by_name(item, search_terms):
    logger.info("streamondemand.channels.database search_person_by_name '%s'"%(search_terms))

    persons = tmdb_get_data("search/person?query=%s&" % url_quote_plus(search_terms))

    itemlist = []
    for person in persons:
        name = normalize_unicode(tmdb_tag(person, 'name'))
        poster = tmdb_image(person, 'profile_path')
        fanart = ''
        for movie in tmdb_tag(person, 'known_for', []):
            if tmdb_tag_exists(movie, 'backdrop_path'):
                fanart = tmdb_image(movie, 'backdrop_path', 'w1280')
                break

        itemlist.append(Item(
            channel=item.channel,
            action='search_movie_by_person',
            extra=str(tmdb_tag(person, 'id')),
            title=name,
            thumbnail=poster,
            viewmode='list',
            fanart=fanart,
            ))

    return itemlist

def search_movie_by_person(item):
    logger.info("streamondemand.channels.database search_movie_by_person '%s'"%(item.extra))

    person_movie_credits = tmdb_get_data("person/%s/movie_credits?" % item.extra)
    movies = []
    if person_movie_credits:
        movies.extend(tmdb_tag(person_movie_credits, 'cast', []))
        movies.extend(tmdb_tag(person_movie_credits, 'crew', []))

    # Movie person list is not paged
    return build_movie_list(item, movies)

def search_company_by_name(item, search_terms):
    logger.info("streamondemand.database search_company_by_name '%s'"%(search_terms))

    companies = tmdb_get_data("search/company?query=%s&" % url_quote_plus(search_terms))

    itemlist = []
    for company in companies:
        name = normalize_unicode(tmdb_tag(company, 'name'))
        poster = tmdb_image(company, 'logo_path')

        itemlist.append(Item(
            channel=item.channel,
            action='search_movie_by_company',
            extra=str(tmdb_tag(company, 'id')),
            title=name,
            thumbnail=poster,
            viewmode='list',
            ))

    return itemlist

def search_movie_by_company(item):
    logger.info("streamondemand.channels.database search_movie_by_company '%s'"%(item.extra))

    return list_movie(Item(channel=item.channel, url='company/%s/movies?' % item.extra, plot="1"))

def search_collection_by_name(item, search_terms):
    logger.info("streamondemand.channels.database search_collection_by_name '%s'"%(search_terms))

    collections = tmdb_get_data("search/collection?query=%s&" % url_quote_plus(search_terms))

    itemlist = []
    for collection in collections:
        name = normalize_unicode(tmdb_tag(collection, 'name'))
        poster = tmdb_image(collection, 'poster_path')
        fanart = tmdb_image(collection, 'backdrop_path', 'w1280')

        itemlist.append(Item(
            channel=item.channel,
            action='search_movie_by_collection',
            extra=str(tmdb_tag(collection, 'id')),
            title=name,
            thumbnail=poster,
            viewmode='list',
            fanart=fanart,
            ))

    return itemlist

def search_movie_by_collection(item):
    logger.info("streamondemand.channels.database search_movie_by_collection '%s'"%(item.extra))

    collection = tmdb_get_data("collection/%s?" % item.extra)

    # Movie collection list is not paged
    return build_movie_list(item, collection['parts']) if 'parts' in collection else []

def build_movie_list(item, movies):
    if movies is None: return []

    itemlist = []
    for movie in movies:
        title = normalize_unicode(tmdb_tag(movie, 'title'))
        title_search = normalize_unicode(tmdb_tag(movie, 'title'), encoding='ascii')
        poster = tmdb_image(movie, 'poster_path')
        fanart = tmdb_image(movie, 'backdrop_path', 'w1280')
        jobrole = normalize_unicode(' [COLOR azure][' + tmdb_tag(movie, 'job') + '][/COLOR]' if tmdb_tag_exists(movie, 'job') else '')
        genres = ' / '.join([tmdb_genre(genre).upper() for genre in tmdb_tag(movie, 'genre_ids', [])])
        year = tmdb_tag(movie, 'release_date')[0:4] if tmdb_tag_exists(movie, 'release_date') else ''
        plot = "[COLOR orange]%s%s[/COLOR]\n%s"%(genres, '\n' + year, tmdb_tag(movie, 'overview'))
        plot = normalize_unicode(plot)

        found = False
        kodi_db_movies = kodi_database_movies(title)
        for kodi_db_movie in kodi_db_movies:
            logger.info('streamondemand.database set for local playing(%s):\n%s' % (title, str(kodi_db_movie)))
            if year == str(kodi_db_movie["year"]):
                found = True
                itemlist.append(Item(
                    channel=item.channel,
                    action='play',
                    url=kodi_db_movie["file"],
                    title='[COLOR orange][%s][/COLOR] ' % NLS_Library + kodi_db_movie["title"] + jobrole,
                    thumbnail=kodi_db_movie["art"]["poster"],
                    category=genres,
                    plot=plot,
                    viewmode='movie_with_plot',
                    fanart=kodi_db_movie["art"]["fanart"],
                    folder=False,
                ))

        if not found:
            logger.info('streamondemand.database set for channels search(%s)' % title)
            itemlist.append(Item(
                channel=item.channel,
                action='do_channels_search',
                extra=("%4s" % year) + title_search,
                title=title + jobrole,
                thumbnail=poster,
                category=genres,
                plot=plot,
                viewmode='movie_with_plot',
                fanart=fanart,
                ))

    return itemlist

def do_channels_search(item):
    logger.info("streamondemand.channels.database do_channels_search " + item.extra)

    try:
        title_year = int(item.extra[0:4])
    except Exception:
        title_year = 0
    title_search = item.extra[4:]

    import glob
    import imp
    from lib.fuzzywuzzy import fuzz

    master_exclude_data_file = os.path.join( config.get_runtime_path() , "resources", "sodsearch.txt")
    logger.info("streamondemand.channels.database master_exclude_data_file=" + master_exclude_data_file)

    exclude_data_file = os.path.join( config.get_data_path() , "sodsearch.txt")
    logger.info("streamondemand.channels.database exclude_data_file=" + exclude_data_file)

    channels_path = os.path.join( config.get_runtime_path() , "channels" , '*.py' )
    logger.info("streamondemand.channels.database channels_path=" + channels_path)

    channels_excluded = "seriesly\nbuscador\ntengourl\n__init__\n"

    for path in [master_exclude_data_file, exclude_data_file]:
        if os.path.exists(path):
            logger.info("streamondemand.channels.database found exclusion file %s" % path)

            fileexclude = open(path, "r")
            channels_excluded += fileexclude.read()
            fileexclude.close()
        else:
            logger.info("streamondemand.channels.database not found exclusion file %s" % path)

    try:
        import xbmcgui
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(NLS_Looking_For % item.title)
        show_dialog = True
    except:
        show_dialog = False

    channel_files = glob.glob(channels_path)
    number_of_channels = len(channel_files)

    itemlist = []
    channels_successfull = ''
    for index, infile in enumerate(channel_files):
        if progress_dialog.iscanceled():
            logger.info("streamondemand.channels.database channels search aborted")
            break

        basename = os.path.basename(infile)[:-3]
        if basename in channels_excluded:
            logger.info("streamondemand.channels.database excluded channel %s" % basename)
        else:
            if show_dialog:
                progress_dialog.update(index * 100 / number_of_channels,
                    NLS_Searching_In % basename,
                    NLS_Found_So_Far % (len(itemlist), channels_successfull))

            try:
                obj = imp.load_source(basename, infile)
                logger.info("streamondemand.channels.database loaded %s from %s" % (basename, infile))

                #
                # Please note that python threads cannot be stopped, therefore, if the channel is
                # taking too long, the threading allows the calling process to continue but not
                # to kill the channel thread. The runaway channel will continue to execute and
                # eventually terminate later. OK, it takes resources, but better to consume some
                # additional resources than blocking the KODI GUI altogether.
                #
                from threading import Thread

                class ChannelThread(Thread):
                    def __init__(self, channel_obj, search_terms):
                        Thread.__init__(self)
                        self._channel_obj = channel_obj
                        self._search_terms = search_terms
                        self._return = []

                    def run(self):
                        self._return = self._channel_obj.search(Item(), self._search_terms)

                    def join(self, timeout=0):
                        Thread.join(self, timeout)
                        if Thread.is_alive(self) and timeout > 0:
                            logger.info("streamondemand.channels.database forgetting channel %s because is taking more than %s seconds" % (basename, timeout))
                        return self._return

                logger.info("streamondemand.channels.database searching in channel %s for '%s'" % (basename, title_search))
                channel_thread = ChannelThread(obj, title_search.replace(' ', '+'))
                # NOTE: setting dameon to True allows the main thread can exit even if there are daemon threads still running
                channel_thread.daemon = True
                channel_thread.start()
                channel_result_itemlist = channel_thread.join(60)

                for item in channel_result_itemlist:
                    title = item.fulltitle

                    # Check if the found title matches the release year
                    year_match = re.search('\(.*(\d{4})\)', title)
                    if year_match:
                        found_year = int(year_match.group(1))
                        title = title[:year_match.start()] + title[year_match.end():]
                        if title_year > 0 and abs(found_year - title_year) > 1:
                            logger.info("streamondemand.channels.database %s: '%s' doesn't match the searched title '%s' %d (delta year is %d)" \
                                % (basename, item.fulltitle, title_search, title_year, abs(found_year - title_year)))
                            continue

                    # Clean up a bit the returned title to improve the fuzzy matching
                    title = re.sub(r'\(\d\.\d\)', '', title)                    # Rating, es: (8.4)
                    title = re.sub(r'(?i) (film|streaming|ITA)', '', title)     # Common keywords in titles
                    title = re.sub(r'[\[(](HD|B/N)[\])]', '', title)            # Common keywords in titles, es. [HD], (B/N), etc.
                    title = re.sub(r'(?i)\[/?COLOR[^\]]*\]', '', title)         # Formatting keywords

                    # Check if the found title fuzzy matches the searched one
                    fuzzy = fuzz.token_sort_ratio(title_search, title)
                    if  fuzzy <= 85:
                            logger.info("streamondemand.channels.database %s: '%s' doesn't match the searched title '%s' %d (title fuzzy comparision is %d)" \
                                % (basename, item.fulltitle, title_search, title_year, fuzzy))
                            continue

                    logger.info("streamondemand.channels.database %s: '%s' matches the searched title '%s' %d (title fuzzy comparision is %d)" \
                        % (basename, item.fulltitle, title_search, title_year, fuzzy))

                    item.title = "[COLOR orange][%s][/COLOR] %s" % (basename, item.title)
                    item.fulltitle = title # Use the clean title for sorting
                    item.viewmode = "list"
                    itemlist.append(item)

                    if basename not in channels_successfull:
                        if len(channels_successfull): channels_successfull += ', '
                        channels_successfull += basename

            except:
                import traceback
                logger.error(traceback.format_exc())

    itemlist = sorted(itemlist, key=lambda Item: fuzz.token_sort_ratio(title_search, item.fulltitle), reverse=True)

    if show_dialog:
        progress_dialog.close()

    return itemlist

def normalize_unicode(string, encoding='utf-8'):
    return normalize('NFKD', string if isinstance(string, unicode) else unicode(string, encoding, 'ignore')).encode(encoding, 'ignore')

def tmdb_get_data(url="", results=[ 0, 0]):
    url = TMDB_URL_BASE + "%sinclude_adult=%s&language=%s&api_key=%s" % (url, INCLUDE_ADULT, LANGUAGE_ID, TMDB_KEY)
    response = get_JSON_response(url)
    results[0] = response['total_pages'] if 'total_pages' in response else 0
    results[1] = response['total_results'] if 'total_results' in response else 0
    return response["results"] if response and "results" in response else response

def tmdb_tag_exists(entry, tag):
    return tag in entry and entry[tag] is not None

def tmdb_tag(entry, tag, default=""):
    return entry[tag] if isinstance(entry, dict) and tag in entry else default

def tmdb_image(entry, tag, width='original'):
    return TMDB_IMAGES_BASEURL + width + '/' + tmdb_tag(entry, tag) if tmdb_tag_exists(entry, tag) else ''

def tmdb_genre(id):
    if id not in TMDb_genres:
        genres = tmdb_get_data("genre/list?")
        for genre in tmdb_tag(genres, 'genres', []):
                TMDb_genres[tmdb_tag(genre, 'id')] = tmdb_tag(genre, 'name')

    return TMDb_genres[id] if id in TMDb_genres else str(id)

def kodi_database_movies(title):
    json_query = \
        '{"jsonrpc": "2.0",\
            "params": {\
               "sort": {"order": "ascending", "method": "title"},\
               "filter": {"operator": "is", "field": "title", "value": "%s"},\
               "properties": ["title", "art", "file", "year"]\
            },\
            "method": "VideoLibrary.GetMovies",\
            "id": "libMovies"\
        }' % title
    response = get_xbmc_JSONRPC_response(json_query)
    return response["result"]["movies"] if response and "result" in response and "movies" in response["result"] else []

def get_xbmc_JSONRPC_response(json_query=""):
    try:
        response = xbmc.executeJSONRPC(json_query)
        response = unicode(response, 'utf-8', errors='ignore')
        response = json.loads(response)
        logger.info("streamondemand.channels.database jsonrpc %s" % response)
    except Exception, e:
        logger.info("streamondemand.channels.database jsonrpc error: %s" % str(e))
        response = None
    return response

def url_quote_plus(input_string):
    try:
        return urllib.quote_plus(input_string.encode('utf8', 'ignore'))
    except:
        return urllib.quote_plus(unicode(input_string, "utf-8").encode("utf-8"))

def get_JSON_response(url="", cache_days=7.0, headers=False):
    now = time.time()
    hashed_url = hashlib.md5(url).hexdigest()
    cache_path = xbmc.translatePath(os.path.join(ADDON_DATA_PATH, 'cache'))
    path = os.path.join(cache_path, hashed_url + ".txt")
    cache_seconds = int(cache_days * 86400.0)
    prop_time = HOME.getProperty(hashed_url + "_timestamp")
    if prop_time and now - float(prop_time) < cache_seconds:
        try:
            prop = json.loads(HOME.getProperty(hashed_url))
            logger.info("streamondemand.channels.database prop load for %s. time: %f" % (url, time.time() - now))
            return prop
        except:
            logger.info("could not load prop data for %s" % url)
    if xbmcvfs.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
        results = read_from_file(path)
        logger.info("streamondemand.channels.database loaded file for %s. time: %f" % (url, time.time() - now))
    else:
        response = get_http(url, headers)
        try:
            results = json.loads(response)
            logger.info("streamondemand.channels.database download %s. time: %f" % (url, time.time() - now))
            save_to_file(results, hashed_url, cache_path)
        except:
            logger.info("streamondemand.channels.database Exception: Could not get new JSON data from %s. Tryin to fallback to cache" % url)
            if xbmcvfs.exists(path):
                results = read_from_file(path)
            else:
                results = []
    HOME.setProperty(hashed_url + "_timestamp", str(now))
    HOME.setProperty(hashed_url, json.dumps(results))
    return results

def get_http(url=None, headers=False):
    succeed = 0
    if not headers:
        headers = {'User-agent': 'XBMC/14.0 ( phil65@kodi.tv )'}
    request = urllib2.Request(url)
    for (key, value) in headers.iteritems():
        request.add_header(key, value)
    while (succeed < 2) and (not xbmc.abortRequested):
        try:
            response = urllib2.urlopen(request, timeout=3)
            data = response.read()
            return data
        except:
            logger.info("get_http: could not get data from %s" % url)
            xbmc.sleep(1000)
            succeed += 1
    return None

def save_to_file(content, filename, path=""):
    if path == "":
        return False
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdirs(path)
    text_file_path = os.path.join(path, filename + ".txt")
    now = time.time()
    text_file = xbmcvfs.File(text_file_path, "w")
    json.dump(content, text_file)
    text_file.close()
    logger.info("saved textfile %s. Time: %f" % (text_file_path, time.time() - now))
    return True

def read_from_file(path="", raw=False):
    if path == "":
        return False
    if not xbmcvfs.exists(path):
        return False
    try:
        with open(path) as f:
            logger.info("opened textfile %s." % (path))
            if not raw:
                result = json.load(f)
            else:
                result = f.read()
        return result
    except:
        logger.info("failed to load textfile: " + path)
        return False
