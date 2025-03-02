# -*- coding: utf-8 -*-
import sys
import re
import os

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs

import urllib

from lib.general import *
from lib.rumble_user import RumbleUser
from lib.comments import CommentWindow

import json

BASE_URL = 'https://rumble.com'
PLUGIN_URL = sys.argv[0]
PLUGIN_ID = int(sys.argv[1])
PLUGIN_NAME = PLUGIN_URL.replace('plugin://','')

ADDON = xbmcaddon.Addon()
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')

HOME_DIR = 'special://home/addons/' + PLUGIN_NAME
RESOURCE_DIR = HOME_DIR + 'resources/'
MEDIA_DIR = RESOURCE_DIR + 'media/'

DATE_FORMAT = ADDON.getSetting('date_format')

RUMBLE_USER = RumbleUser()

favorites = xbmcvfs.translatePath(os.path.join(ADDON.getAddonInfo('profile'), 'favorites.dat'))


def favorites_create():
    """
    Creates favorite directory if it doesn't exist.

    The function checks if the directory specified by the addon's profile path exists.
    If it doesn't exist, the function creates the directory. After the directory creation,
    the function waits for 1 millisecond to ensure the directory is fully created before proceeding.

    Parameters:
    None

    Returns:
    None
    """
    addon_data_path = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))

    if os.path.exists(addon_data_path) is False:
        os.mkdir(addon_data_path)

    xbmc.sleep(1)

def to_unicode( text, encoding='utf-8', errors='strict' ):

    """ Forces text to unicode """

    if isinstance(text, bytes):
        return text.decode(encoding, errors=errors)

    return text



def favorites_load(return_string=False):
    """
    Load favorites from file into a variable.

    Parameters:
    return_string (bool): If True, the function returns the favorites as a string.
                           If False (default), the function returns the favorites as a list.

    Returns:
    str or list: The favorites as a string or list, depending on the return_string parameter.
                  If the favorites file does not exist, an empty string or list is returned.
    """

    if os.path.exists(favorites):
        fav_str = open(favorites).read()
        if return_string:
            return fav_str
        if fav_str:
            return json.loads(fav_str)
    else:
        favorites_create()

    # nothing to load, return type necessary
    if return_string:
        return ''

    return []


def get_search_string(heading='', message=''):
    """
    Ask the user for a search string.

    Parameters:
    heading (str): The heading for the keyboard input dialog. Default is an empty string.
    message (str): The message for the keyboard input dialog. Default is an empty string.

    Returns:
    str: The search string entered by the user. If the user cancels the input, the function returns None.
    """
    search_string = None

    keyboard = xbmc.Keyboard(message, heading)
    keyboard.doModal()

    if keyboard.isConfirmed():
        search_string = to_unicode(keyboard.getText())

    return search_string



def home_menu():
    """
    Creates home menu.

    This function generates the main menu options for the Rumble plugin.
    It includes options for searching, favorites, subscriptions, following,
    watch later, battle leaderboard, categories, live streams, and settings.

    Parameters:
    None

    Returns:
    None
    """
    # Search
    add_dir( get_string(137), '', 1, { 'thumb': 'search.png' } )
    # Favorites
    add_dir( get_string(1036), '', 7, { 'thumb': 'favorite.png' } )

    if RUMBLE_USER.has_login_details():
        # Subscriptions
        add_dir( 'Subscriptions', BASE_URL + '/subscriptions', 3, { 'thumb': 'favorite.png' }, {}, 'subscriptions' )
        # Following
        add_dir( 'Following', BASE_URL + '/followed-channels', 3, { 'thumb': 'favorite.png' }, {}, 'following' )
        # Watch Later
        add_dir( 'Watch Later', BASE_URL + '/playlists/watch-later', 3, { 'thumb': 'favorite.png' }, {}, 'playlist' )

    # Battle Leaderboard
    add_dir( get_string(30050), BASE_URL + '/battle-leaderboard/recorded', 3, { 'thumb': 'leader.png' }, {}, 'top' )

    # Categories
    add_dir( get_string(30051), BASE_URL + '/browse', 3, { 'thumb': 'viral.png' }, {}, 'cat_list' )

    # Live Streams
    add_dir( get_string(30052), BASE_URL + '/browse/live', 3, { 'thumb': 'viral.png' }, {}, 'live_stream' )

    # Settings
    add_dir( get_string(5), '', 8, { 'thumb': 'settings.png' } )

    xbmcplugin.endOfDirectory( PLUGIN_ID, cacheToDisc=False )


def search_menu():
    """
    Creates search menu.

    This function generates a menu with search options for videos, channels, and users.
    It adds three items to the menu: one for searching videos, one for searching channels,
    and one for searching users. Each item is a directory that leads to a search page on Rumble.

    Parameters:
    None

    Returns:
    None
    """
    # Search Video
    add_dir( get_string(30100), BASE_URL + '/search/video?q=', 2, { 'thumb': 'search.png' }, {}, 'video' )
    # Search Channel
    add_dir( get_string(30101), BASE_URL + '/search/channel?q=', 2, { 'thumb': 'search.png' }, {}, 'channel' )
    # Search User
    add_dir( get_string(30102), BASE_URL + '/search/channel?q=', 2, { 'thumb': 'search.png' }, {}, 'user' )

    xbmcplugin.endOfDirectory(PLUGIN_ID)



