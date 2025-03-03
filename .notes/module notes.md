# Module Overview

1. Provides utility functions for Kodi add-ons to handle HTTP requests, URL building, notifications, localization, and video metadata management.
2. Manages HTTP requests with cookie support, custom headers, and both GET and POST methods.
3. Offers URL encoding utilities that construct Kodi-compatible navigation URLs.
4. Displays notifications to users via Kodi's built-in notification system.
5. Retrieves localized strings for both addon-specific messages and Kodi's built-in language strings.
6. Includes functions for date formatting and converting duration strings into seconds.
7. Parses URL parameters from Kodi's add-on invocation.
8. Cleans and sanitizes text by stripping whitespace and unescaping HTML entities.
9. Sets video metadata on Kodi ListItem objects based on the Kodi version.
10. Disables urllib3's InsecureRequestWarning for unverified HTTPS requests.

Preconditions: Must be running within a Kodi add-on environment (Kodi 21 Omega or compatible) on Python 3.11+ with Kodi modules (xbmc, xbmcgui, xbmcplugin, xbmcaddon), as well as requests and six installed, with proper add-on settings configured.
