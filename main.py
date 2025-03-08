# Auto updated?
#   Yes
# Modified:
#   Friday, March 7, 2025 7:29:17 AM PST
#
"""
The snippet above is from an Ext from TheRepoClub called File Header Generator
==========================================================================================
Module: ............ main.py/main
Description: ....... Main entry point for the Rumble Video Kodi Plugin, handling parameter parsing and routing for video playback, search, favorites, user session management, and other plugin functionalities.
Version: ........... 1.0.0 - major.minor.patch
Created: ........... 2025-03-02
Updated: ........... 2025-03-02
Installs to: ....... plugin.video.rumbleinthejungle/
Compatibility: ..... XBMC, Kodi 16+, Kodi 21 Omega
Contact Author: .... lundeen-bryan
Copyright:  ........ company © 2025. All rights reserved.
Preconditions: ..... Requires Python 3.11+ and a Kodi environment with xbmc, xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs; depends on auxiliary modules (lib.general, lib.rumble_user, lib.comments).
Calls To: .......... Internal functions (home_menu, search_menu, play_video, etc.)
Called By: ......... Kodi Plugin System
Examples: .......... _
 (1) When Kodi launches the plugin, main() is executed to dispatch the appropriate functionality based on URL parameters.
Notes: ............. _
 (1) This module integrates routing and dispatching for plugin operations such as search, favorites, video playback, and session management.
 (2) Originally adapted from the Rumble project by Azzy9; updated for improved clarity, maintainability, and documentation.
==========================================================================================
"""

import sys
import re
import os


from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Optional, Union, List, Tuple

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs

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

def build_page_url(base_url: str, page: int) -> str:
    """
    Given a base URL, update its query parameters to include the page number.
    """
    parsed = urlparse(base_url)
    # parse_qs returns values as lists, so convert them into single values
    query_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    query_params['page'] = str(page)
    new_query = urlencode(query_params)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                       parsed.params, new_query, parsed.fragment))

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


def favorites_load(return_string: bool = False):
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
        with open(favorites, 'r', encoding='utf-8') as fav_file:
            fav_str = fav_file.read()
        if return_string:
            return fav_str
        if fav_str:
            return json.loads(fav_str)
    else:
        favorites_create()

    return '' if return_string else []


def prompt_user_for_search(heading: str = '', message: str = '') -> Optional[str]:
    """
    Prompt the user for a search string using a Kodi keyboard dialog.

    This function displays a keyboard input dialog to the user, allowing them
    to enter a search string. The dialog can be customized with a heading and
    a message.

    Args:
        heading (str): The heading text for the keyboard input dialog.
                       Defaults to an empty string.
        message (str): The message text for the keyboard input dialog.
                       Defaults to an empty string.

    Returns:
        Optional[str]: The search string entered by the user if confirmed,
                       or None if the user cancels the input.

    Example:
        search_query = prompt_user_for_search("Search", "Enter your search term:")
        if search_query:
            perform_search(search_query)
        else:
            print("Search was cancelled.")
    """
    user_input = None
    keyboard = xbmc.Keyboard(message, heading)
    keyboard.doModal()

    if keyboard.isConfirmed():
        user_input = keyboard.getText()

    return user_input


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

def pagination(url: str, page: int, category: str, search: Optional[str] = None) -> None:
    """
    List directory items and show pagination.

    If no results are loaded, this function prompts the user to either refresh
    the container or go back.

    Args:
        url (str): The base URL for the directory.
        page (int): The current page number.
        category (str): The category of the directory.
        search (Optional[str]): A search query string, if applicable.

    Returns:
        None
    """
    if url:
        # Combine search query if provided
        if search:
            combined_url = f"{url}{search}"
        else:
            combined_url = url

        # Update the query parameters to include the current page number
        page_url = build_page_url(combined_url, page)

        # For certain categories, we might not paginate.
        paginated = category not in {'following', 'top', 'cat_list'}

        # Retrieve results
        amount = list_rumble(page_url, category)

        # Handle empty results
        if amount == 0:
            dialog = xbmcgui.Dialog()
            if dialog.yesno("No results loaded", "Would you like to try again?"):
                xbmc.executebuiltin('Container.Refresh')
            else:
                xbmc.executebuiltin('Container.GoBack')
            return

        # If pagination is enabled and there are enough items, add a link for the next page.
        if paginated and amount > 15 and page < 10:
            next_page = page + 1
            name = f"{get_string(30150)} {next_page}"
            list_item = xbmcgui.ListItem(name)

            link_params = {
                'url': url,
                'mode': '3',
                'name': name,
                'page': str(next_page),
                'cat': category,
            }
            link = build_url(link_params)
            if search and category == 'video':
                link = f"{link}&search={urllib.parse.quote_plus(search)}"

            xbmcplugin.addDirectoryItem(PLUGIN_ID, link, list_item, True)
    xbmcplugin.endOfDirectory(PLUGIN_ID)