def pagination(url, page, cat, search=False):
    """
    List directory items and show pagination.

    Parameters:
    url (str): The base URL for the directory.
    page (int): The current page number.
    cat (str): The category of the directory.
    search (str, optional): The search string. Defaults to False.

    Returns:
    None. This function does not return any value.
    """
    if url > '':

        page = int(page)
        page_url = url
        paginated = True

        if page == 1:
            if search:
                page_url = url + search
        elif search and cat == 'video':
            page_url = url + search + "&page=" + str( page )
        elif cat in {'channel', 'cat_video', 'user', 'other', 'subscriptions', 'live_stream' }:
            page_url = url + "?page=" + str( page )

        if cat in { 'following', 'top', 'cat_list' }:
            paginated = False

        amount = list_rumble( page_url, cat )

        if paginated and amount > 15 and page < 10:

            # for next page
            page = page + 1

            name = get_string(30150) + " " + str( page )
            list_item = xbmcgui.ListItem(name)

            link_params = {
                'url': url,
                'mode': '3',
                'name': name,
                'page': str( page ),
                'cat': cat,
            }

            link = build_url( link_params )

            if search and cat == 'video':
                link = link + "&search=" + urllib.parse.quote_plus(search)

            xbmcplugin.addDirectoryItem(PLUGIN_ID, link, list_item, True)

    xbmcplugin.endOfDirectory(PLUGIN_ID)



def get_image(data, image_id):
    """
    Method to get an image from scraped page's CSS from the image ID.

    Parameters:
    data (str): The scraped HTML page content.
    image_id (int): The ID of the image to find.

    Returns:
    str: The URL of the image if found, otherwise an empty string.

    The function uses a regular expression to search for the CSS rule for the given image ID
    and extracts the URL from the 'background-image' property.
    """
    image_re = re.compile(
        "i.user-image--img--id-" + str(image_id) + ".+?{\s*background-image: url(.+?);",
        re.MULTILINE|re.DOTALL|re.IGNORECASE
    ).findall(data)

    if image_re != []:
        image = str(image_re[0]).replace('(', '').replace(')', '')
    else:
        image = ''

    return image
def get_video_id(url):
    """
    Extracts the video ID from a Rumble video URL.

    This function fetches the HTML content of the given Rumble video URL and uses
    a regular expression to extract the video ID from the embed URL found in the page.

    Args:
        url (str): The Rumble video URL from which to extract the video ID.

    Returns:
        str or False: The extracted video ID if found, or False if no video ID could be extracted.

    Raises:
        Any exceptions raised by the request_get function (e.g., network errors).

    Example:
        >>> video_id = get_video_id("https://rumble.com/v2jqx56-example-video.html")
        >>> print(video_id)
        'v2jqx56'
    """

    data = request_get(url)

    video_id = re.compile(
        ',\"embedUrl\":\"' + BASE_URL + '/embed/(.*?)\/\",',
        re.MULTILINE|re.DOTALL|re.IGNORECASE
    ).findall(data)

    if video_id:
        return video_id[0]
    return False



def list_rumble(url, cat):
    """
    Method to get and display items from Rumble.

    Parameters:
    url (str): The URL from which to retrieve the items.
    cat (str): The category of items to retrieve.

    Returns:
    int: The number of items retrieved and displayed.
    """
    amount = 0
    headers = None

    if 'subscriptions' in url or cat == 'following':
        # make sure there is a session
        # result is stored in a cookie
        RUMBLE_USER.has_session()

    data = request_get(url, None, headers)

    # Fix for favorites & search
    if cat in { 'other', 'channel' } and '/c/' in url:
        cat = 'channel_video'

    if 'search' in url:
        if cat == 'video':
            amount = dir_list_create( data, cat, 'video', True, 1 )
        else:
            amount = dir_list_create( data, cat, 'channel', True )
    elif cat in { 'subscriptions', 'cat_video', 'live_stream', 'playlist' }:
        amount = dir_list_create( data, cat, cat, False, 2 )
    elif cat in { 'channel', 'top', 'other' }:
        amount = dir_list_create( data, cat, 'video', False, 2 )
    elif cat in { 'channel_video', 'user' }:
        amount = dir_list_create( data, cat, 'channel_video', False, 2 )
    elif cat == 'following':
        amount = dir_list_create( data, cat, 'following', False, 2 )
    elif cat == 'cat_list':
        amount = dir_list_create( data, cat, cat, False )

    return amount



