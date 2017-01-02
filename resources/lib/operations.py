# -*- coding: utf-8 -*-
import sys
import urllib
import urllib2
import urlparse
import socket
import re
from bs4 import BeautifulSoup
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import json

sys_arg = str(sys.argv[1])
ADDON_ID = 'plugin.video.streamathome'

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive'}

header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
           'Accept': '*/*',
           'Connection': 'keep-alive'}


# add item to video
def add_menu_items(details, show=True, is_folder=True):
    changed = False
    for detail in details:
        try:
            url = sys.argv[0]+"?url="+detail['url']+"&mode="+str(detail['mode']) + \
                  "&name="+urllib.quote_plus(detail['title'].encode("utf-8"))+"&icon="+detail['icon']
            li = xbmcgui.ListItem(detail['title'].encode("utf-8"),
                                  iconImage=detail['icon'],
                                  thumbnailImage=detail['icon'])
            li.setInfo(type=detail['type'],
                       infoLabels={"Title": detail['title'].encode("utf-8"), "Plot": detail['plot']})
        except:
            url = sys.argv[0]+"?url="+detail['url']+"&mode="+str(detail['mode']) + \
                  "&name="+urllib.quote_plus(detail['title']).decode("utf-8")+"&icon="+detail['icon']
            li = xbmcgui.ListItem(detail['title'].encode("utf-8"),
                                  iconImage=detail['icon'],
                                  thumbnailImage=detail['icon'])
            li.setInfo(type=detail['type'],
                       infoLabels={"Title": detail['title'].decode("utf-8"), "Plot": detail['plot']})

        # this will be the title displayed when the video is playing
        if 'video_title' in detail:
            url = url + "&videotitle=" + detail['video_title']
        if 'resolution' in detail:
            url = url + "&resolution=" + detail['resolution']
        if 'page_num' in detail:
            url = url + "&pagenum=" + detail['page_num']

        if is_folder:
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)
        else:
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)

    if show:
        if changed:
            xbmc.executebuiltin('Container.SetViewMode(%d)' % int(xbmcplugin.getSetting(int(sys_arg), "vidview")))
    xbmcplugin.endOfDirectory(int(sys_arg))


# play the video
def play_media(title, thumbnail, link, media_type='Video', library=True, title2=""):
    li = xbmcgui.ListItem(label=title2, iconImage=thumbnail, thumbnailImage=thumbnail, path=link)
    li.setProperty('IsPlayable', 'true')
    li.setInfo("video", {"Title": title})
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)


def parse_parameters(input_string=sys.argv[2]):
    """Parses a parameter string starting at the first ? found in inputString

    Argument:
    inputString: the string to be parsed, sys.argv[2] by default

    Returns a dictionary with parameter names as keys and parameter values as values
    """

    parameters = {}
    log_msg(input_string, xbmc.LOGDEBUG)
    p1 = input_string.find('?')
    if p1 >= 0:
        split_parameters = input_string[p1 + 1:].split('&')
        for nameValuePair in split_parameters:
            try:
                if len(nameValuePair) > 0:
                    pair = nameValuePair.split('=')
                    key = pair[0]
                    value = urllib.unquote(urllib.unquote_plus(pair[1])).decode('utf-8')
                    parameters[key] = value
            except:
                pass
    return parameters


# get the content of the url.
def get_url_content(url, header=header):
    # when there's utf-8 characters in the url, try to quote them before accessing the web page.
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(url)
    path = urllib.quote(path.encode('utf-8'), '/%')
    qs = urllib.quote_plus(qs, ':&=')
    url = urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

    try:
        req = urllib2.Request(url, headers=header)
        response = urllib2.urlopen(req)

        if response and response.getcode() == 200:
            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO.StringIO( response.read())
                gzip_f = gzip.GzipFile(fileobj=buf)
                content = gzip_f.read()
            else:
                content = response.read()
            content = content.decode('utf-8', 'ignore')
            return content
        else:
            log_msg('Error Loading URL : '+str(response.getcode()), xbmc.LOGERROR)
    except urllib2.HTTPError as err:
        log_msg('Error Loading URL : '+url.encode("utf-8"))
        log_msg(str(err))
    except urllib2.URLError as err:
        log_msg('Error Loading URL : '+url.encode("utf-8"))
        log_msg(str(err))
    except socket.timeout as err:
        log_msg('Error Loading URL : '+url.encode("utf-8"))
        log_msg(str(err))

    return False


# log the message according the to log level.
def log_msg(msg, log_level=xbmc.LOGERROR):
    head = ADDON_ID + " - "
    try:
        xbmc.log(head + str(msg.encode("utf-8")), log_level)
    except:
        xbmc.log(head + str(msg), log_level)


# display notice
def notify(addonId, message, reportError=False, timeShown=5000):
    """Displays a notification to the user

    Parameters:
    addonId: the current addon id
    message: the message to be shown
    timeShown: the length of time for which the notification will be shown, in milliseconds, 5 seconds by default
    """
    addon = xbmcaddon.Addon(addonId)
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (addon.getAddonInfo('name'), message, timeShown, addon.getAddonInfo('icon')))
    if reportError:
        log_msg(message)
    else:
        log_msg(message, xbmc.LOGDEBUG)


