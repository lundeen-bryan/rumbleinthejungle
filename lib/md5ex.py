# Auto updated?
#   Yes
# Modified:
#   Monday, March 3, 2025 8:22:44 PM PST
#
"""
The snippet above is from an Ext from TheRepoClub called File Header Generator
==========================================================================================
Procedure: ......... md5ex.py
Description: ....... Generates MD5 hash for a given string or file used to login to Rumble.
Version: ........... 1.0.0 - major.minor.patch
Created: ........... 2025-03-03
Updated: ........... 2025-03-03
Module URL: ........ weburl
Installs to: ....... plugin.video.rumbleinthejungle/lib
Compatibility: ..... Kodi, Kodi 16+
Contact Author: .... lundeen-bryan
Copyright:  ........ n/a © 2025. All rights reserved.
Preconditions: ..... precondition
Examples: .......... _
 (1) examples_here
    md5 = MD5Ex()
    print(md5.hash("Hello, World!"))
    print(md5.hashStretch("Hello, World!", "somesalt", 1024))
Notes: ............. _
 (1) notes_here
    - Implements MD5 hashing using Python's built-in hashlib module.
    - Generates both hexadecimal and raw binary MD5 digests.
    - Processes UTF-8 encoded strings for proper handling of non-ASCII characters.
    - Provides a hash stretching function to enhance security with iterative hashing.
    - Offers a modern, Pythonic, and compact alternative to legacy MD5 implementations.This module provides a re-implementation of the MD5Ex class using Python's built-in hashlib module.
===========================================================================================
"""

import hashlib
from typing import Union

class MD5Ex:
    """
    MD5Ex class using Python's hashlib for MD5 hash generation.
    """

    def hash(self, input_str: str) -> str:
        """
        Generate an MD5 hash for the given input string.

        Args:
            input_str (str): The input string to be hashed.

        Returns:
            str: The MD5 hash in hexadecimal format.
        """
        return hashlib.md5(input_str.encode('utf-8')).hexdigest()

    def hashUTF8(self, input_str: str) -> str:
        """
        Generate an MD5 hash for the UTF-8 encoded input string.

        Args:
            input_str (str): The input string to be hashed.

        Returns:
            str: The MD5 hash in hexadecimal format.
        """
        # In this implementation, UTF-8 encoding is inherent in the hash method.
        return self.hash(input_str)

    def hashRaw(self, input_str: str) -> bytes:
        """
        Generate a raw MD5 hash for the given input string.

        Args:
            input_str (str): The input string to be hashed.

        Returns:
            bytes: The MD5 hash as a raw binary digest.
        """
        return hashlib.md5(input_str.encode('utf-8')).digest()

    def hashRawUTF8(self, input_str: str) -> bytes:
        """
        Generate a raw MD5 hash for the UTF-8 encoded input string.

        Args:
            input_str (str): The input string to be hashed.

        Returns:
            bytes: The MD5 hash as a raw binary digest.
        """
        return self.hashRaw(input_str)

    def hashStretch(self, input_str: str, salt: str, iterations: int = 1024) -> str:
        """
        Generate an MD5 hash with stretching (repeated hashing) for added security.

        This method combines the input string with a salt and applies the MD5 hashing process
        iteratively for the specified number of iterations.

        Args:
            input_str (str): The input string to be hashed.
            salt (str): The salt value to be prepended to the input string.
            iterations (int, optional): The number of hashing iterations. Defaults to 1024.

        Returns:
            str: The resulting MD5 hash in hexadecimal format after stretching.
        """
        current_hash = salt + input_str
        for _ in range(iterations):
            current_hash = hashlib.md5(current_hash.encode('utf-8')).hexdigest()
        return current_hash
