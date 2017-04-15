# -*- coding: utf-8 -*-

# dnvodPlayer
# adapted from Cameron

import re
import exceptions
from bs4 import BeautifulSoup
import cookielib
import json
import urllib
import urllib2
import xbmc
import xbmcgui

import cfscrape
from ... import kodi
from .. import operations
from .. import menu

ADDON_ID = kodi.addon_id

scraper = cfscrape.create_scraper()

cookies, user_agent = cfscrape.get_cookie_string("http://dnvod.eu")
# cookies, user_agent = cfscrape.get_cookie_string("http://www.dnvod.eu/Movie/Readyplay.aspx?id=7COqHhPaRZg%3d")
operations.log_msg("cookie: " + cookies, xbmc.LOGDEBUG)
operations.log_msg("user_agent: " + user_agent, xbmc.LOGDEBUG)

url2 = 'http://www.dnvod.eu/Movie/Readyplay.aspx?id=7COqHhPaRZg%3d'


class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self,request,response):
        return response

cookie = cookielib.MozillaCookieJar()
# opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cookie), urllib2.HTTPHandler(debuglevel=1))
opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cookie))
urllib2.install_opener(opener)


def add_session_id(url2, cookies):
    request1 = urllib2.Request("http://dnvod.eu")
    response1 = urllib2.urlopen(request1)
    # operations.log_msg("add_session_id 1 : " + response1.read(), xbmc.LOGDEBUG)
    request = urllib2.Request(url2)
    request.add_header("User-Agent", user_agent)
    request.add_header("Cookie", cookies)
    request.add_header('Referer', 'http://dnvod.eu')

    response = urllib2.urlopen(request)
    # operations.log_msg("add_session_id: " + response.read(), xbmc.LOGDEBUG)
    header1 = response.info().headers

    sessionID = ''
    for i in header1:
        m = re.compile(r'ASP.NET_SessionId=(.*); path=/; HttpOnly').findall(i)
        if len(m) > 0:
            sessionID = m[0]
    if sessionID == '':
        operations.log_msg("Cannot find session id in " + '\n'.join(header1))

    print("session id: " + sessionID)

    cookies += "; ASP.NET_SessionId=" + sessionID

    return cookies


cookies = add_session_id(url2, cookies)


# find episodes from series link
def find_dnvod_episode(url):

    request = urllib2.Request(url)
    request.add_header("User-Agent", user_agent)
    request.add_header("Cookie", cookies)
    request.add_header('Referer', url)

    response = urllib2.urlopen(request)

    content = response.read()

    bs_obj = BeautifulSoup(content, "html.parser")
    # find the series title
    title = bs_obj.find_all("div", {"class": "p-r"})[0].ul.h1.text

    # find the series cover picture
    try:
        img = bs_obj.find_all("div", {"id": "spec-list"})[0].ul.li.img.get("src")
        img = "http:" + img
    except exceptions.IndexError:
        img = ""
        operations.log_msg("Cannot find image link")
        operations.log_msg(content)

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
        # episode_item_hd = episode_item.copy()
        # episode_item_hd['resolution'] = "hd"
        # episode_item_hd['title'] += ' - HD'
        # episode_list.append(episode_item_hd)

    return episode_list