def extract_image_url(html_content: str, image_id: int) -> str:
    """
    Extract the URL of an image from a CSS background-image rule based on its image ID.

    This function searches the provided HTML content for a CSS rule corresponding to the
    given image ID and extracts the URL specified in the 'background-image' property.

    Args:
        html_content (str): The HTML content to search.
        image_id (int): The image identifier used in the CSS class (e.g., in 'user-image--img--id-{image_id}').

    Returns:
        str: The extracted image URL if found; otherwise, an empty string.
    """
    pattern = rf"i\.user-image--img--id-{image_id}.*?\{{\s*background-image:\s*url\((.*?)\);"
    matches = re.findall(pattern, html_content, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return matches[0] if matches else ""


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
            amount = create_directory_listing( data, cat, 'video', True, 1 )
        else:
            amount = create_directory_listing( data, cat, 'channel', True )
    elif cat in { 'subscriptions', 'cat_video', 'live_stream', 'playlist' }:
        amount = create_directory_listing( data, cat, cat, False, 2 )
    elif cat in { 'channel', 'top', 'other' }:
        amount = create_directory_listing( data, cat, 'video', False, 2 )
    elif cat in { 'channel_video', 'user' }:
        amount = create_directory_listing( data, cat, 'channel_video', False, 2 )
    elif cat == 'following':
        amount = create_directory_listing( data, cat, 'following', False, 2 )
    elif cat == 'cat_list':
        amount = create_directory_listing( data, cat, cat, False )

    return amount


def create_directory_listing(html_data: str, category: str, listing_type: str = 'video', is_search: bool = False, play_mode: int = 0) -> int:
    """
    Creates and displays a directory listing based on the provided HTML content and listing type.

    Parameters:
        html_data (str): The HTML content containing the directory listing items.
        category (str): The category for the directory listing items.
        listing_type (str, optional): The type of listing to create. Supported types include:
            'video', 'cat_video', 'subscriptions', 'live_stream', 'channel_video', 'playlist',
            'cat_list', 'following', etc. Defaults to 'video'.
        is_search (bool, optional): Indicates whether the listing is generated as a result of a search.
            Defaults to False.
        play_mode (int, optional): The play mode for the directory items. Defaults to 0.

    Returns:
        int: The number of directory listing items created.
    """
    item_count = 0
    one_line_titles = ADDON.getSetting('one_line_titles') == 'true'

    if listing_type == 'video':
        video_pattern = re.compile(
            r'href=\"([^\"]+)\"><div class=\"(?:[^\"]+)\"><img\s*class=\"video-item--img\"\s*src=\"([^\"]+)\"\s*alt=\"(?:[^\"]+)\"\s*>(?:<span class=\"video-item--watching\">[^\<]+</span>)?(?:<div class=video-item--overlay-rank>(?:[0-9]+)</div>)?</div><(?:[^\>]+)></span></a><div class=\"video-item--info\"><time class=\"video-item--meta video-item--time\" datetime=(.+?)-(.+?)-(.+?)T(?:.+?) title\=\"(?:[^\"]+)\">(?:[^\<]+)</time><h3 class=video-item--title>(.+?)</h3><address(?:[^\>]+)><a rel=author class=\"(?:[^\=]+)=(.+?)><div class=ellipsis-1>(.+?)</div>',
            re.MULTILINE | re.DOTALL | re.IGNORECASE
        )
        videos = video_pattern.findall(html_data)
        if videos:
            item_count = len(videos)
            for link, img, year, month, day, title, channel_link, channel_name in videos:
                info_labels = {}
                if '<svg' in channel_name:
                    channel_name = channel_name.split('<svg')[0] + " (Verified)"
                info_labels['year'] = year
                video_title = '[B]' + clean_text(title) + '[/B]'
                video_title += ' - ' if one_line_titles else '\n'
                video_title += '[COLOR gold]' + channel_name + '[/COLOR] - [COLOR lime]' + get_date_formatted(DATE_FORMAT, year, month, day) + '[/COLOR]'
                images = {'thumb': str(img), 'fanart': str(img)}
                add_dir(video_title, BASE_URL + link, 4, images, info_labels, category, False, True, play_mode, {'name': channel_link, 'subscribe': True})
    elif listing_type in {'cat_video', 'subscriptions', 'live_stream', 'channel_video', 'playlist'}:
        if listing_type == 'live_stream':
            videos_regex = r'<div class=\"thumbnail__grid\"\s*role=\"list\">(.*)<nav class=\"paginator\">'
        elif listing_type == 'playlist':
            videos_regex = r'<ol\s*class=\"videostream__list\"(?:[^>]+)>(.*)</ol>'
        else:
            videos_regex = r'<ol\s*class=\"thumbnail__grid\">(.*)</ol>'
        videos_section = re.compile(videos_regex, re.DOTALL | re.IGNORECASE).findall(html_data)
        if videos_section:
            if listing_type == 'playlist':
                video_items = videos_section[0].split('"videostream videostream__list-item')
            else:
                video_items = videos_section[0].split('"videostream thumbnail__grid-')
            video_items.pop(0)
            item_count = len(video_items)
            for video in video_items:
                video_title = ''
                images = {}
                info_labels = {}
                subscribe_context = {}

                title_match = re.compile(r'<h3(?:[^\>]+)?>(.*)</h3>', re.DOTALL | re.IGNORECASE).findall(video)
                link_match = re.compile(r'<a\sclass="videostream__link link"\sdraggable="false"\shref="([^\"]+)">', re.DOTALL | re.IGNORECASE).findall(video)
                img_match = re.compile(r'<img\s*class=\"thumbnail__image\"\s*draggable=\"false\"\s*src=\"([^\"]+)\"', re.DOTALL | re.IGNORECASE).findall(video)

                if title_match:
                    video_title = '[B]' + clean_text(title_match[0]) + '[/B]'
                if 'videostream__status--live' in video:
                    video_title += ' [COLOR red](Live)[/COLOR]'
                if 'videostream__status--upcoming' in video:
                    video_title += ' [COLOR yellow](Upcoming)[/COLOR]'

                channel_name_match = re.compile(
                    r'<span\sclass="channel__name(?:[^\"]+)" title="(?:[^\"]+)">([^\<]+)</span>(\s*<svg class=channel__verified)?',
                    re.DOTALL | re.IGNORECASE
                ).findall(video)
                channel_link_match = re.compile(
                    r'<a\s*rel=\"author\"\s*class=\"channel__link\slink\s(?:[^\"]+)\"\s*href=\"([^\"]+)\"\s*>',
                    re.DOTALL | re.IGNORECASE
                ).findall(video)
                if channel_name_match:
                    video_title += ' - ' if one_line_titles else '\n'
                    video_title += '[COLOR gold]' + clean_text(channel_name_match[0][0])
                    if channel_name_match[0][1]:
                        video_title += " (Verified)"
                    video_title += '[/COLOR]'
                    if channel_link_match:
                        subscribe_context = {'name': channel_link_match[0], 'subscribe': True}
                date_time_match = re.compile(
                    r'<time\s*class=\"(?:[^\"]+)\"\s*datetime=\"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})-(\d{2}):(\d{2})\"',
                    re.DOTALL | re.IGNORECASE
                ).findall(video)
                if date_time_match:
                    info_labels['year'] = date_time_match[0][0]
                    video_title += ' - [COLOR lime]' + get_date_formatted(DATE_FORMAT, date_time_match[0][0], date_time_match[0][1], date_time_match[0][2]) + '[/COLOR]'
                if img_match:
                    images = {'thumb': str(img_match[0]), 'fanart': str(img_match[0])}
                duration_match = re.compile(r'videostream__status--duration\"\s*>([^<]+)</div>', re.DOTALL | re.IGNORECASE).findall(video)
                if duration_match:
                    info_labels['duration'] = duration_to_secs(duration_match[0].strip())
                add_dir(video_title, BASE_URL + link_match[0], 4, images, info_labels, category, False, True, play_mode, subscribe_context)
    elif listing_type == 'cat_list':
        category_list = re.compile(
            r'<a\s*class=\"category__link link\"\s*href=\"([^\"]+)\"\s*>\s*<img\s*class=\"category__image\"\s*src=\"([^\"]+)\"\s*alt=(?:[^\>]+)>\s*<strong class=\"category__title\">([^\<]+)</strong>',
            re.DOTALL | re.IGNORECASE
        ).findall(html_data)
        if category_list:
            item_count = len(category_list)
            for link, img, title in category_list:
                new_category = 'channel_video'
                images = {'thumb': str(img), 'fanart': str(img)}
                add_dir(clean_text(title), BASE_URL + link.strip() + '/videos', 3, images, {}, new_category)
    elif listing_type == 'following':
        followed_regex = r'<ol\s*class=\"followed-channels__list\">(.*)</ol>'
        followed_section = re.compile(followed_regex, re.DOTALL | re.IGNORECASE).findall(html_data)
        if followed_section:
            video_items = followed_section[0].split('"followed-channel flex items-')
            video_items.pop(0)
            item_count = len(video_items)
            for video in video_items:
                video_title = ''
                images = {}
                title_match = re.compile(r'<span\s*class=\"line-clamp-2\">([^<]+)<\/span>', re.DOTALL | re.IGNORECASE).findall(video)
                followers_match = re.compile(r'<div\s*class=\"followed-channel__followers(?:[^\"]+)\">([^<]+)</div>', re.DOTALL | re.IGNORECASE).findall(video)
                link_match = re.compile(r'<a\s*class=\"(?:[^\"]+)\"\s*href=\"(\/(?:c|user)\/[^\"]+)\"\s*>', re.DOTALL | re.IGNORECASE).findall(video)
                img_match = re.compile(r'<(?:img|span)\s*class=\"channel__avatar([^\"]+)\"\s*(?:src=\"([^\"]+)\")?', re.DOTALL | re.IGNORECASE).findall(video)
                if title_match:
                    video_title = '[B]' + clean_text(title_match[0]) + '[/B]'
                if '<use href="#channel_verified" />' in video:
                    video_title += ' [COLOR gold](Verified)[/COLOR]'
                channel_link = link_match[0] if link_match else ""
                if img_match:
                    if 'channel__letter' in img_match[0][0]:
                        image_url = MEDIA_DIR + 'letters/' + title_match[0][0].lower() if title_match else ''
                    else:
                        image_url = img_match[0][1]
                    images = {'thumb': str(image_url), 'fanart': str(image_url)}
                    if 'channel__live' in img_match[0][0]:
                        video_title += ' [COLOR red](Live)[/COLOR]'
                if followers_match:
                    video_title += ' - ' if one_line_titles else '\n'
                    video_title += '[COLOR green]' + followers_match[0].strip() + '[/COLOR]'
                new_category = 'user' if '/user/' in channel_link else 'channel_video'
                add_dir(video_title, BASE_URL + channel_link, 3, images, {}, new_category, True, True, play_mode, {'name': channel_link, 'subscribe': False})
    else:
        channels_regex = r'<div class="main-and-sidebar">(.*)<nav class="paginator">'
        channels_section = re.compile(channels_regex, re.DOTALL | re.IGNORECASE).findall(html_data)
        if channels_section:
            channels = channels_section[0].split('<article')
            channels.pop(0)
            item_count = len(channels)
            for channel in channels:
                link_match = re.compile(r'<a\shref=([^\s]+)\sclass=\"(?:[^\"]+)\">', re.DOTALL | re.IGNORECASE).findall(channel)
                channel_link = link_match[0] if link_match else ""
                xbmc.log(json.dumps(channel_link), xbmc.LOGWARNING)
                # Filter based on search context and category type
                if is_search:
                    if category == 'channel' and '/c/' not in channel_link:
                        continue
                    elif category != 'channel' and '/user/' not in channel_link:
                        continue
                images = {}
                channel_name_match = re.compile(r'<span\sclass=\"block\struncate\">([^<]+)<\/span>', re.DOTALL | re.IGNORECASE).findall(channel)
                channel_name = channel_name_match[0] if channel_name_match else ""
                verified = bool(re.compile(r'<title>Verified</title>', re.DOTALL | re.IGNORECASE).findall(channel))
                followers_match = re.compile(r'<span\sclass=\"(?:[^\"]+)\">\s+([^&]+)&nbsp;Follower(?:s)?\s+</span>', re.DOTALL | re.IGNORECASE).findall(channel)
                followers = followers_match[0] if followers_match else "0"
                img_id_match = re.compile(r'user-image--img--id-([^\s]+)\s', re.DOTALL | re.IGNORECASE).findall(channel)
                img_id_str = img_id_match[0] if img_id_match else ""
                if img_id_str:
                    try:
                        img_id = int(img_id_str)
                        img_url = str(extract_image_url(html_data, img_id))
                    except ValueError:
                        img_url = MEDIA_DIR + 'letters/' + channel_name[0] + '.png'
                else:
                    img_url = MEDIA_DIR + 'letters/' + channel_name[0] + '.png'
                images = {'thumb': str(img_url), 'fanart': str(img_url)}
                video_title = '[B]' + channel_name + '[/B]'
                if verified:
                    video_title += ' [COLOR gold](Verified)[/COLOR]'
                video_title += ' - ' if one_line_titles else '\n'
                video_title += '[COLOR palegreen]' + followers + '[/COLOR] [COLOR yellow]' + get_string(30156) + '[/COLOR]'
                add_dir(video_title, BASE_URL + channel_link, 3, images, {}, category, True, True, play_mode, {'name': channel_link, 'subscribe': True})
    return item_count


def extract_playlist_video_id(url: str) -> Optional[str]:
    """
    Retrieve and extract the playlist video ID from a given URL.

    This function fetches the HTML content from the specified URL using `request_get`,
    then uses a regular expression to locate the 'data-id' attribute. This ID is essential
    for operations like adding videos to playlists.

    Args:
        url (str): The URL of the playlist video page.

    Returns:
        Optional[str]: The extracted playlist video ID if found; otherwise, None.
    """
    html_content = request_get(url)
    match = re.search(r'data-id="([0-9]+)"', html_content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return match.group(1) if match else None

def resolve_video_url(video_url: str) -> Optional[str]:
    """
    Resolves a Rumble video URL to a direct media link based on the user's playback settings.

    This function extracts the video ID from the provided Rumble URL, retrieves available quality
    options via the Rumble API, and selects the appropriate media URL according to the user's
    playback method preference:
      - Playback method 0 (high auto): Automatically selects the highest quality.
      - Playback method 1 (low auto): Automatically selects the lowest quality.
      - Playback method 2 (quality select): Prompts the user to choose the desired quality.

    Args:
        video_url (str): The Rumble video URL to resolve.

    Returns:
        Optional[str]: The resolved direct media URL if successful; otherwise, None.
    """
    playback_method: int = int(ADDON.getSetting('playbackMethod'))  # 0, 1, or 2
    resolved_url: Optional[str] = None
    quality_urls: List[Tuple[str, str]] = []  # List of tuples (quality, url)

    video_id = get_video_id(video_url)
    if not video_id:
        return None

    api_url = f"{BASE_URL}/embedJS/u3/?request=video&ver=2&v={video_id}"
    api_response = request_get(api_url)
    qualities = ['1080', '720', '480', '360', 'hls']

    for quality in qualities:
        pattern = rf'"{quality}".+?url.+?:"(.*?)"'
        matches = re.findall(pattern, api_response, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if matches:
            if playback_method == 0:
                resolved_url = matches[0]
                break
            else:
                quality_urls.append((quality, matches[0]))

    if playback_method > 0 and quality_urls:
        # If only one URL is available and it's an HLS stream, process it using M3U8Processor.
        if len(quality_urls) == 1 and '.m3u8' in quality_urls[0][1]:
            from lib.m3u8 import M3U8Processor  # Updated import based on available attribute
            m3u8_handler = M3U8Processor()
            # Assuming m3u8_handler.process returns a list of (quality, url) tuples.
            quality_urls = m3u8_handler.process(request_get(quality_urls[0][1]))
        if playback_method == 1:
            # For low auto, reverse the list to select the lowest quality.
            quality_urls.reverse()
            resolved_url = quality_urls[0][1]
        elif playback_method == 2:
            # For quality select, prompt the user.
            selected_index: int
            if len(quality_urls) == 1:
                selected_index = 0
            else:
                quality_labels = [quality for quality, _ in quality_urls]
                selected_index = xbmcgui.Dialog().select('Select Quality', quality_labels)
            if selected_index != -1:
                resolved_url = quality_urls[selected_index][1]

    if resolved_url:
        resolved_url = resolved_url.replace(r'\/', '/')
    return resolved_url

def play_kodi_video(video_title: str, video_url: str, thumbnail_url: str, play_method: int = 2) -> None:
    """
    Resolves and plays a video in Kodi.

    This function takes an original video URL, resolves it to a playable stream, and initiates
    playback in Kodi. It checks the add-on settings to determine whether to switch from HTTPS to HTTP,
    creates a Kodi ListItem with the video metadata and thumbnail, and then starts playback based on
    the specified playback method.

    Args:
        video_title (str): The title of the video.
        video_url (str): The original URL of the video to resolve.
        thumbnail_url (str): The URL or local path to the video's thumbnail image.
        play_method (int, optional): Playback method indicator. Defaults to 2.
            - 1: Immediate playback using xbmc.Player().
            - 2: Deferred playback using xbmcplugin.setResolvedUrl().

    Returns:
        None
    """
    resolved_url = resolve_video_url(video_url)

    if resolved_url:
        # Apply HTTP if the user set HTTP as the default protocol.
        if ADDON.getSetting('useHTTP') == 'true':
            resolved_url = resolved_url.replace('https://', 'http://', 1)

        video_list_item = xbmcgui.ListItem(video_title, path=resolved_url)
        video_list_item.setArt({'icon': thumbnail_url, 'thumb': thumbnail_url})

        info_labels = {'Title': video_title, 'plot': ''}
        item_set_info(video_list_item, info_labels)

        if play_method == 1:
            xbmc.Player().play(item=resolved_url, listitem=video_list_item)
        elif play_method == 2:
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, video_list_item)
    else:
        xbmcgui.Dialog().ok('Error', 'Video not found')

def perform_search_and_display_results(rumble_base_url: str, search_category: str) -> None:
    """
    Execute a Rumble search based on user input and display the paginated results.

    This function:
    1. Prompts the user for a search query.
    2. Encodes the query for URL usage.
    3. Calls the pagination function to display the resulting pages.

    Args:
        rumble_base_url (str): The base URL for performing the Rumble search.
        search_category (str): The category of the search (e.g., 'video', 'channel').

    Returns:
        None: The function does not explicitly return a value. It initiates
        the display of search results through the pagination function.

    Note:
        If the user cancels the search input (i.e., provides no query),
        the function returns without performing the search.
    """
    user_search_input = prompt_user_for_search(heading="Search")

    if not user_search_input:
        return

    encoded_search_query: str = urllib.parse.quote_plus(user_search_input)
    pagination(rumble_base_url, 1, search_category, encoded_search_query)

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
        if data:  # Check if the list is non-empty
            for (name, url, mode, thumb, fanart, plot, cat, folder_str, play_str) in data:
                images = {
                    'thumb': str(thumb),
                    'fanart': str(fanart)
                }
                info_labels = {'plot': str(plot)}
                folder = (folder_str == 'True')
                add_dir(name, url, mode, images, info_labels, cat, folder, True, int(play_str))

            xbmcplugin.endOfDirectory(PLUGIN_ID)
        else:
            xbmcgui.Dialog().ok(get_string(14117), get_string(30155))

    except Exception as e:
        # Log the error for debugging
        xbmc.log(f"[Favorites Error] {e}", level=xbmc.LOGERROR)
        xbmcplugin.endOfDirectory(PLUGIN_ID)

def add_favorite_video(video_title: str, video_url: str, favorite_mode: int,
                       thumbnail: str, fanart_image: str, plot_summary: str,
                       category: str, is_folder: bool, playback_mode: int) -> None:
    """
    Add a video to the favorites list.

    This function appends a new favorite video entry—containing metadata such as
    title, URL, mode, thumbnail, fanart, plot summary, category, folder flag, and playback mode—
    to the favorites file. After updating the file, it displays a notification to inform the user
    that the video has been added.

    Args:
        video_title (str): The title of the video.
        video_url (str): The URL of the video.
        favorite_mode (int): The mode number associated with this favorite.
        thumbnail (str): The URL or path to the video's thumbnail image.
        fanart_image (str): The URL or path to the video's fanart image.
        plot_summary (str): A brief description or summary of the video.
        category (str): The category to which the video belongs.
        is_folder (bool): Whether the item should be treated as a folder.
        playback_mode (int): The playback mode for the video (e.g., 0 for non-playable, 2 for playable).

    Returns:
        None
    """
    favorites_data = favorites_load()
    favorites_data.append((video_title, video_url, favorite_mode, thumbnail,
                           fanart_image, plot_summary, category, is_folder, playback_mode))
    with open(favorites, 'w', encoding='utf-8') as fav_file:
        fav_file.write(json.dumps(favorites_data))
    notify(get_string(30152), video_title, thumbnail)

def remove_favorite_video(video_title: str) -> None:
    """
    Remove a favorite video from the favorites list by title.

    This function searches for a favorite video matching the provided title,
    removes it from the favorites data, updates the favorites file, and notifies
    the user of the removal.

    Args:
        video_title (str): The title of the video to remove from favorites.

    Returns:
        None
    """
    favorites_data = favorites_load()
    for index, favorite in enumerate(favorites_data):
        if favorite[0] == video_title:
            del favorites_data[index]
            with open(favorites, 'w', encoding='utf-8') as fav_file:
                fav_file.write(json.dumps(favorites_data))
            break

    notify(get_string(30154), video_title)
    xbmc.executebuiltin('Container.Refresh')

# 📌  import_favs_from_matrix_version.md 📝 🗑️

def login_session_reset():
    """
    Reset the current Rumble user session when the "Reset Session" button is pressed
    in the add-on settings (found under "Login").

    This function performs the following actions:
    1. Resets the session details for the current Rumble user.
    2. Displays a notification to the user indicating that the session has been reset.

    The function does not take any parameters and does not return any values.

    Notes:
    - Assumes the existence of a global RUMBLE_USER object with a reset_session_details() method.
    - Relies on notify() and get_string() for user notifications.

    Usage:
    Called automatically when the user clicks the "Reset Session" button in
    the add-on settings (Login category). It can also be invoked manually as needed
    to forcibly clear the user's session, for instance to handle logout or resolve
    authentication issues.
    """

    RUMBLE_USER.reset_session_details()
    notify(get_string(30200))

def manage_rumble_subscription(
    target_identifier: str,
    subscription_action: str
) -> bool:
    """
    Manage subscribing or unsubscribing to a Rumble channel or user.

    This function checks for an active session, determines whether the target
    is a channel or user based on the format of `target_identifier`, and then
    attempts the specified subscription action through the RUMBLE_USER object.

    Parameters:
        target_identifier (str): The channel/user identifier in the format
            '/user/username' or '/c/channelname'.
        subscription_action (str): Either 'subscribe' or 'unsubscribe'.

    Returns:
        bool: True if the subscription action succeeded, False otherwise.

    Side Effects:
        - Modifies the user's subscription status on Rumble.
        - Displays a notification about the action's result.

    Dependencies:
        - RUMBLE_USER: An object that manages Rumble user sessions and API requests.
        - notify: A function to display notifications to the user.
        - json: Used to parse the API response.

    Usage:
        success = manage_rumble_subscription('/c/example_channel', 'subscribe')
        if success:
            print("Subscription action completed successfully.")
        else:
            print("Failed to complete the subscription action.")
    """
    # Exit early if there is no active session
    if not RUMBLE_USER.has_session():
        notify("Unable to perform action: No active session.")
        return False

    # Determine the target type based on the identifier
    subscription_target = None
    if "/user/" in target_identifier:
        target_identifier = target_identifier.replace("/user/", "")
        subscription_target = "user"
    elif "/c/" in target_identifier:
        target_identifier = target_identifier.replace("/c/", "")
        subscription_target = "channel"

    # Proceed only if a valid target type was identified
    if subscription_target:
        response = RUMBLE_USER.subscribe(subscription_action, subscription_target, target_identifier)
        if response:
            data = json.loads(response)
            user_data = data.get("user", {})
            extra_data = data.get("data", {})

            # Check if the user is logged in and the response contains a thumbnail
            if user_data.get("logged_in") and extra_data.get("thumb"):
                if subscription_action == "subscribe":
                    notify(f"Subscribed to {target_identifier}", None, extra_data["thumb"])
                else:
                    notify(f"Unsubscribed to {target_identifier}", None, extra_data["thumb"])
                return True

    # Fallback notification if no successful action took place
    notify("Unable to perform the requested action.")
    return False

def test_rumble_login() -> None:
    """
    Reset the current session and test the Rumble user login.

    This function:
        1. Resets the current session details.
        2. Checks if login details are available.
        3. Attempts to log in if details are present.
        4. Notifies the user of the login result.

    Side Effects:
        - Resets the current user session.
        - Displays a notification about the login status.

    Notifications:
        - 30201 ("Login Success"): Displayed when the login is successful.
        - 30202 ("Login Failed"): Displayed when the login fails.
        - 30203 ("No details detected"): Displayed when no login details are provided.

    Dependencies:
        - RUMBLE_USER: Manages user sessions and login.
        - notify: Displays notifications to the user.
        - get_string: Retrieves localized string resources.

    Usage:
        Typically called to verify user authentication or troubleshoot login issues.
    """
    RUMBLE_USER.reset_session_details()

    if RUMBLE_USER.has_login_details():
        if RUMBLE_USER.login():
            notify(get_string(30201))  # Login Success
        else:
            notify(get_string(30202))  # Login Failed
    else:
        notify(get_string(30203))      # No details detected

'''
 *
 * Stop Here
 *
'''



def add_dir(name, url, mode, images={}, info_labels={}, cat='', folder=True, fav_context=False, play=0, subscribe_context=False):
    """
    Adds a directory item to the Kodi interface for the Rumble video addon.

    This function creates and configures a ListItem object with the provided information,
    sets up context menus, and adds the item to the Kodi interface.

    Parameters:
    name (str): The display name of the item.
    url (str): The URL associated with the item.
    mode (int): The mode number for the item's action.
    images (dict): A dictionary containing 'thumb' and 'fanart' image URLs.
    info_labels (dict): A dictionary of metadata labels for the item.
    cat (str): The category of the item.
    folder (bool): If True, the item is treated as a folder; otherwise, as a playable item.
    fav_context (bool): If True, adds favorite-related context menu items.
    play (int): Playback mode (0: not playable, 1: unknown, 2: playable).
    subscribe_context (dict or bool): If dict, adds subscribe/unsubscribe context menu items.

    The function performs the following main tasks:
    1. Sets up artwork (thumbnail and fanart) for the item.
    2. Builds a URL with the item's parameters.
    3. Creates and configures a ListItem object.
    4. Adds various context menu items based on the item type and user login status.
    5. Handles favorites-related functionality.
    6. Adds the configured item to the Kodi interface.

    Note:
    - This function relies on several global variables and functions (e.g., HOME_DIR, MEDIA_DIR, RUMBLE_USER).
    - It uses Kodi-specific modules like xbmcgui and xbmcplugin.

    Returns:
    None
    """

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

def playlist_manage(url, action="add"):
    """
    Manages a video in Rumble's playlist by adding or deleting it.

    This function extracts the video ID from the given URL and performs
    the specified action (add or delete) on Rumble's playlist. It then
    notifies the user about the result of the operation.

    Parameters:
    url (str): The URL of the video to be managed in the playlist.
    action (str, optional): The action to perform on the playlist.
                            Can be either "add" or "delete". Defaults to "add".

    Returns:
    None

    Side Effects:
    - Modifies the user's Rumble playlist.
    - Displays a notification to the user about the result of the operation.
    """

    video_id = get_playlist_video_id(url)
    if video_id:
        if action == "add":
            RUMBLE_USER.playlist_add_video(video_id)
            message = "Added to playlist"
        else:
            RUMBLE_USER.playlist_delete_video(video_id)
            message = "Deleted from playlist"
    else:
        if action == "add":
            message = "Cannot add to playlist"
        else:
            message = "Cannot delete from playlist"

    notify(message, "Playlist")

def comments_show(url):
    """
    Retrieve and display comments for a Rumble video in a modal window.

    This function extracts the video ID from the provided URL, creates a modal
    window to display the comments, and shows it to the user. If the video ID
    cannot be extracted, it notifies the user that comments are unavailable.

    Parameters:
    url (str): The URL of the Rumble video for which to show comments.

    Returns:
    None

    Side Effects:
    - Opens a modal window displaying comments if the video ID is successfully extracted.
    - Displays a notification if comments cannot be retrieved.

    Raises:
    No exceptions are explicitly raised, but underlying functions may raise exceptions.

    Dependencies:
    - get_video_id(): Function to extract the video ID from a URL.
    - CommentWindow: Custom class for creating a comment display window.
    - ADDON: Kodi Addon object for retrieving addon information.
    - notify(): Function to display notifications to the user.

    Usage:
    comments_show('https://rumble.com/v1234-example-video')
    """

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

# 📌  main_notes.md 📝 🗑️
def main():
    """
    Main entry point for the Rumble video Kodi plugin.

    This function serves as the central dispatcher for the plugin, handling various
    operations based on the parameters passed to it. It processes user interactions
    within the Kodi interface and routes them to the appropriate functionality.

    The function performs the following main tasks:
    1. Retrieves and processes plugin parameters.
    2. Decodes URL-encoded parameter values.
    3. Executes different actions based on the 'mode' parameter.

    Parameters:
    None explicitly, but it uses the following global or imported functions/variables:
    - get_params(): Function to retrieve plugin parameters.
    - urllib.parse.unquote_plus(): Function to decode URL-encoded strings.
    - Various mode-specific functions (e.g., home_menu, search_menu, play_video, etc.)

    Returns:
    None

    Mode Operations:
    0: Display home menu
    1: Display search menu
    2: Perform search
    3: Handle pagination
    4: Play video
    5-6: Manage favorites (add/remove)
    7: Show favorites
    8: Open addon settings
    9: Import favorites
    10: Reset login session
    11: Subscribe to channel
    12: Manage playlist
    13: Show video comments
    14: Test login

    Note:
    This function assumes the existence of various other functions and global variables
    that are part of the larger plugin structure.
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
        perform_search_and_display_results(url, cat)
    elif mode == 3:
        if search and search is not None:
            pagination(url, page, cat, search)
        else:
            pagination(url, page, cat)
    elif mode == 4:
        play_kodi_video(name, url, thumb, play)
    elif mode in [5, 6]:
        if '\\ ' in name:
            name = name.split('\\ ')[1]
        if '  - ' in name:
            name = name.split('  - ')[0]
        if mode == 5:
            add_favorite_video(name, url, fav_mode, thumb, fanart, plot, cat, str(folder), str(play))
        else:
            remove_favorite_video(name)
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