####################
# MapleStage #######
# find episode pages from maplestage series page
def find_ms_episode(url):
    content = get_url_content(url)

    json_obj = get_json_from_content(content)

    episode_list = []

    if json_obj:
        if 'props' in json_obj:
            for prop in json_obj['props']:
                if 'name' in prop:
                    if prop['name'] == 'show':
                        if ('value' in prop) & ('episodes' in prop['value']):
                            for episode in prop['value']['episodes']:
                                menu_item = {}
                                menu_item['title'] = episode['slug'] + ' - ' + episode['numStr']
                                if 'topicCn' in episode:
                                    menu_item['title'] = menu_item['title'] + ' - ' + episode['topicCn']

                                menu_item['url'] = 'http://maplestage.com/episode/' + episode['shortId'] + \
                                                   '/' + episode['slug'] + '-' + episode['numStr']
                                menu_item['mode'] = 2
                                menu_item['icon'] = episode['thumb']
                                menu_item['type'] = ""
                                menu_item['plot'] = ""
                                episode_list.append(menu_item)
                        else:
                            log_msg("Cannot find episodes under show tag")
                            log_msg(content)
                    else:
                        # other props ignore
                        continue
                else:
                    log_msg('Cannot find name prop.')
                    log_msg(content)
        else:
            log_msg("Cannot find props in the string.")
            log_msg(content)

        if len(episode_list) > 0:
            # found some episodes
            add_menu_items(episode_list)
        else:
            log_msg("Cannot find any episodes.")
            log_msg(content)
            notify(ADDON_ID, "Cannot find any episodes.", True)
    else:
        notify(ADDON_ID, "Unable to load page.", True)


# get the parsed json object from the page content
def get_json_from_content(content):
    if content:
        bs_obj = BeautifulSoup(content, "html.parser")

        val_string = re.compile(r'var pageData = (.+);', re.MULTILINE | re.DOTALL)

        page_data = bs_obj.find("script", text=val_string)
        if page_data:
            match = val_string.search(page_data.text)
            if match:
                json_str = match.group(1)
                json_obj = json.loads(json_str)
                return json_obj
            else:
                log_msg("Cannot find pageData definition in the web page.")
                log_msg(content)
        else:
            log_msg("Cannot find pageData definition in the web page.")
            log_msg(content)

    return False


# find vid link from episode page
def find_ms_episode_link(url):
    content = get_url_content(url)
    json_obj = get_json_from_content(content)

    source_list = []
    if json_obj:
        video_title = json_obj['title'][len(json_obj['title']) - 1]
        if 'props' in json_obj:
            for prop in json_obj['props']:
                if 'name' in prop:
                    if prop['name'] == 'model':
                        if ('value' in prop) & ('videoSources' in prop['value']):
                            source_num = 1
                            for source in prop['value']['videoSources']:
                                if 'videos' in source:
                                    multi_part = False
                                    if len(source['videos']) > 1:
                                        # the episode has multi-part videos
                                        multi_part = True
                                    part_num = 1
                                    for video in source['videos']:
                                        source_item = {}
                                        source_item['title'] = 'Source ' + str(source_num) + ' - ' + video['type']
                                        if multi_part:
                                            source_item['title'] += " Part " + str(part_num)
                                            part_num += 1
                                        source_item['url'] = get_vid_link_by_site(video['id'],
                                                                                  video['type'])
                                        source_item['mode'] = 3
                                        source_item['icon'] = prop['value']['thumb']
                                        if 'thumbnail' in video:
                                            source_item['icon'] = video['thumbnail']
                                        source_item['type'] = ""
                                        source_item['plot'] = ""
                                        source_item['video_title'] = video_title

                                        # for some type that we do not know, display an notice with empty url
                                        if source_item['url'] == False:
                                            source_item['url'] = ""
                                            source_item['title'] = 'UNPLAYABLE - ' + source_item['title']
                                        source_list.append(source_item)

                                else:
                                    log_msg("Cannot find video sources.")
                                    log_msg(content)

                                source_num += 1
                        else:
                            log_msg("Cannot find video sources.")
                            log_msg(content)
                    else:
                        # if the name is not model, ignore
                        continue
                else:
                    log_msg('Cannot find name prop.')
                    log_msg(content)
        else:
            log_msg("Cannot find props in the string.")
            log_msg(content)

    if len(source_list) > 0:
        add_menu_items(source_list, is_folder=False)
    else:
        log_msg("Cannot find any video sources.")
        log_msg(content)
        notify(ADDON_ID, "Cannot find any video sources.", True)


# generate direct video link
def get_vid_link_by_site(vid, site):
    url = False
    if site == 'dailymotion':
        url = 'http://www.dailymotion.com/video/' + vid
    elif site == 'youtube':
        url = 'https://www.youtube.com/embed/' + vid
    else:
        log_msg("Cannot generate video link for site " + site + ".")

    return url


