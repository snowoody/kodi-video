# -*- coding: utf-8 -*-

# dnvodPlayer
# adapted from Cameron

import requests
import re
import urllib
import urllib2
import exceptions
from bs4 import BeautifulSoup
import xbmcgui
import xbmc


ADDON_ID = 'plugin.video.streamathome'

url1 = 'http://www.dnvod.eu'
url2 = 'http://www.dnvod.eu/Movie/Readyplay.aspx?id=KVGG7jEHOhU%3d'


# get ASP.NET_SessionId
def get_session_id(url_1, url_2):
    session = requests.Session()
    session.get(url_1)
    r1 = session.get(url_2)
    header = r1.headers
    reg = r'ASP.NET_SessionId=(.*); path=/; HttpOnly'
    pattern = re.compile(reg)
    session_id_result = pattern.findall(header['Set-Cookie'])[0]
    return session_id_result

session_id = get_session_id(url1, url2)

# create user headers
dnvod_header = {"User-Agent": 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
           "Content-Type": "application/x-www-form-urlencoded",
           "Accept": "*/*",
           "Referer": "http://www.dnvod.eu/Movie/Readyplay.aspx?id=jydSM%2fudfCo%3d",
           "Accept-Encoding": "",
           "Accept-Language": "de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2,zh;q=0.2,zh-TW;q=0.2,fr-FR;q=0.2,fr;q=0.2",
           "X-Requested-With": "XMLHttpRequest",
           "DNT": "1",
           "Cookie": 'ASP.NET_SessionId='+session_id}

# create server headers
dnvod_server_header = {"Host": "www.dnvod.eu",
            "Content-Length": "36",
            "Cache-Control": "nax-age=0",
            "Accept": "*/*",
            "Origin": "http://www.dnvod.eu",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "DNT": "1",
            "Referer": "http://www.dnvod.eu/Movie/Readyplay.aspx?id=%2bWXev%2bhf16w%3d",
            "Accept-Encoding": "",
            "Accept-Language": "de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2,zh;q=0.2,zh-TW;q=0.2,fr-FR;q=0.2,fr;q=0.2",
            "Connection": "keep-alive",
            "Cookie": 'ASP.NET_SessionId='+session_id}


# find episodes from series link
def find_dnvod_episode(url):
    request_1 = urllib2.Request(url, None, dnvod_header)
    response_1 = urllib2.urlopen(request_1)
    content = response_1.read()

    bs_obj = BeautifulSoup(content, "html.parser")
    # find the series title
    title = bs_obj.find_all("div", {"class": "p-r"})[0].ul.h1.text

    # find the series cover picture
    try:
        img = bs_obj.find_all("div", {"id": "spec-list"})[0].ul.li.img.get("src")
        img = "http:" + img
    except exceptions.IndexError:
        img = ""
        log_msg("Cannot find image link")
        log_msg(content)

    # find the links to each episode
    episode_list = []
    for div in bs_obj.find_all("div", {"class": "bfan-n"}):
        url = div.a.get('href')
        url = "http://www.dnvod.eu" + url
        episode_name = div.a.text
        episode_item = {}
        episode_item['title'] = title + ' - ' + episode_name
        episode_item['url'] = url
        episode_item['mode'] = 103
        episode_item['icon'] = img
        episode_item['type'] = ""
        episode_item['plot'] = ""
        episode_item['resolution'] = "sd"
        episode_list.append(episode_item)
        episode_item_hd = episode_item.copy()
        episode_item_hd['resolution'] = "hd"
        episode_item_hd['title'] += ' - HD'
        episode_list.append(episode_item_hd)

    return episode_list


# get the playable video link from the episode url
def get_video_link(url, resolution='sd'):
    request_1 = urllib2.Request(url, None, dnvod_header)
    response_1 = urllib2.urlopen(request_1)
    response_content_1 = response_1.read()

    # get resource id
    reg_id = r'id:.*\'(.*)\','
    pattern_id = re.compile(reg_id)
    res_id = pattern_id.findall(response_content_1)[0]

    # get resource key
    reg_key = r'key:.*\'(.*)\','
    pattern_key = re.compile(reg_key)
    res_key = pattern_key.findall(response_content_1)[0]

    url_2 = 'http://www.dnvod.eu/Movie/GetResource.ashx?id='+res_id+'&type=htm'

    ref = urllib.urlencode({'key': res_key})
    request_2 = urllib2.Request(url_2, ref, dnvod_server_header)
    response_2 = urllib2.urlopen(request_2)
    real_url = response_2.read()
    print("dnvod link: " + real_url)
    pattern = re.compile(r'(\d||\d\d||\d\d\d||\d\d\d\d||\d\d\d\d\d||\d\d\d\d\d\d||\d\d\d\d\d\d\d||\d\d\d\d\d\d\d\d)\.mp4')
    num = re.split(pattern, real_url)
    hd_url = num[0]+'hd-'+num[1]+'.mp4'+num[2]

    if resolution == 'sd':
        return real_url
    elif resolution == 'hd':
        return hd_url
    else:
        log_msg("Cannot recognized resolution " + resolution + ".")

    return ""


