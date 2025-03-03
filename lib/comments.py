# Auto updated?
#   Yes
# Modified:
#   Sunday, March 2, 2025 5:01:08 PM PST
#
"""
The snippet above is from an Ext from TheRepoClub called File Header Generator
==========================================================================================
Procedure: ......... comments.py
Description: ....... manage and document comments for the plugin.video.rumbleinthejungle library.
Version: ........... 1.0.0 - major.minor.patch
Created: ........... 2025-03-02
Updated: ........... 2025-03-02
Module URL: ........ weburl
Installs to: ....... plugin.video.rumbleinthejungle/lib
Compatibility: ..... XBMC, Kodi 16+, Kodi 21 Omega
Contact Author: .... lundeen-bryan
Copyright:  ........ n/a © 2025. All rights reserved.
Preconditions: ..... xbmc, xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs; depends on auxiliary modules (lib.general, lib.rumble_user).
Examples: .......... _
 (1)
Notes: ............. _
 (1)
===========================================================================================
"""
# 📌  comments_todo 📝 🗑️

import xbmc
import xbmcgui
import requests

from lib.general import *
from lib.rumble_user import RumbleUser
from dataclasses import dataclass

RUMBLE_USER = RumbleUser()

@dataclass
class Comment:
    author_url: str
    author_name: str
    comment_id: str
    post_day: str
    post_month: str
    post_date: str
    post_year: str
    post_hour: str
    post_minute: str
    post_meridiem: str
    post_time_ago: str
    comment_text: str


