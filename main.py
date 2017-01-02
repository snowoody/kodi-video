# -*- coding: utf-8 -*-

import sys
# from urllib import urlencode
# from urlparse import parse_qsl
# import xbmcgui
import xbmcplugin
import urlresolver
import xbmcaddon
from resources.lib import menu
from resources.lib import operations
from resources.lib import dnvod
from resources.lib import streamhd

sys_arg=str(sys.argv[1])
ADDON_ID = 'plugin.video.streamathome'
addon = xbmcaddon.Addon(id=ADDON_ID)
parameters = operations.parse_parameters()
try:
    mode = int(parameters["mode"])
except:
    mode = None

# url = u'http://maplestage.com/show/蒙面唱將猜猜猜'
# li = xbmcgui.ListItem(u'蒙面唱將猜猜猜', iconImage='DefaultVideo.png')
# li.setProperty('IsPlayable', 'false')
# xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)
#
# # url = urlresolver.resolve('http://javonline.tv/watch/heyzo-1356-satomi-fucked-by-geek-on-xmas-6479.html')
# url = urlresolver.resolve('http://www.dailymotion.com/video/k5njbR3LH6K4WFlcYFK')
# li = xbmcgui.ListItem('other', iconImage='DefaultVideo.png')
# li.setProperty('IsPlayable', 'true')
# xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)
#
# url = urlresolver.resolve('https://www.youtube.com/watch?v=0y-o8LUF8w4')
# li = xbmcgui.ListItem('youtube', iconImage='DefaultVideo.png')
# li.setProperty('IsPlayable', 'true')
# xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)
#
# url = urlresolver.resolve('http://www.dailymotion.com/embed/video/k5ntMyPnuSj641jPwuO')
# li = xbmcgui.ListItem('dailymotion', iconImage='DefaultVideo.png')
# li.setProperty('IsPlayable', 'true')
# xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)
#
#
# xbmcplugin.endOfDirectory(int(sys.argv[1]))

# search for episodes
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