def dir_list_create( data, cat, video_type='video', search = False, play=0 ):

    """
    Create and display directory list based on the given type.

    Parameters:
    data (str): The HTML data containing the directory list items.
    cat (str): The category of the directory list items.
    video_type (str, optional): The type of the directory list items. Defaults to 'video'.
    search (bool, optional): Whether the function is being used for searching. Defaults to False.
    play (int, optional): The play mode for the directory list items. Defaults to 0.

    Returns:
    int: The number of directory list items created.
    """

    amount = 0

    one_line_titles = ADDON.getSetting('one_line_titles') == 'true'

    if video_type == 'video':
        videos = re.compile(r'href=\"([^\"]+)\"><div class=\"(?:[^\"]+)\"><img\s*class=\"video-item--img\"\s*src=\"([^\"]+)\"\s*alt=\"(?:[^\"]+)\"\s*>(?:<span class=\"video-item--watching\">[^\<]+</span>)?(?:<div class=video-item--overlay-rank>(?:[0-9]+)</div>)?</div><(?:[^\>]+)></span></a><div class=\"video-item--info\"><time class=\"video-item--meta video-item--time\" datetime=(.+?)-(.+?)-(.+?)T(?:.+?) title\=\"(?:[^\"]+)\">(?:[^\<]+)</time><h3 class=video-item--title>(.+?)</h3><address(?:[^\>]+)><a rel=author class=\"(?:[^\=]+)=(.+?)><div class=ellipsis-1>(.+?)</div>', re.MULTILINE|re.DOTALL|re.IGNORECASE).findall(data)
        if videos:
            amount = len(videos)
            for link, img, year, month, day, title, channel_link, channel_name in videos:

                info_labels = {}

                if '<svg' in channel_name:
                    channel_name = channel_name.split('<svg')[0] + " (Verified)"

                info_labels[ 'year' ] = year

                video_title = '[B]' + clean_text( title ) + '[/B]'
                video_title += ' - ' if one_line_titles else '\n'
                video_title += '[COLOR gold]' + channel_name + '[/COLOR] - [COLOR lime]' + get_date_formatted( DATE_FORMAT, year, month, day ) + '[/COLOR]'

                images = { 'thumb': str(img), 'fanart': str(img) }

                #open get url and open player
                add_dir( video_title, BASE_URL + link, 4, images, info_labels, cat, False, True, play, { 'name' : channel_link, 'subscribe': True }  )

    elif video_type in { 'cat_video', 'subscriptions', 'live_stream', 'channel_video', 'playlist' }:

        if video_type == 'live_stream':
            videos_regex = r'<div class=\"thumbnail__grid\"\s*role=\"list\">(.*)<nav class=\"paginator\">'
        elif video_type == 'playlist':
            videos_regex = r'<ol\s*class=\"videostream__list\"(?:[^>]+)>(.*)</ol>'
        else:
            videos_regex = r'<ol\s*class=\"thumbnail__grid\">(.*)</ol>'
        videos = re.compile(videos_regex, re.DOTALL|re.IGNORECASE).findall(data)

        if videos:
            if video_type == 'playlist':
                videos = videos[0].split('"videostream videostream__list-item')
            else:
                videos = videos[0].split('"videostream thumbnail__grid-')

            videos.pop(0)
            amount = len(videos)
            for video in videos:

                video_title = ''
                images = {}
                info_labels = {}
                subscribe_context = False

                title = re.compile(r'<h3(?:[^\>]+)?>(.*)</h3>', re.DOTALL|re.IGNORECASE).findall(video)
                link = re.compile(r'<a\sclass="videostream__link link"\sdraggable="false"\shref="([^\"]+)">', re.DOTALL|re.IGNORECASE).findall(video)
                img = re.compile(r'<img\s*class=\"thumbnail__image\"\s*draggable=\"false\"\s*src=\"([^\"]+)\"', re.DOTALL|re.IGNORECASE).findall(video)

                if title:
                    video_title = '[B]' + clean_text( title[0] ) + '[/B]'
                if 'videostream__status--live' in video:
                    video_title += ' [COLOR red](Live)[/COLOR]'
                if 'videostream__status--upcoming' in video:
                    video_title += ' [COLOR yellow](Upcoming)[/COLOR]'

                channel_name = re.compile(r'<span\sclass="channel__name(?:[^\"]+)" title="(?:[^\"]+)">([^\<]+)</span>(\s*<svg class=channel__verified)?', re.DOTALL|re.IGNORECASE).findall(video)
                channel_link = re.compile(r'<a\s*rel=\"author\"\s*class=\"channel__link\slink\s(?:[^\"]+)\"\s*href=\"([^\"]+)\"\s*>', re.DOTALL|re.IGNORECASE).findall(video)

                if channel_name:

                    video_title += ' - ' if one_line_titles else '\n'
                    video_title += '[COLOR gold]' + clean_text( channel_name[0][0] )
                    if channel_name[0][1]:
                        video_title += " (Verified)"
                    video_title += '[/COLOR]'

                    if channel_link:
                        subscribe_context = { 'name' : channel_link[0], 'subscribe': True }

                date_time = re.compile(r'<time\s*class=\"(?:[^\"]+)\"\s*datetime=\"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})-(\d{2}):(\d{2})\"', re.DOTALL|re.IGNORECASE).findall(video)

                if date_time:
                    info_labels[ 'year' ] = date_time[0][0]
                    video_title += ' - [COLOR lime]' + get_date_formatted( DATE_FORMAT, date_time[0][0], date_time[0][1], date_time[0][2] ) + '[/COLOR]'

                if img:
                    images = { 'thumb': str(img[0]), 'fanart': str(img[0]) }

                duration = re.compile(r'videostream__status--duration\"\s*>([^<]+)</div>', re.DOTALL|re.IGNORECASE).findall(video)

                if duration:
                    info_labels[ 'duration' ] = duration_to_secs( duration[0].strip() )

                #open get url and open player
                add_dir( video_title, BASE_URL + link[0], 4, images, info_labels, cat, False, True, play, subscribe_context  )

        return amount

    elif video_type == 'cat_list':
        cat_list = re.compile(r'<a\s*class=\"category__link link\"\s*href=\"([^\"]+)\"\s*>\s*<img\s*class=\"category__image\"\s*src=\"([^\"]+)\"\s*alt=(?:[^\>]+)>\s*<strong class=\"category__title\">([^\<]+)</strong>', re.DOTALL|re.IGNORECASE).findall(data)
        if cat_list:
            amount = len(cat_list)
            for link, img, title in cat_list:

                cat = 'channel_video'
                images = { 'thumb': str(img), 'fanart': str(img) }

                #open get url and open player
                add_dir( clean_text( title ), BASE_URL + link.strip() + '/videos', 3, images, {}, cat )

    elif video_type == 'following':

        videos_regex = r'<ol\s*class=\"followed-channels__list\">(.*)</ol>'
        videos = re.compile(videos_regex, re.DOTALL|re.IGNORECASE).findall(data)
        if videos:
            videos = videos[0].split('"followed-channel flex items-')

            videos.pop(0)
            amount = len(videos)
            for video in videos:

                video_title = ''
                images = {}

                title = re.compile(r'<span\s*class=\"line-clamp-2\">([^<]+)<\/span>', re.DOTALL|re.IGNORECASE).findall(video)
                followers = re.compile(r'<div\s*class=\"followed-channel__followers(?:[^\"]+)\">([^<]+)</div>', re.DOTALL|re.IGNORECASE).findall(video)
                link = re.compile(r'<a\s*class=\"(?:[^\"]+)\"\s*href=\"(\/(?:c|user)\/[^\"]+)\"\s*>', re.DOTALL|re.IGNORECASE).findall(video)
                img = re.compile(r'<(?:img|span)\s*class=\"channel__avatar([^\"]+)\"\s*(?:src=\"([^\"]+)\")?', re.DOTALL|re.IGNORECASE).findall(video)

                if title:
                    video_title = '[B]' + clean_text( title[0] ) + '[/B]'

                if '<use href="#channel_verified" />' in video:
                    video_title += ' [COLOR gold](Verified)[/COLOR]'

                link = link[0] if link else ""

                if img:
                    if 'channel__letter' in img[0][0]:
                        if title:
                            image_url = MEDIA_DIR + 'letters/' + title[0][0].lower() + '.png'
                        else:
                            image_url = ''
                    else:
                        image_url = img[0][1]

                    images = { 'thumb': str(image_url), 'fanart': str(image_url) }

                    if 'channel__live' in img[0][0]:
                        video_title += ' [COLOR red](Live)[/COLOR]'

                if followers:
                    video_title += ' - ' if one_line_titles else '\n'
                    video_title += '[COLOR green]' + followers[0].strip() + '[/COLOR]'

                cat = 'user'
                if '/user/' not in link:
                    cat = 'channel_video'

                #open get url and open player
                add_dir( video_title, BASE_URL + link, 3, images, {}, cat, True, True, play, { 'name' : link, 'subscribe': False } )

    else:

        channels_regex = r'<div class="main-and-sidebar">(.*)<nav class="paginator">'
        channels = re.compile(channels_regex, re.DOTALL|re.IGNORECASE).findall(data)
        if channels:
            channels = channels[0].split('<article')

            channels.pop(0)
            amount = len(channels)
            for channel in channels:

                link = re.compile(r'<a\shref=([^\s]+)\sclass=\"(?:[^\"]+)\">', re.DOTALL|re.IGNORECASE).findall(channel)
                link = link[0] if link else ""
                xbmc.log( json.dumps(link), xbmc.LOGWARNING )
                # split channel and user
                if search:
                    if cat == 'channel':
                        if '/c/' not in link:
                            continue
                    else:
                        if '/user/' not in link:
                            continue

                images = {}

                channel_name = re.compile(r'<span\sclass=\"block\struncate\">([^<]+)<\/span>', re.DOTALL|re.IGNORECASE).findall(channel)
                channel_name = channel_name[0] if channel_name else ""

                is_verified = re.compile(r'<title>Verified</title>', re.DOTALL|re.IGNORECASE).findall(channel)
                is_verified = True if is_verified else False

                followers = re.compile(r'<span\sclass=\"(?:[^\"]+)\">\s+([^&]+)&nbsp;Follower(?:s)?\s+</span>', re.DOTALL|re.IGNORECASE).findall(channel)
                followers = followers[0] if followers else "0"

                img_id = re.compile(r'user-image--img--id-([^\s]+)\s', re.DOTALL|re.IGNORECASE).findall(channel)
                img_id = img_id[0] if img_id else ""

                if img_id:
                    img = str( get_image( data, img_id ) )
                else:
                    img = MEDIA_DIR + 'letters/' + channel_name[0] + '.png'

                images = { 'thumb': str(img), 'fanart': str(img) }

                video_title = '[B]' + channel_name + '[/B]'
                if is_verified:
                    video_title += ' [COLOR gold](Verified)[/COLOR]'
                video_title += ' - ' if one_line_titles else '\n'
                video_title += '[COLOR palegreen]' + followers + '[/COLOR] [COLOR yellow]' + get_string(30156) + '[/COLOR]'

                #open get url and open player
                add_dir( video_title, BASE_URL + link, 3, images, {}, cat, True, True, play, { 'name' : link, 'subscribe': True } )

    return amount