class CommentWindow(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        self.video_id = kwargs['video_id']
        xbmcgui.WindowXML.__init__(self, args, kwargs)

    def onInit(self):
        self.refresh()

    def fetch_comment_list(self):
        """
        Fetches the list of comments for the current video from Rumble.

        This method uses the RumbleUser instance to retrieve comments
        associated with the video_id of the current CommentWindow instance.

        Returns:
            list: A list of comment data. Each item in the list is expected
                  to be a tuple containing various details about a comment,
                  such as author name, comment text, post date, etc.

        Note:
            The actual structure of the returned data depends on the
            implementation of the RUMBLE_USER.get_comments method.

        Raises:
            Any exceptions raised by RUMBLE_USER.get_comments will be
            propagated to the caller.
        """
        try:
            raw_comments = RUMBLE_USER.get_comments(self.video_id)
            # Convert the raw comments into Comment objects
            comments = [Comment(*comment_data) for comment_data in raw_comments]
            return comments
        except Exception as e:
            xbmc.log(f"Error fetching comments: {str(e)}", level=xbmc.LOGERROR)
            # notify the user via UI
            xbmcgui.Dialog().notification("Error", "Failed to fetch comments. Please try again later.", xbmcgui.NOTIFICATION)
            return []

    def refresh(self):
        """
        Refreshes the comment list in the CommentWindow.

        This method fetches the latest comments for the current video and updates
        the comment control list in the UI. If comments are found, it populates
        the list with individual comment items. If no comments are found, it
        displays a "No Comments Found" message.

        The method performs the following steps:
        1. Retrieves the comment control list.
        2. Fetches the latest comments using fetch_comment_list().
        3. If comments are found:
        - Iterates through each comment.
        - Creates a list item for each comment with relevant information.
        - Adds each list item to the comment control list.
        4. If no comments are found and the list is empty:
        - Adds a single item with the "No Comments Found" message.

        Note:
        - The comment data is expected to be a tuple containing various details
        about each comment (e.g., author name, post time, comment text).
        - This method assumes that self.get_comment_control_list(),
        self.fetch_comment_list(), and self.create_list_item() are implemented.

        Returns:
            None
        """

        ccl = self.get_comment_control_list()

        results = self.fetch_comment_list()

        if results:
            for comment in results:
                ccl.addItem(
                    self.create_list_item(
                        comment.comment_id,
                        comment.author_name,
                        comment.post_time_ago,
                        comment.comment_text
                    )
                )

        else:
            if ccl.size() == 0:
                ccl.addItem(xbmcgui.ListItem(label="No Comments Found"))

    def get_comment_control_list(self):
        """
        Retrieves the comment control list from the window.

        This method returns the control object responsible for displaying
        the list of comments in the user interface. The control is identified
        by the ID 1 in the window's XML layout.

        Returns:
            xbmcgui.ControlList: The control object for the comment list.

        Note:
            This method assumes that the comment list control has an ID of 1
            in the window's XML definition. If the ID changes, this method
            should be updated accordingly.
        """
        return self.getControl(1)

    def create_list_item(self, comment_id, comment_author_name, comment_post_time_ago, comment):
        """
        Creates a ListItem object for a single comment to be displayed in the Kodi UI.

        This method constructs a xbmcgui.ListItem object that represents a comment
        in the Rumble video comments list. It sets the label of the ListItem using
        the create_label method and stores additional comment data as properties
        of the ListItem.

        Args:
            comment_id (str): The unique identifier of the comment.
            comment_author_name (str): The name of the comment's author.
            comment_post_time_ago (str): A string representing how long ago the comment was posted.
            comment (str): The text content of the comment.

        Returns:
            xbmcgui.ListItem: A fully configured ListItem object representing the comment.

        Note:
            The created ListItem includes the following properties:
            - 'id': The comment's unique identifier
            - 'comment_author_name': The name of the comment's author
            - 'comment_post_time_ago': When the comment was posted
            - 'comment': The full text of the comment

        These properties can be accessed later for refreshing the display or
        handling user interactions with the comment item.
        """

        line_item = xbmcgui.ListItem(
            label=self.create_label(
                comment_id,
                comment_author_name,
                comment_post_time_ago,
                comment
            )
        )
        line_item.setProperty('id', comment_id)
        line_item.setProperty('comment_author_name', comment_author_name)
        line_item.setProperty('comment_post_time_ago', comment_post_time_ago)
        line_item.setProperty('comment', comment)
        return line_item

    def refresh_label(self, line_item, selected=True):
        """
        Refreshes the label of a comment item in the Kodi UI.

        This method updates the display of a comment by retrieving its properties
        and creating a new label using the create_label method. It's typically used
        when the appearance of a comment needs to be updated, such as when it's
        selected or deselected in the UI.

        Args:
            line_item (xbmcgui.ListItem): The ListItem object representing the comment
                in the Kodi UI. This object should have properties set for 'id',
                'comment_author_name', 'comment_post_time_ago', and 'comment'.
            selected (bool, optional): Indicates whether the item is currently selected.
                Defaults to True.

        Returns:
            None

        Note:
            This method assumes that the line_item has been previously created with
            the necessary properties set. It uses the create_label method to format
            the label string.

        Example:
            comment_item = xbmcgui.ListItem()
            comment_item.setProperty('id', '12345')
            comment_item.setProperty('comment_author_name', 'John Doe')
            comment_item.setProperty('comment_post_time_ago', '2 hours ago')
            comment_item.setProperty('comment', 'Great video!')
            self.refresh_label(comment_item, selected=True)
        """

        comment_id = line_item.getProperty('id')
        comment_author_name = line_item.getProperty('comment_author_name')
        comment_post_time_ago = line_item.getProperty('comment_post_time_ago')
        comment = line_item.getProperty('comment')
        line_item.setLabel(
            self.create_label(
                comment_id,
                comment_author_name,
                comment_post_time_ago,
                comment,
                selected
            )
        )

    def create_label(self, comment_id, comment_author_name, comment_post_time_ago, comment, selected=False):
        """
        Creates a formatted label string for displaying a comment in the Kodi UI.

        This method constructs a string that combines the comment author's name,
        the comment text, and the time since the comment was posted. It uses
        Kodi's color tags to style different parts of the label for better
        visual distinction in the UI.

        Args:
            comment_id (str): The unique identifier of the comment. Not used in
                              the current implementation but may be useful for
                              future enhancements.
            comment_author_name (str): The name of the comment's author.
            comment_post_time_ago (str): A string representing how long ago the
                                         comment was posted (e.g., "2 hours ago").
            comment (str): The text content of the comment.
            selected (bool, optional): Indicates whether the comment is currently
                                       selected in the UI. Not used in the current
                                       implementation. Defaults to False.

        Returns:
            str: A formatted string representing the comment, ready for display
                 in the Kodi UI. The string includes Kodi color tags for styling.

        Example:
            >>> create_label("123", "JohnDoe", "2 hours ago", "Great video!")
            'JohnDoe [COLOR white]Great video![/COLOR] [COLOR orange](2 hours ago)[/COLOR]'

        Note:
            - The comment text is processed through the clean_text() function,
              which is assumed to sanitize or format the text appropriately.
            - Kodi color tags are used: white for the comment text and orange
              for the post time.
        """
        return comment_author_name + ' [COLOR white]' + clean_text( comment ) \
            + '[/COLOR] [COLOR orange](' + comment_post_time_ago + ')[/COLOR]'
