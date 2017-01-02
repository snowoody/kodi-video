# -*- coding: utf-8 -*-

# StreamHD.eu

import re
import urllib2
import exceptions
from bs4 import BeautifulSoup
import xbmc
import xbmcgui

ADDON_ID = 'plugin.video.streamathome'

url1 = 'http://www.streamhd.eu'
url2 = 'http://www.streamhd.eu'


# log the message according the to log level.
def log_msg(msg, log_level=xbmc.LOGERROR):
    head = ADDON_ID + " - "
    try:
        xbmc.log(head + str(msg.encode("utf-8")), log_level)
    except:
        xbmc.log(head + str(msg), log_level)

client_header = {"User-Agent": 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
                 "Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "*/*",
                 "Referer": "http://www.dnvod.eu/Movie/Readyplay.aspx?id=jydSM%2fudfCo%3d",
                 "Accept-Encoding": "",
                 "Accept-Language": "de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2,zh;q=0.2,zh-TW;q=0.2,fr-FR;q=0.2,fr;q=0.2",
                 "X-Requested-With": "XMLHttpRequest",
                 "DNT": "1"}


# get the category list from main page
def find_category(url):
    request_1 = urllib2.Request(url, None, client_header)
    response_1 = urllib2.urlopen(request_1)
    content = response_1.read()

    bs_obj = BeautifulSoup(content, "html.parser")

    menu_list = []
    # find the front page list
    main_html = bs_obj.find_all("div", {"class": "panel panel-default"})[0]
    live_title = main_html.find_all("div", {"class": "panel-heading"})[0].h2.text
    live_items = main_html.find_all("div", {"class": "panel-body"})[0].\
        find_all("table", {"class": "table table-hover table-condensed table-striped"})[0].tbody.find_all("tr")
    for live in live_items:
        tds = live.find_all("td")
        time = tds[0].find_all("span", {"class": "eventsmall"})[0].text
        time_zone = tds[0].find_all("span", {"class": "hidden-xs"})[0].text
        live_link = tds[4].find_all("a")[0]
        title = live_link.text
        link = live_link.get('href')
        live_item = {}
        live_item['title'] = live_title + time + time_zone + ' -' + title
        live_item['url'] = "http://www.streamhd.eu" + link
        live_item['mode'] = 203
        live_item['icon'] = ""
        live_item['type'] = ""
        live_item['plot'] = ""
        menu_list.append(live_item)

    # find the categories
    nav_html = bs_obj.find_all("nav", {"class": "navbar navbar-default"})[0].\
        find_all("div", {"class": "collapse navbar-collapse"})[0].ul
    for cat in nav_html.find_all("li", recursive=False):
        log_msg("test " + str(cat), xbmc.LOGDEBUG)
        log_msg("test 2: " + str(cat.get("class")), xbmc.LOGDEBUG)
        if cat.get("class") and cat.get("class")[0] == u'divider-vertical':
            # separator skip
            continue

        cat_name = cat.a.text.strip()
        cat_img = cat.a.img.get("src")
        if cat_img:
            cat_img = "http://www.streamhd.eu" + cat_img
        else:
            cat_img = ""
        if cat.get("class") and ((cat.get("class")[0] == u'dropdown') or (cat.get("class")[0] == u'dropdown open')):
            for subcat in cat.ul.find_all("li"):
                subcat_name = subcat.a.text.strip()
                subcat_url = "http://www.streamhd.eu" + subcat.a.get("href")
                subcat_item = {}
                subcat_item['title'] = cat_name + "-" + subcat_name
                subcat_item['url'] = subcat_url
                subcat_item['mode'] = 205
                subcat_item['icon'] = cat_img
                subcat_item['type'] = ""
                subcat_item['plot'] = ""
                menu_list.append(subcat_item)
        else:
            cat_url = "http://www.streamhd.eu" + cat.a.get("href")
            cat_item = {}
            cat_item['title'] = cat_name
            cat_item['url'] = cat_url
            cat_item['mode'] = 205
            cat_item['icon'] = cat_img
            cat_item['type'] = ""
            cat_item['plot'] = ""
            menu_list.append(cat_item)

    return menu_list


# get the direct link of the video from the video page
def get_video_link(url):
    log_msg("get_video_link - getting video link for url: " + url, xbmc.LOGINFO)
    request_1 = urllib2.Request(url, None, client_header)
    response_1 = urllib2.urlopen(request_1)
    content = response_1.read()

    bs_obj = BeautifulSoup(content, "html.parser")
    frame = bs_obj.find_all("iframe", {"name": "videoiframe"})[0]
    video_link = frame.get("src")

    log_msg("get_video_link - getting video link for url: " + video_link + "from url: " + url, xbmc.LOGINFO)
    request_2 = urllib2.Request(video_link, None, client_header)
    request_2.add_header('Referer', url)
    response_2 = urllib2.urlopen(request_2)
    content_2 = response_2.read()

    link_2_regex = r'<script[^>]+> fid="([^"]+)";[^<]+</script><script[^>]+src="([^"]+)"></script>'
    link_2_pattern = re.compile(link_2_regex)
    link_2_match = link_2_pattern.search(content_2)
    vid = ""
    if link_2_match:
        vid = link_2_match.group(1)
    else:
        log_msg("get_video_link link_2_regex : " + link_2_regex)
        log_msg("get_video_link content_2: " + content_2)
        return False

    # construct the second link
    link_2 = 'http://hdcast.org/streamhd.php?u=' + vid + '&vw=100%&vh=100%'
    log_msg("get_video_link - getting video link for url: " + link_2 + "from url: " + video_link, xbmc.LOGINFO)

    request_3 = urllib2.Request(link_2, None, client_header)
    request_3.add_header('Referer', video_link)
    response_3 = urllib2.urlopen(request_3)
    content_3 = response_3.read()

    # get the next link
    link_3_regex = r'<iframe[^>]+src="?([^"\s]+)"?\s+allowfullscreen="allowfullscreen">'
    link_3_pattern = re.compile(link_3_regex)
    link_3_match = link_3_pattern.search(content_3)
    link_3 = ""
    if link_3_match:
        link_3 = link_3_match.group(1)
    else:
        log_msg("get_video_link link_3_regex : " + link_3_regex)
        log_msg("get_video_link content_3: " + content_3)
        return False

    log_msg("get_video_link - getting video link for url: " + link_3 + "from url: " + link_2, xbmc.LOGINFO)

    # get the next page
    request_4 = urllib2.Request(link_3, None, client_header)
    request_4.add_header('Referer', link_2)
    response_4 = urllib2.urlopen(request_4)
    content_4 = response_4.read()

    # get the video link
    link_4_regex = r'jwplayer\("videoContainer"\).setup\([^\)]+file:"([^"]+)"'
    link_4_pattern = re.compile(link_4_regex, re.MULTILINE)
    link_4_match = link_4_pattern.search(content_4)
    link_4 = ""
    if link_4_match:
        link_4 = link_4_match.group(1)
    else:
        log_msg("get_video_link link_4_regex : " + link_4_regex)
        log_msg("get_video_link content_4: " + content_4)
        return False

    log_msg("get_video_link - got video link: " + link_4, xbmc.LOGINFO)

    # log_msg("get_video_link: " + content_4)

    return link_4


# play the video url.
def play_media(url, title):
    playlist = xbmc.PlayList(1)
    playlist.clear()
    list_item = xbmcgui.ListItem(u'Play')
    list_item.setInfo(type='video', infoLabels={"Title": title})
    playlist.add(url, listitem=list_item)
    xbmc.Player().play(playlist)


# find video links from the category page
def find_video_link(url):
    request_1 = urllib2.Request(url, None, client_header)
    response_1 = urllib2.urlopen(request_1)
    content = response_1.read()

    # bs_obj = BeautifulSoup(content, "html.parser")
    bs_obj = BeautifulSoup(content.decode('utf-8', 'ignore'), "html5lib")

    menu_list = []
    # find the front page list
    main_html = bs_obj.find_all("div", {"class": "panel panel-default"})[0]
    if main_html.find_all("div", {"class": "panel-heading"})[0].h2:
        live_title = main_html.find_all("div", {"class": "panel-heading"})[0].h2.text
        try:
            live_items = main_html.find_all("div", {"class": "panel-body"})[0]. \
                find_all("table", {"class": "table table-hover table-condensed table-striped"})[0].tbody.find_all("tr")
            for live in live_items:
                tds = live.find_all("td")
                time = tds[0].find_all("span", {"class": "eventsmall"})[0].text.strip()
                time_zone = tds[0].find_all("span", {"class": "hidden-xs"})[0].text.strip()
                live_link = tds[4].find_all("a")[0]
                title = live_link.text.strip()
                link = live_link.get('href')
                live_item = {}
                live_item['title'] = live_title + time + time_zone + ' - ' + title
                live_item['url'] = "http://www.streamhd.eu" + link
                live_item['mode'] = 203
                live_item['icon'] = ""
                live_item['type'] = ""
                live_item['plot'] = ""
                menu_list.append(live_item)
        except exceptions.IndexError as err:
            log_msg("find_video_link - parsing error: " + str(err))
    else:
        log_msg("find_video_link - Cannot find any video in url: " + url)

    return menu_list
