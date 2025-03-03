# Auto updated?
#   Yes
# Modified:
#   Sunday, March 2, 2025 8:08:51 PM PST
#
"""
The snippet above is from an Ext from TheRepoClub called File Header Generator
==========================================================================================
Procedure: ......... m3u8.py
Description: ....... Provides functionality to process M3U8 file content specifically for streaming live videos on Kodi. It has been refactored to work with PY3+ and utilizes Kodi's xbmc logging system.
Version: ........... 1.0.0 - major.minor.patch
Created: ........... 2025-03-02
Updated: ........... 2025-03-02
Module URL: ........ weburl
Installs to: ....... plugin.video.rumbleinthejungle/lib
Compatibility: ..... XBMC, Kodi 16+
Contact Author: .... lundeen-bryan
Copyright:  ........ n/a © 2025. All rights reserved.
Parameters: ........ name(type): param_description
Returns: ........... type param_description
Preconditions: ..... precondition
Calls To: .......... procedure
Called By: ......... procedure
Examples: .......... _
 (1) examples_here
Notes: ............. _
 (1) Changes to previous versions:
     - Added type hints for improved clarity and maintainability.
     - Replaced multiple pop() calls with slicing to skip the first two lines of the file.
     - Utilized splitlines for robust and consisten line splitting.
     - Procesed the M3U8 content lines in pairs to extract resolution and URL
     - Integrated Kodi's xbmc.log for error logging during processing
     - Reveresed the list of URLs to maintain the original behavior
===========================================================================================
"""
import xbmc
from typing import List, Tuple

class M3U8Processor:
    def process(self, m3u8_data: str) -> List[Tuple[str, str]]:
        """
        Process the M3U8 file content and return a list of tuples (resolution, URL).
        """
        urls: List[Tuple[str, str]] = []
        # Use strip() and splitlines() for robust line splitting
        lines = m3u8_data.strip().splitlines()
        # Skip the first two lines (if present)
        content_lines = lines[2:] if len(lines) > 2 else []

        # Process lines in pairs (first line: resolution, second line: URL)
        for i in range(0, len(content_lines) - 1, 2):
            try:
                resolution_line = content_lines[i]
                url_line = content_lines[i + 1]
                # Extract resolution from the resolution line (e.g., "1920x1080" -> "1080")
                resolution_parts = resolution_line.split('x')
                resolution = resolution_parts[-1].strip() if resolution_parts else ''
                urls.append((resolution, url_line.strip()))
            except Exception as e:
                xbmc.log(f"Error processing pair starting at line {i}: {e}", level=xbmc.LOGERROR)

        # Reverse the list to maintain the original behavior (if required)
        urls.reverse()
        return urls