def get_playlist_video_id(url):
    """
    Extracts the playlist video ID from a given URL.

    This function retrieves the HTML content of the provided URL and uses a regular
    expression to find the 'data-id' attribute, which represents the playlist video ID.

    Args:
        url (str): The URL of the playlist video page.

    Returns:
        str or False: The extracted playlist video ID if found, or False if not found.

    Note:
        This function is useful for adding videos to playlists, as it provides the
        necessary ID for such operations.
    """

    data = request_get(url)

    # gets embed id from embed url
    video_id = re.compile(
        'data-id=\"([0-9]+)\"',
        re.MULTILINE|re.DOTALL|re.IGNORECASE
    ).findall(data)

    if video_id:
        return video_id[0]
    return False


def resolver(url):
    """
    Resolves a Rumble video URL and returns the direct media link.

    This function takes a Rumble video URL, extracts the video ID, and then fetches
    available quality options from Rumble's API. It selects the appropriate media URL
    based on the user's playback method preference.

    Args:
        url (str): The Rumble video URL to resolve.

    Returns:
        str or False: The resolved direct media URL if successful, False otherwise.

    Behavior:
        - Playback method 0 (high auto): Selects the highest quality automatically.
        - Playback method 1 (low auto): Selects the lowest quality automatically.
        - Playback method 2 (quality select): Prompts the user to choose the quality.

    Notes:
        - Supports various video qualities: 1080p, 720p, 480p, 360p, and HLS.
        - Handles m3u8 (HLS) streams separately.
        - Uses regex to parse the API response for video URLs.
        - Replaces escaped forward slashes in the final URL.

    Dependencies:
        - Requires the ADDON settings for 'playbackMethod'.
        - Uses external functions: get_video_id, request_get.
        - May import lib.m3u8 for HLS stream processing.
    """

    # playback options - 0: high auto, 1: low auto, 2: quality select
    playback_method = int( ADDON.getSetting('playbackMethod') )

    media_url = False

    if playback_method > 0:
        urls = []

    video_id = get_video_id( url )

    if video_id:

        # use site api to get video urls
        # TODO: use as dict / array instead of using regex to get URLs
        data = request_get(BASE_URL + '/embedJS/u3/?request=video&ver=2&v=' + video_id)
        sizes = [ '1080', '720', '480', '360', 'hls' ]

        for quality in sizes:

            # get urls for quality
            matches = re.compile(
                '"' + quality + '".+?url.+?:"(.*?)"',
                re.MULTILINE|re.DOTALL|re.IGNORECASE
            ).findall(data)

            if matches:
                if playback_method > 0:
                    urls.append(( quality, matches[0] ))
                else:
                    media_url = matches[0]
                    break

        # if not automatically selecting highest quality
        if int( playback_method ) > 0:

            # m3u8 check
            if len( urls ) == 1 and '.m3u8' in urls[0][1]:
                from lib.m3u8 import m3u8
                m3u8_handler = m3u8()
                urls = m3u8_handler.process( request_get( urls[0][1] ) )

            # reverses array - small to large
            if playback_method == 1:
                urls = urls[::-1]
                media_url = urls[0][1]


            # quality select
            elif playback_method == 2:

                if len(urls) > 0:

                    if len(urls) == 1:
                        # if only one available, no point asking
                        selected_index = 0
                    else:
                        selected_index = xbmcgui.Dialog().select(
                            'Select Quality', [(sourceItem[0] or '?') for sourceItem in urls]
                        )

                    if selected_index != -1:
                        media_url = urls[selected_index][1]

    if media_url:
        media_url = media_url.replace('\/', '/')

    return media_url