# play the dnvod url.
def play_media(url, title, thumbnail):
    playlist = xbmc.PlayList(1)
    playlist.clear()
    list_item = xbmcgui.ListItem(u'Play 播放', iconImage=thumbnail, thumbnailImage=thumbnail)
    list_item.setInfo(type='video', infoLabels={"Title": title})
    playlist.add(url, listitem=list_item)
    xbmc.Player().play(playlist)


# get the category list from main page
def find_dnvod_category(url):
    request_1 = urllib2.Request(url, None, dnvod_header)
    response_1 = urllib2.urlopen(request_1)
    content = response_1.read()

    bs_obj = BeautifulSoup(content.decode('utf-8', 'ignore'), "html5lib")

    category_list = []
    index = bs_obj.find_all("div", {"id": "smoothmenu1"})[0].ul.ul
    for cat in index.find_all("li"):

        if len(cat.find_all("li")) > 0:
            # this is a parent category

            # first get the parent category info
            category_name = cat.a.text
            category_url = cat.a.get('href')
            if "http" not in category_url:
                category_url = "http://www.dnvod.eu" + category_url

            category_item = {}
            category_item['title'] = category_name
            category_item['url'] = category_url
            category_item['mode'] = 105
            category_item['icon'] = "http://www.dnvod.eu/images/logo.jpg"  # currently using the website icon for categories.
            category_item['type'] = ""
            category_item['plot'] = ""
            category_list.append(category_item)

            # now add all the sub-categories
            for sub_cat in cat.find_all("li"):
                subcat_name = category_name + " - " + sub_cat.a.text
                subcat_url = sub_cat.a.get('href')
                if "http" not in subcat_url:
                    subcat_url = "http://www.dnvod.eu" + subcat_url

                subcat_item = {}
                subcat_item['title'] = subcat_name
                subcat_item['url'] = subcat_url
                subcat_item['mode'] = 105
                subcat_item['icon'] = "http://www.dnvod.eu/images/logo.jpg"  # currently using the website icon for categories.
                subcat_item['type'] = ""
                subcat_item['plot'] = ""
                category_list.append(subcat_item)

        else:
            # This is a subcategory. Do nothing.
            continue

    return category_list


# find the series within the category page
def find_dnvod_serie(url, page_num="1"):
    # add the page number parameter to the url if the page number is not 1.
    if page_num != "1":
        url = url + "&page=" + page_num
    request_1 = urllib2.Request(url, None, dnvod_header)
    response_1 = urllib2.urlopen(request_1)
    content = response_1.read()

    serie_list = []
    bs_obj = BeautifulSoup(content.decode('utf-8', 'ignore'), "html5lib")
    series = bs_obj.find_all("div", {"class": "product"})[0].find_all("div", {"class": "cp_a"})
    for serie in series:
        serie_info = serie.find_all("a")[1]
        serie_name = serie_info.get("title")
        serie_url = serie_info.get("href")
        if "http" not in serie_url:
            serie_url = "http://www.dnvod.eu" + serie_url

        serie_img = serie.find_all("img")[0].get("src")
        if serie_img.startswith("//"):
            serie_img = "http:" + serie_img
        elif not serie_img.startswith("http"):
            serie_img = "http://www.dnvod.eu" + serie_img


        serie_item = {}
        serie_item['title'] = serie_name
        serie_item['url'] = serie_url
        serie_item['mode'] = 101
        serie_item['icon'] = serie_img
        serie_item['type'] = ""
        serie_item['plot'] = ""
        serie_list.append(serie_item)

    # add the link to next page
    pager_link = bs_obj.find_all("div", {"id": "pager_List"})
    if len(pager_link) > 0:
        pagers = pager_link[0]
        for pager in pagers.find_all("a"):
            if pager.text == u'下页':
                if pager.has_attr("href"):
                    next_url = pager.get("href")
                    page_num_pattern = re.compile(r'page=(\d+)')
                    page_num = page_num_pattern.findall(next_url)[0]

                    next_item = {}
                    next_item['title'] = "Next Page >>"
                    next_item['url'] = url
                    next_item['mode'] = 105
                    next_item['icon'] = "http://www.dnvod.eu/images/logo.jpg"  # currently using the website icon for categories.
                    next_item['type'] = ""
                    next_item['plot'] = ""
                    next_item['page_num'] = page_num
                    serie_list.append(next_item)
                else:
                    # this should mean the button is disabled, which means the current page is the last one
                    break
            else:
                # other pagers. ignore
                continue

    return serie_list


# log the message according the to log level.
def log_msg(msg, log_level=xbmc.LOGERROR):
    head = ADDON_ID + " - "
    try:
        xbmc.log(head + str(msg.encode("utf-8")), log_level)
    except:
        xbmc.log(head + str(msg), log_level)





