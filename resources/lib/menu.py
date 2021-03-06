# -*- coding: utf-8 -*-


# mode:
#   1: search in the series for episodes
#   2: search in the episode page for the video link
#   3: play the video
#   4: search in the main page for categories - maplestage - currently only support manual list
#   5: search using user input for series - maplestage
# 101: search in the series for episodes - dnvod
# 103: play the video in the episode page - dnvod
# 104: search in the main page for category - dnvod
# 105: search in the category page for series - dnvod
# 106: search using user input for series - dnvod
# 107: list basic options - dnvod
# 203: play the video in the item page - streamhd
# 204: search in the main page for category - streamhd
# 205: search in the category page for the links - streamhd
main_menu = [
    {
        "title": u'多瑙影院',
        "url": u'http://www.dnvod.tv/',
        "mode": 107,
        "poster": "none",
        "icon": 'http://www.dnvod.tv/images/logo.jpg',
        # "fanart":os.path.join(home, '', 'fanart.jpg'),
        "type": "",
        "plot": ""
    },
    {
        "title": u'Maplestage',
        "url": u'http://maplestage.com/',
        "mode": 4,  # for searching for episodes.
        "poster": "none",
        "icon": 'DefaultVideo.png',
        # "fanart":os.path.join(home, '', 'fanart.jpg'),
        "type": "",
        "plot": ""
    },
    {
        "title": u'StreamHD.eu',
        "url": u'http://www.streamhd.eu/',
        "mode": 204,  # for searching for episodes.
        "poster": "none",
        "icon": 'http://www.streamhd.eu/images/logo.png',
        # "fanart":os.path.join(home, '', 'fanart.jpg'),
        "type": "",
        "plot": ""
    },
]

maplestage_menu = [
    {
        "title": u'Search',
        "url": u'http://maplestage.com/v1/search',
        "mode": 5,  # for searching for episodes.
        "poster": "none",
        "icon": 'DefaultVideo.png',
        # "fanart":os.path.join(home, '', 'fanart.jpg'),
        "type": "",
        "plot": ""
    },
    {
        "title": u'夢想的聲音',
        "url": u'http://maplestage.com/show/%E5%A4%A2%E6%83%B3%E7%9A%84%E8%81%B2%E9%9F%B3',
        "mode": 1,  # for searching for episodes.
        "poster": "none",
        "icon": 'DefaultVideo.png',
        # "fanart":os.path.join(home, '', 'fanart.jpg'),
        "type": "",
        "plot": ""
    },
    {
        "title": u'飯局的誘惑',
        "url": u'http://maplestage.com/show/%E9%A3%AF%E5%B1%80%E7%9A%84%E8%AA%98%E6%83%91',
        "mode": 1,  # for searching for episodes.
        "poster": "none",
        "icon": 'DefaultVideo.png',
        # "fanart":os.path.join(home, '', 'fanart.jpg'),
        "type": "",
        "plot": ""
    },
    {
        "title": u'我們的挑戰',
        "url": u'http://maplestage.com/show/%E6%88%91%E5%80%91%E7%9A%84%E6%8C%91%E6%88%B0',
        "mode": 1,
        "poster": "none",
        "icon": 'http://p4.qhimg.com/t017469736020e6f9dd.jpg',
        "type": "",
        "plot": ""
    },
]

dnvod_menu = [
    {
        "title": u'Search',
        "url": u'http://www.dnvod.tv/Movie/Search.aspx',
        "mode": 106,
        "poster": 'none',
        "icon": 'http://www.dnvod.tv/images/logo.jpg',
        "type": "",
        "plot": ""
    },
    {
        "title": u'List Categories',
        "url": u'http://www.dnvod.tv/Movie/Search.aspx',
        "mode": 104,
        "poster": 'none',
        "icon": 'http://www.dnvod.tv/images/logo.jpg',
        "type": "",
        "plot": ""
    }
]