def play_video(name, url, thumb, play=2):
    """
    Resolves and plays a video in Kodi.

    This function takes a video URL, resolves it to a playable stream, and initiates
    playback in Kodi. It handles different playback methods and applies user settings.

    Args:
        name (str): The title of the video to be played.
        url (str): The initial URL of the video, which will be resolved.
        thumb (str): The URL or path of the video's thumbnail image.
        play (int, optional): The playback method to use. Defaults to 2.
                              1: Immediate playback using xbmc.Player().
                              2: Deferred playback using xbmcplugin.setResolvedUrl().

    Behavior:
        - Resolves the video URL using the resolver() function.
        - Applies HTTP protocol if specified in addon settings.
        - Creates a ListItem with video metadata and artwork.
        - Initiates playback based on the 'play' parameter.
        - Displays an error dialog if the video URL cannot be resolved.

    Note:
        This function relies on Kodi's xbmc and xbmcplugin modules for playback,
        as well as addon-specific settings and helper functions.
    """

    # get video link
    url = resolver(url)

    if url:

        # Use HTTP
        if ADDON.getSetting('useHTTP') == 'true':
            url = url.replace('https://', 'http://', 1)

        list_item = xbmcgui.ListItem(name, path=url)
        list_item.setArt({'icon': thumb, 'thumb': thumb})

        info_labels={ 'Title': name, 'plot': '' }

        item_set_info( list_item, info_labels )

        if play == 1:
            xbmc.Player().play(item=url, listitem=list_item)
        elif play == 2:
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, list_item)

    else:
        xbmcgui.Dialog().ok( 'Error', 'Video not found' )


def search_items(url, cat):
    """
    Performs a search on Rumble based on user input.

    This function prompts the user for a search string, encodes it,
    and then calls the pagination function to display search results.

    Parameters:
    url (str): The base URL for the search operation.
    cat (str): The category of the search (e.g., 'video', 'channel').

    Returns:
    None: This function doesn't return a value, but it triggers
          the display of search results through the pagination function.

    Note:
    If the user cancels the search input, the function returns early
    without performing a search.
    """
    search_str = get_search_string(heading="Search")

    if not search_str:
        return

    title = urllib.parse.quote_plus(search_str)

    pagination(url, 1, cat, title)


