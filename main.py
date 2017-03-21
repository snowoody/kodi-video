# -*- coding: utf-8 -*-

import sys
# from urllib import urlencode
# from urlparse import parse_qsl
# import xbmcgui
import xbmcplugin
import urlresolver
import xbmcaddon

import xbmc

import sys
import os

from resources import kodi
ADDON_ID = kodi.addon_id
apppath = xbmc.translatePath(os.path.join('special://home/addons/'+ADDON_ID, ''))
print(apppath)
print(sys.path)
sys.path.append(apppath + 'lib')
print(sys.path)
#
# import cfscrape
#
# scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
# # Or: scraper = cfscrape.CloudflareScraper()  # CloudflareScraper inherits from requests.Session
# print scraper.get("http://dnvod.eu").content
#
#
# raise Exception("main die")


from resources.lib import menu
from resources.lib import operations
from resources.lib import maplestage
from resources.lib import dnvod
from resources.lib import streamhd


sys_arg=str(sys.argv[1])
addon = xbmcaddon.Addon(id=ADDON_ID)
parameters = operations.parse_parameters()
try:
    mode = int(parameters["mode"])
except:
    mode = None

# modes:
# first three digits: sites
#   001: http://www.dnvod.eu/
#   002: http://maplestage.com/
#   003: http://www.streamhd.eu/
# last 2 digits: action
#   01: play the video
#   02: search in the item page for video link
#   03: search in the series page for items
#   04: search in the category page for series
#   05: search in the main page for categories


if mode == 1:
    xbmcplugin.setContent(int(sys_arg), "movies")
    url = parameters['url']
    operations.find_ms_episode(url)
elif mode == 2:
    xbmcplugin.setContent(int(sys_arg), "movies")
    url = parameters['url']
    operations.find_ms_episode_link(url)
elif mode == 3:
    url = urlresolver.resolve(parameters['url'])
    video_title = parameters['name']
    if 'videotitle' in parameters:
        video_title = parameters['videotitle']
    operations.play_media(video_title, parameters['icon'], url, "Video", False, video_title)
elif mode == 4:
    menu = menu.maplestage_menu
    operations.add_menu_items(menu)
elif mode == 5:
    xbmcplugin.setContent(int(sys_arg), "movies")
    url = parameters['url']
    menu = maplestage.search_for_series(url)
    operations.add_menu_items(menu)
elif mode == 101:
    xbmcplugin.setContent(int(sys_arg), "movies")
    url = parameters['url']
    menu = dnvod.find_dnvod_episode(url)
    operations.add_menu_items(menu)
elif mode == 103:
    url = parameters['url']
    url = dnvod.get_video_link(url, parameters['resolution'])
    dnvod.play_media(url, parameters['name'], parameters['icon'])
elif mode == 104:
    xbmcplugin.setContent(int(sys_arg), "movies")
    url = parameters['url']
    menu = dnvod.find_dnvod_category(url)
    operations.add_menu_items(menu)
elif mode == 105:
    xbmcplugin.setContent(int(sys_arg), "movies")
    url = parameters['url']
    page_num = '1'
    if 'pagenum' in parameters:
        page_num = parameters['pagenum']
    menu = dnvod.find_dnvod_serie(url, page_num)
    operations.add_menu_items(menu)
elif mode == 203:
    url = parameters['url']
    video_link = streamhd.get_video_link(url)
    streamhd.play_media(video_link, parameters['name'])
elif mode == 204:
    xbmcplugin.setContent(int(sys_arg), "movies")
    url = parameters['url']
    menu = streamhd.find_category(url)
    operations.add_menu_items(menu)
elif mode == 205:
    xbmcplugin.setContent(int(sys_arg), "movies")
    url = parameters['url']
    menu = streamhd.find_video_link(url)
    operations.add_menu_items(menu)
else:
    operations.add_menu_items(menu.main_menu)


