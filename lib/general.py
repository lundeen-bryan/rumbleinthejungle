# -*- coding: utf-8 -*-
import sys
import requests
from datetime import datetime, timedelta

import html

import xbmcgui
import xbmc
import xbmcplugin
import xbmcaddon

import six
from six.moves import urllib

try:
    import json
except ImportError:
    import simplejson as json

PLUGIN_URL = sys.argv[0]

ADDON = xbmcaddon.Addon()
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')

KODI_VERSION = float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4])

#language
__language__ = ADDON.getLocalizedString

# Disable urllib3's "InsecureRequestWarning: Unverified HTTPS request is being made" warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

reqs = requests.session()

def request_get(url, data=None, extra_headers=None):
    """
    Makes an HTTP GET or POST request to the specified URL.

    This function handles setting up headers, managing cookies, and making the actual HTTP request.
    It supports both GET and POST methods, and can handle additional custom headers.

    Args:
        url (str): The URL to make the request to.
        data (dict, optional): Data to send in a POST request. If provided, a POST request is made;
                               otherwise, a GET request is made. Defaults to None.
        extra_headers (dict, optional): Additional headers to include in the request. Defaults to None.

    Returns:
        str: The text content of the response. Returns an empty string if an exception occurs.

    Note:
        - This function uses a predefined set of headers, including a specific User-Agent.
        - It manages cookies across requests, storing them in the Kodi addon settings.
        - The function has a timeout of 10 seconds for the request.
    """

    try:

        # headers
        my_headers = {
            'Accept-Language': 'en-gb,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': url,
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1'
        }

        # add extra headers
        if extra_headers:
            my_headers.update(extra_headers)

        # get stored cookie string
        cookies = ADDON.getSetting('cookies')

        # split cookies into dictionary
        if cookies:
            cookie_dict = json.loads( cookies )
        else:
            cookie_dict = None

        # make request
        if data:
            response = reqs.post(url, data=data, headers=my_headers, cookies=cookie_dict, timeout=10)
        else:
            response = reqs.get(url, headers=my_headers, cookies=cookie_dict, timeout=10)

        if response.cookies.get_dict():
            if cookie_dict:
                cookie_dict.update( response.cookies.get_dict() )
            else:
                cookie_dict = response.cookies.get_dict()

            # store cookies
            ADDON.setSetting('cookies', json.dumps(cookie_dict))

        return response.text

    except Exception:
        return ''

def build_url(query):
    """
    Constructs a URL for Kodi xbmcgui.ListItem with encoded parameters.

    This function takes a dictionary of URL parameters and builds a properly
    formatted and URL-encoded string for use in Kodi. It handles encoding of
    both string and non-string values, ensuring compatibility with Kodi's
    expectations.

    Args:
        query (dict): A dictionary containing key-value pairs to be included
                      as URL parameters.

    Returns:
        str: A formatted URL string with encoded parameters, ready for use
             in Kodi xbmcgui.ListItem.

    Example:
        params = {'action': 'play', 'video_id': '12345'}
        url = build_url(params)
        # Result: 'plugin://your.addon.id/?action=play&video_id=12345'
    """

    return (PLUGIN_URL + '?' + urllib.parse.urlencode({
        k: v.encode('utf-8') if isinstance(v, six.text_type)
        else unicode(v, errors='ignore').encode('utf-8')
        for k, v in query.items()
    }))


def notify(message, name=False, iconimage=False, time_shown=5000):
    """
    Display a notification to the user in the Kodi interface.

    This function shows a notification with customizable title, message, icon, and duration.
    If the title or icon is not provided, it uses default values from the addon settings.

    Args:
        message (str): The main content of the notification.
        name (str, optional): The title of the notification.
            Defaults to the addon name if not provided.
        iconimage (str, optional): The path to the icon image for the notification.
            Defaults to the addon icon if not provided.
        time_shown (int, optional): The duration to display the notification, in milliseconds.
            Defaults to 5000 (5 seconds).

    Returns:
        None

    Example:
        notify("Video started playing", "Now Playing", time_shown=3000)
    """

    if not name:
        name = ADDON_NAME

    if not iconimage:
        iconimage = ADDON_ICON

    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (name, message, time_shown, iconimage))

def get_string(string_id):
    """
    Retrieves a localized language string based on the provided string ID.

    This function handles both addon-specific strings and Kodi's built-in strings.
    For addon-specific strings (IDs >= 30000), it uses the addon's localization system.
    For Kodi's built-in strings (IDs < 30000), it uses Kodi's global localization system.

    Args:
        string_id (int): The ID of the desired language string.

    Returns:
        str: The localized string corresponding to the given string_id.

    Note:
        - Addon-specific strings typically use IDs starting from 30000 to avoid
          conflicts with Kodi's built-in string IDs.
        - The addon's localization strings should be defined in the addon's
          language files (e.g., resources/language/resource.language.en_gb/strings.po).

    Example:
        localized_string = get_string(30001)  # Retrieves addon-specific string
        kodi_string = get_string(13)  # Retrieves a Kodi built-in string
    """
    if string_id >= 30000:
        return __language__(string_id)
    return xbmc.getLocalizedString(string_id)