def favorites_show():
    """
    Displays the user's favorite items in the Kodi interface.

    This function loads the user's favorites and creates a directory listing
    for each favorite item. If favorites exist, it displays them as selectable
    items in the Kodi interface. If no favorites are found, it shows a dialog
    informing the user.

    The function handles the following operations:
    1. Loads favorite data using favorites_load().
    2. Iterates through each favorite item if any exist.
    3. Extracts relevant information for each favorite (name, URL, mode, images, etc.).
    4. Adds each favorite as a directory item in the Kodi interface using add_dir().
    5. Finalizes the directory listing or shows a "no favorites" dialog.

    The function uses a try-except block to handle any exceptions that may occur
    during the process, ensuring that the directory listing is properly ended
    even if an error occurs.

    Returns:
        None

    Raises:
        No exceptions are raised explicitly, but any occurring exceptions
        are caught and handled to ensure proper function termination.

    Dependencies:
        - favorites_load(): Function to load favorite data
        - add_dir(): Function to add directory items to Kodi interface
        - xbmcplugin.endOfDirectory(): Kodi function to finalize directory listing
        - xbmcgui.Dialog().ok(): Kodi function to display dialog boxes
        - get_string(): Function to retrieve localized strings
    """

    data = favorites_load()

    try:

        amount = len(data)
        if amount > 0:
            for i in data:
                name = i[0]
                url = i[1]
                mode = i[2]
                images = { 'thumb': str(i[3]), 'fanart': str(i[4]) }
                info_labels = { 'plot': str(i[5]) }
                cat = i[6]
                folder = ( i[7] == 'True' )
                play = i[8]

                add_dir( name, url, mode, images, info_labels, cat, folder, True, int(play) )

            xbmcplugin.endOfDirectory(PLUGIN_ID)
        else:
            xbmcgui.Dialog().ok( get_string(14117), get_string(30155) )

    except Exception:

        xbmcplugin.endOfDirectory(PLUGIN_ID)


def favorite_add(name, url, fav_mode, thumb, fanart, plot, cat, folder, play):
    """
    Add a new favorite item to the favorites list.

    This function adds a new favorite item with the provided details to the favorites list.
    It loads the existing favorites, appends the new item, and saves the updated list.
    Finally, it notifies the user that the item has been added to favorites.

    Parameters:
    name (str): The name or title of the favorite item.
    url (str): The URL associated with the favorite item.
    fav_mode (int): The mode number for the favorite item.
    thumb (str): The URL or path to the thumbnail image for the favorite.
    fanart (str): The URL or path to the fanart image for the favorite.
    plot (str): A brief description or plot summary of the favorite item.
    cat (str): The category of the favorite item.
    folder (str): A string indicating whether the item is a folder ('True' or 'False').
    play (str): A string representing the play mode for the favorite item.

    Returns:
    None

    Side effects:
    - Updates the favorites file with the new item.
    - Displays a notification to the user.
    """
    data = favorites_load()
    data.append((name, url, fav_mode, thumb, fanart, plot, cat, folder, play))
    fav_file = open( favorites, 'w' )
    fav_file.write(json.dumps(data))
    fav_file.close()

    notify( get_string(30152), name, thumb )



def favorite_remove(name):
    """
    Remove a favorite item from the favorites list based on its name.

    This function searches for a favorite item with the given name in the favorites list,
    removes it if found, and updates the favorites file. It then notifies the user about
    the removal.

    Parameters:
    name (str): The name of the favorite item to be removed.

    Returns:
    None

    Note:
    - This function currently loops through all favorites to find a match.
    - Future improvements may include using a more unique identifier and a more
      efficient removal method.
    """
    # TODO: remove via something more unique instead
    # TODO: remove via a method that doesn't require to loop through all favorites

    data = favorites_load()

    if data:
        for index in range(len(data)):
            if data[index][0] == name:
                del data[index]
                fav_file = open(favorites, 'w')
                fav_file.write(json.dumps(data))
                fav_file.close()
                break

    notify(get_string(30154), name)



def favorites_import():
    """
    Import favorites from the original 'plugin.video.rumble.matrix' addon to the current addon.

    This function is designed to migrate user favorites after a plugin name change from the original fork.
    It performs the following steps:
    1. Prompts the user for confirmation before proceeding with the import.
    2. Ensures the favorites directory for the current addon exists.
    3. Attempts to locate and read the favorites file from the original addon.
    4. If found, copies the content to the current addon's favorites file.
    5. Notifies the user of the import result.

    The function uses Kodi's xbmcgui, xbmcvfs, and os modules for dialog, file operations, and path handling.

    Returns:
        None

    Side effects:
        - May overwrite the current addon's favorites file.
        - Displays Kodi dialog boxes and notifications.

    Raises:
        No exceptions are explicitly raised, but file I/O operations may raise exceptions.

    Note:
        This function assumes the existence of helper functions like favorites_create() and notify().
        The 'favorites' variable should be defined elsewhere in the code, representing the path
        to the current addon's favorites file.
    """

    if not xbmcgui.Dialog().yesno(
        'Import Favorites',
        'This will replace the favorites with the plugin.video.rumble.matrix version.\nProceed?',
        nolabel='Cancel',
        yeslabel='Ok'
    ):
        return

    # Make sure path exists
    favorites_create()

    # Load matrix favorites
    rumble_matrix_dir = xbmcvfs.translatePath(
        os.path.join('special://home/userdata/addon_data/plugin.video.rumble.matrix', 'favorites.dat')
    )

    if os.path.exists(rumble_matrix_dir):
        rumble_matrix = open(rumble_matrix_dir).read()

        if rumble_matrix:
            with open(favorites, 'w') as fav_file:
                fav_file.write(rumble_matrix)

            notify('Imported Favorites')
            return

    notify('Favorites Not Found')



