import xbmc
import xbmcgui

import requests

from lib.general import *
from lib.rumble_user import RumbleUser

RUMBLE_USER = RumbleUser()

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
        return RUMBLE_USER.get_comments(self.video_id)

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
            for comment_author_url, comment_author_name, comment_id, \
                comment_post_day, comment_post_month, comment_post_date, comment_post_year, \
                comment_post_hour, comment_post_minute, comment_post_meridiem, \
                comment_post_time_ago, comment in results:

                ccl.addItem(
                    self.create_list_item(
                        comment_id,
                        comment_author_name,
                        comment_post_time_ago,
                        comment
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

        """ creates list that will view comment """

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

        """ Refreshes comment label """

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

        """ Creates label to view comments """

        return comment_author_name + ' [COLOR white]' + clean_text( comment ) \
            + '[/COLOR] [COLOR orange](' + comment_post_time_ago + ')[/COLOR]'
