# -*- coding: utf-8 -*-
"""Module for returning track Metadata (music-tags)."""
import pygn
import sys
from meta_utils import FuncTimeitWrapper
reload(sys)
sys.setdefaultencoding('utf8')

clientID = '1735505540-C6C936F2054DA76A0D98E82163189CF0'
userID = pygn.register(clientID)        # register time is about 2 sec.


@FuncTimeitWrapper
def main(artist_name, track_name):
    """Receive artist + track name and return music-tags from GraceNote API.

    :param artist_name:
    :param track_name:
    :return: a dictionary containing music-tags

    """
    tags_results = pygn.search(clientID, userID,
                               artist=artist_name, track=track_name)
    tags_dictionary = dict()
    tags_dictionary['album'] = tags_results["album_title"]
    tags_dictionary['year'] = tags_results["album_year"]
    tags_dictionary['track_number'] = tags_results["track_number"]
    tags_dictionary['album'] = tags_results["album_title"]
    tags_dictionary['track_title'] = tags_results["track_title"]
    tags_dictionary["artist"] = artist_name
    print tags_results['album_title']
    print tags_results['genre']['3']['TEXT']
    print tags_results['album_year']
    print tags_results['track_number']
    print tags_results["album_art_url"]
    print tags_results["track_title"]