def login_session_reset():
    """
    Force a reset of the current Rumble user session.

    This function performs the following actions:
    1. Resets the session details for the current Rumble user.
    2. Displays a notification to the user indicating that the session has been reset.

    The function does not take any parameters and does not return any values.

    Note:
    - This function assumes the existence of a global RUMBLE_USER object with a
      reset_session_details() method.
    - It also assumes the availability of notify() and get_string() functions for
      user notifications.

    Usage:
    Call this function when you need to forcibly clear the current user's session,
    such as for logout operations or troubleshooting authentication issues.
    """

    RUMBLE_USER.reset_session_details()
    # Session Reset
    notify( get_string(30200) )

def login_test():
    """
    Reset the current session and test the Rumble user login.

    This function performs the following steps:
    1. Resets the current session details.
    2. Checks if login details are available.
    3. Attempts to log in if details are present.
    4. Notifies the user of the login result.

    The function uses the RUMBLE_USER object to manage session details and perform login operations.
    It also uses the notify() function to display messages to the user.

    Returns:
        None

    Side Effects:
        - Resets the current user session.
        - Displays a notification to the user about the login status.

    Notifications:
        - Login Success (string ID: 30201): Displayed when login is successful.
        - Login Failed (string ID: 30202): Displayed when login fails.
        - No details detected (string ID: 30203): Displayed when no login details are found.

    Dependencies:
        - RUMBLE_USER: An object with methods for managing user sessions and login.
        - notify(): Function to display notifications to the user.
        - get_string(): Function to retrieve localized string resources.

    Usage:
        This function is typically called to test user authentication or verify login status.
        It can be used after changing login credentials or for troubleshooting login issues.
    """

    RUMBLE_USER.reset_session_details()

    if RUMBLE_USER.has_login_details():
        if RUMBLE_USER.login():
            # Login Success
            notify( get_string(30201) )
        else:
            # Login Failed
            notify( get_string(30202) )
    else:
        # No details detected
        notify( get_string(30203) )

def subscribe( name, action ):

    """ Attempts to (un)subscribe to rumble channel """

    # make sure we have a session
    if RUMBLE_USER.has_session():

        action_type = False
        if '/user/' in name:
            name = name.replace( '/user/', '' )
            action_type = 'user'
        elif '/c/' in name:
            name = name.replace( '/c/', '' )
            action_type = 'channel'

        if action_type:

            # subscribe to action
            data = RUMBLE_USER.subscribe( action, action_type, name )

            if data:

                # Load data from JSON
                data = json.loads(data)

                # make sure everything looks fine
                if data.get( 'user', False ) and data.get( 'data', False ) \
                    and data[ 'user' ][ 'logged_in' ] and data[ 'data' ][ 'thumb' ]:

                    if action == 'subscribe':
                        notify( 'Subscribed to ' + name, None, data[ 'data' ][ 'thumb' ] )
                    else:
                        notify( 'Unubscribed to ' + name, None, data[ 'data' ][ 'thumb' ] )

                    return True

    notify( 'Unable to to perform action' )

    return False


