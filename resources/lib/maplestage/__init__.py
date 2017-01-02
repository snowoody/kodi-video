# -*- coding: utf-8 -*-

# maplestage
import urllib2
import json
import xbmc
from .. import menu

ADDON_ID = 'plugin.video.streamathome'

client_header = {"User-Agent": 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
                 "Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "*/*",
                 "Referer": "http://www.dnvod.eu/Movie/Readyplay.aspx?id=jydSM%2fudfCo%3d",
                 "Accept-Encoding": "",
                 "Accept-Language": "de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2,zh;q=0.2,zh-TW;q=0.2,fr-FR;q=0.2,fr;q=0.2",
                 "X-Requested-With": "XMLHttpRequest",
                 "DNT": "1"}


# collect user inputs
def get_search_input(question):
    kb = xbmc.Keyboard(None, question, False)
    kb.doModal()
    if kb.isConfirmed():
        text = kb.getText()
        return text
    else:
        return False


# search for shows
def search_for_series(url):
    search_str = get_search_input("Search for shows")

    # user did not give any input.
    if not search_str:
        return menu.maplestage_menu

    url = url + "?q=" + search_str
    request = urllib2.Request(url, None, headers=client_header)
    response = urllib2.urlopen(request)
    content = response.read()

    series_list = []
    series = json.loads(content)
    log_msg("json data")
    for serie in series:
        title = serie['name']
        thumbnail = serie['thumb']
        slug = serie['slug']
        url = "http://maplestage.com/show/" + slug

        series_item = {}
        series_item['title'] = title
        series_item['url'] = url
        series_item['mode'] = 1
        series_item['icon'] = thumbnail
        series_item['type'] = ""
        series_item['plot'] = ""
        series_list.append(series_item)

    return series_list


# log the message according the to log level.
def log_msg(msg, log_level=xbmc.LOGERROR):
    head = ADDON_ID + " - "
    try:
        xbmc.log(head + str(msg.encode("utf-8")), log_level)
    except:
        xbmc.log(head + str(msg), log_level)