def get_date_formatted(format_id, year, month, day):
    """
    Format a date string based on the specified format ID.

    This function takes individual components of a date (year, month, day) and
    formats them into a string according to the specified format_id.

    Args:
        format_id (str): A string indicating the desired date format.
            '1' for MM/DD/YYYY
            '2' for DD/MM/YYYY
            Any other value for YYYY/MM/DD
        year (str): The year component of the date.
        month (str): The month component of the date.
        day (str): The day component of the date.

    Returns:
        str: A formatted date string according to the specified format_id.

    Examples:
        >>> get_date_formatted('1', '2023', '12', '31')
        '12/31/2023'
        >>> get_date_formatted('2', '2023', '12', '31')
        '31/12/2023'
        >>> get_date_formatted('3', '2023', '12', '31')
        '2023/12/31'
    """

    date = datetime(
        int(year),
        int(month),
        int(day)
    )
    if format_id == '1':
        return date.strftime('%m/%d/%Y')
    if format_id == '2':
        return date.strftime('%d/%m/%Y')
    return date.strftime('%Y/%m/%d')


def duration_to_secs(duration, fail_return=''):
    """
    Convert a duration string to seconds.

    This function takes a duration string in various formats and converts it to seconds.
    It supports formats like "HH:MM:SS", "MM:SS", or just seconds as a string.

    Args:
        duration (str): A string representing the duration. Can be in the format
                        "HH:MM:SS", "MM:SS", or just seconds.
        fail_return (str, optional): The value to return if conversion fails.
                                     Defaults to an empty string.

    Returns:
        str: The duration converted to seconds as a string. If conversion fails
             or the input is invalid, returns the value of `fail_return`.

    Examples:
        >>> duration_to_secs("01:30:45")
        '5445'
        >>> duration_to_secs("45:30")
        '2730'
        >>> duration_to_secs("3600")
        '3600'
        >>> duration_to_secs("invalid", "0")
        '0'

    Note:
        - For "HH:MM:SS" or "MM:SS" formats, it uses timedelta to calculate total seconds.
        - For input that's already in seconds, it simply returns that value as a string.
        - If the input is empty or conversion fails, it returns the `fail_return` value.
    """

    if not duration:
        return fail_return

    try:
        if ':' in duration:
            parts = duration.split(':')
            if len(parts) == 2:
                parts.insert(0, '0')  # Add 0 hours if only minutes and seconds
            h, m, s = map(int, parts)
            return str(int(timedelta(hours=h, minutes=m, seconds=s).total_seconds()))
        else:
            # should only be seconds
            return str(int(duration))
    except ValueError:
        return fail_return

def get_params():
    """
    Extract and parse URL parameters from the Kodi addon request.

    This function retrieves the URL query string from sys.argv[2], which is
    typically where Kodi passes the addon's URL parameters. It then parses
    this string into a dictionary of key-value pairs.

    Returns:
        dict: A dictionary containing the parsed URL parameters.
              Keys are parameter names, and values are parameter values.
              Empty values are retained in the dictionary.

    Example:
        If the addon is called with a URL like:
        'plugin://your.addon.id/?action=play&video_id=12345&quality='

        The function will return:
        {
            'action': 'play',
            'video_id': '12345',
            'quality': ''
        }

    Note:
        - The function assumes that sys.argv[2] contains the URL query string.
        - The leading '?' character of the query string is stripped before parsing.
        - This function is specifically designed for use in Kodi addons and may not
          work as expected in other contexts.
    """
    return dict(urllib.parse.parse_qsl(sys.argv[2][1:], keep_blank_values=True))

def clean_text(text):
    """
    Clean and sanitize the input text by removing problematic characters and converting HTML entities.

    This function performs the following operations:
    1. Strips leading and trailing whitespace.
    2. Unescapes HTML entities using html.unescape().

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned and sanitized text.

    Note:
        - This function is designed for Python 3.11+ and Kodi 21 Omega.
        - It uses html.unescape() to handle all HTML entities, not just a limited set.

    Examples:
        >>> clean_text("  Hello &amp; World!  ")
        'Hello & World!'
        >>> clean_text("Quote: &#34;Hello&#39;&amp;&#39;World&#34;")
        'Quote: "Hello\'&\'World"'
    """
    # Strip whitespace
    text = text.strip()

    # Unescape HTML entities
    text = html.unescape(text)

    return text

def item_set_info(line_item: xbmcgui.ListItem, properties: dict) -> None:
    """Set video information properties on a Kodi ListItem object.

    Args:
        line_item (xbmcgui.ListItem): The Kodi ListItem object to update.
        properties (dict): A dictionary containing video information properties.
    """
    if KODI_VERSION > 19.8:
        vidtag = line_item.getVideoInfoTag()

        # Use a mapping of property names to setter methods
        setters = {
            'year': lambda x: vidtag.setYear(int(x)),
            'episode': vidtag.setEpisode,
            'season': vidtag.setSeason,
            'plot': vidtag.setPlot,
            'title': vidtag.setTitle,
            'studio': lambda x: vidtag.setStudios([x]),
            'writer': lambda x: vidtag.setWriters([x]),
            'duration': lambda x: vidtag.setDuration(int(x)),
            'tvshowtitle': vidtag.setTvShowTitle,
            'mediatype': vidtag.setMediaType,
            'premiered': vidtag.setPremiered,
        }

        # Use dictionary comprehension with generator expression
        {setter(value) for key, (setter, value)
         in ((k, (setters[k], v)) for k, v in properties.items() if k in setters)}
    else:
        line_item.setInfo('video', properties)