def add_dir( name, url, mode, images = {}, info_labels = {}, cat = '', folder=True, fav_context=False, play=0, subscribe_context=False ):

    """ Adds directory items """

    art_dict = {
        'thumb': images.get( 'thumb', HOME_DIR + 'icon.png' ),
        'fanart': images.get( 'fanart', HOME_DIR + 'fanart.png' ),
    }

    # set default image location to MEDIA_DIR
    for art_type, art_loc in art_dict.items():
        if art_loc:
            if not art_loc.startswith( HOME_DIR ) and \
                not art_loc.startswith( 'http' ) and \
                not art_loc.startswith( '\\' ):
                art_dict[ art_type ] = MEDIA_DIR + art_dict[ art_type ]

    link_params = {
        'url': url,
        'mode': str( mode ),
        'name': name,
        'thumb': art_dict[ 'thumb' ],
        'fanart': art_dict[ 'fanart' ],
        'plot': info_labels.get( 'plot', '' ),
        'cat': cat,
    }

    context_menu = []

    if play:
        link_params['play'] = str( play )

    link = build_url( link_params )

    list_item = xbmcgui.ListItem( name )
    if folder:
        list_item.setArt({'icon': 'DefaultFolder.png', 'thumb': art_dict[ 'thumb' ]})
    else:
        list_item.setArt({'icon': 'DefaultVideo.png', 'thumb': art_dict[ 'thumb' ]})
        xbmcplugin.setContent(PLUGIN_ID, 'videos')

    if play == 2 and mode == 4:
        list_item.setProperty('IsPlayable', 'true')
        context_menu.append((get_string(30158), 'Action(Queue)'))

        if RUMBLE_USER.has_login_details():
            # need to get current
            params=get_params()
            current_url = params.get( 'url', None )

            if '/playlists/watch-later' in current_url:
                # delete watch later context
                context_menu.append(('Delete from Watch Later','RunPlugin(%s)' % build_url( {'mode': '12','url': url, 'cat':'delete'} )))
            else:
                # add watch later context
                context_menu.append(('Add to Watch Later','RunPlugin(%s)' % build_url( {'mode': '12','url': url, 'cat':'add'} )))

    info_labels['title'] = name
    if play:
        # adds information context menu
        info_labels['mediatype'] = 'tvshow'

    item_set_info( list_item, info_labels )

    list_item.setProperty( 'fanart_image', art_dict[ 'fanart' ] )

    if RUMBLE_USER.has_login_details():

        if subscribe_context:
            if subscribe_context['subscribe']:
                context_menu.append(('Subscribe to ' + subscribe_context['name'],'RunPlugin(%s)' % build_url( {'mode': '11','name': subscribe_context['name'], 'cat': 'subscribe'} )))
            else:
                context_menu.append(('Unsubscribe to ' + subscribe_context['name'],'RunPlugin(%s)' % build_url( {'mode': '11','name': subscribe_context['name'], 'cat': 'unsubscribe'} )))

        if play == 2 and mode == 4:
            context_menu.append(('Comments','RunPlugin(%s)' % build_url( {'mode': '13','url': url} )))

    if fav_context:

        favorite_str = favorites_load( True )

        try:
            name_fav = json.dumps(name)
        except Exception:
            name_fav = name

        try:

            # checks fav name via string (I do not like how this is done, so will redo in future)
            if name_fav in favorite_str:
                context_menu.append((get_string(30153),'RunPlugin(%s)' % build_url( {'mode': '6','name': name} )))
            else:
                fav_params = {
                    'url': url,
                    'mode': '5',
                    'name': name,
                    'thumb': art_dict[ 'thumb' ],
                    'fanart': art_dict[ 'fanart' ],
                    'plot': info_labels.get( 'plot', '' ),
                    'cat': cat,
                    'folder': str(folder),
                    'fav_mode': str(mode),
                    'play': str(play),
                }

                context_menu.append((get_string(30151),'RunPlugin(%s)' %build_url( fav_params )))
        except Exception:
            pass

    if context_menu:
        list_item.addContextMenuItems(context_menu)

    xbmcplugin.addDirectoryItem(handle=PLUGIN_ID, url=link, listitem=list_item, isFolder=folder)

def playlist_manage( url, action="add" ):

    """ Adds to Rumble's Playlist """
    video_id = get_playlist_video_id( url )

    if video_id:
        if action == "add":
            RUMBLE_USER.playlist_add_video( video_id )
            message = "Added to playlist"
        else:
            RUMBLE_USER.playlist_delete_video( video_id )
            message = "Deleted from playlist"
    else:
        if action == "add":
            message = "Cannot add to playlist"
        else:
            message = "Cannot delete from playlist"

    notify( message, "Playlist" )

def comments_show( url ):

    """ Retrieves and shows video's comments in a modal """

    video_id = get_video_id( url )

    if video_id:
        win = CommentWindow(
            'addon-rumble-comments.xml',
            ADDON.getAddonInfo('path'),
            'default',
            video_id=video_id
        )
        win.doModal()
        del win
    else:
        notify( "Cannot find comments", "Comments" )

def main():
    """
    Main method to start the plugin.

    Parameters:
    params (dict): A dictionary containing the parameters passed to the plugin.

    Returns:
    None
    """

    params = get_params()

    mode = int(params.get('mode', 0))
    page = int(params.get('page', 1))
    play = int(params.get('play', 0))
    fav_mode = int(params.get('fav_mode', 0))

    url = params.get('url', None)
    if url:
        url = urllib.parse.unquote_plus(url)

    name = params.get('name', None)
    if name:
        name = urllib.parse.unquote_plus(name)

    thumb = params.get('thumb', None)
    if thumb:
        thumb = urllib.parse.unquote_plus(thumb)

    fanart = params.get('fanart', None)
    if fanart:
        fanart = urllib.parse.unquote_plus(fanart)

    plot = params.get('plot', None)
    if plot:
        plot = urllib.parse.unquote_plus(plot)

    subtitle = params.get('subtitle', None)
    if subtitle:
        subtitle = urllib.parse.unquote_plus(subtitle)

    cat = params.get('cat', None)
    if cat:
        cat = urllib.parse.unquote_plus(cat)

    search = params.get('search', None)
    if search:
        search = urllib.parse.unquote_plus(search)

    folder = params.get('folder', None)
    if folder:
        folder = urllib.parse.unquote_plus(folder)

    if mode == 0:
        home_menu()
    elif mode == 1:
        search_menu()
    elif mode == 2:
        search_items(url, cat)
    elif mode == 3:
        if search and search is not None:
            pagination(url, page, cat, search)
        else:
            pagination(url, page, cat)
    elif mode == 4:
        play_video(name, url, thumb, play)
    elif mode in [5, 6]:
        if '\\ ' in name:
            name = name.split('\\ ')[1]
        if '  - ' in name:
            name = name.split('  - ')[0]
        if mode == 5:
            favorite_add(name, url, fav_mode, thumb, fanart, plot, cat, str(folder), str(play))
        else:
            favorite_remove(name)
    elif mode == 7:
        favorites_show()
    elif mode == 8:
        ADDON.openSettings()
    elif mode == 9:
        favorites_import()
    elif mode == 10:
        login_session_reset()
    elif mode == 11:
        subscribe(name, cat)
    elif mode == 12:
        playlist_manage(url, cat)
    elif mode == 13:
        comments_show(url)
    elif mode == 14:
        login_test()


if __name__ == "__main__":
    main()