# get the playable video link from the episode url
def get_video_link(url, resolution='sd'):

    request = urllib2.Request(url)
    request.add_header("User-Agent", user_agent)
    request.add_header("Cookie", cookies)
    request.add_header('Referer', url)

    response = urllib2.urlopen(request)

    response_content_1 = response.read()

    operations.log_msg(response_content_1)

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
    request = urllib2.Request(url_2, ref)
    request.add_header("User-Agent", user_agent)
    request.add_header("Cookie", cookies + '; dn_config=device=desktop&player=CkPlayer&tech=HLS; _uid=0')
    request.add_header('Referer', url)

    operations.log_msg(request.headers, xbmc.LOGDEBUG)

    response_2 = urllib2.urlopen(request)

    # response_2 = scraper.post(url_2, data={'key': res_key})
    # ref = urllib.urlencode({'key': res_key})
    # request_2 = urllib2.Request(url_2, ref, dnvod_server_header)
    # response_2 = urllib2.urlopen(request_2)
    # real_url = response_2.content
    real_url = response_2.read()
    operations.log_msg("dnvod video links: " + real_url, xbmc.LOGDEBUG)
    url_json = json.loads(real_url)
    real_url = url_json["http"]["provider"]
    hd_url = real_url
    operations.log_msg("video link : " + real_url, xbmc.LOGINFO)
    # links = real_url.split('<>')
    # real_url = links[-1]
    # hd_url = links[-1]
    # print("dnvod link: " + real_url)
    # pattern = re.compile(r'(\d||\d\d||\d\d\d||\d\d\d\d||\d\d\d\d\d||\d\d\d\d\d\d||\d\d\d\d\d\d\d||\d\d\d\d\d\d\d\d)\.mp4')
    # num = re.split(pattern, real_url)
    # hd_url = num[0]+'hd-'+num[1]+'.mp4'+num[2]

    if resolution == 'sd':
        return real_url
    elif resolution == 'hd':
        return hd_url
    else:
        operations.log_msg("Cannot recognized resolution " + resolution + ".")

    return ""


# get the category list from main page
def find_dnvod_category(url):

    request = urllib2.Request(url)
    request.add_header("User-Agent", user_agent)
    request.add_header("Cookie", cookies)
    request.add_header('Referer', url)

    response = urllib2.urlopen(request)

    content = response.read()

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

    request = urllib2.Request(url)
    request.add_header("User-Agent", user_agent)
    request.add_header("Cookie", cookies)
    request.add_header('Referer', url)

    response = urllib2.urlopen(request)

    content = response.read()

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


def play_media(url, title, thumbnail):
    playlist = xbmc.PlayList(1)
    playlist.clear()
    list_item = xbmcgui.ListItem(u'Play 播放', iconImage=thumbnail, thumbnailImage=thumbnail)
    list_item.setInfo(type='video', infoLabels={"Title": title})
    playlist.add(url, listitem=list_item)
    xbmc.Player().play(playlist)


def search_for_serie(url):
    search_str = operations.get_search_input("Search for shows")

    # user did not give any input.
    if not search_str:
        return menu.main_menu   # TODO: add dnvod menu instead

    # http://www.dnvod.eu/Movie/Search.aspx?tags=
    url = url + "?tags=" + urllib.quote_plus(search_str)

    request = urllib2.Request(url)
    request.add_header("User-Agent", user_agent)
    request.add_header("Cookie", cookies)
    request.add_header('Referer', url)

    response = urllib2.urlopen(request)

    content = response.read()

    serie_list = []
    bs_obj = BeautifulSoup(content.decode('utf-8', 'ignore'), "html5lib")
    series = bs_obj.find_all("div", {"class": "r-lb2"})[0].find_all("div", {"class": "cp_a"})
    for serie in series:
        serie_info = serie.find_all("a")[1]
        serie_name = serie_info.get("title")
        serie_url = serie_info.get("href")
        if "http" not in serie_url:
            serie_url = "http://www.dnvod.eu/Movie/" + serie_url
        operations.log_msg("serie url: " + serie_url)

        serie_img = serie.find_all("img")[0].get("src")
        if serie_img.startswith("//"):
            serie_img = "http:" + serie_img
        elif not serie_img.startswith("http"):
            serie_img = "http://www.dnvod.eu/Movie/" + serie_img


        serie_item = {}
        serie_item['title'] = serie_name
        serie_item['url'] = serie_url
        serie_item['mode'] = 101
        serie_item['icon'] = serie_img
        serie_item['type'] = ""
        serie_item['plot'] = ""
        serie_list.append(serie_item)

    return serie_list




