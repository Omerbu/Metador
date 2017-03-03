# -*- coding: utf-8 -*-
"""Module for returning track Metadata (music-tags)."""
import re
import pygn
import urllib
import discogs_client
from bs4 import BeautifulSoup
import pylast
from utils import time_decorator

# GraceNote API keys:
pygn_userID = "27962471776224303-FF72AD796AB3BFD8639F5455B63BD7EE"
pygn_clientID = '1735505540-C6C936F2054DA76A0D98E82163189CF0'
# userID = pygn.register(pygn_clientID)        # register time is about 2 sec.

# DisCogs API keys:
discogs_access_token = "LifLerwCJirFtBnEFUDXnhXOWPfZiuBpKutzuLVW"
discogs_user_agent = "Metador_Application_AutoTagger"

# LastFM API keys:
lastfmKey = "78b2431b39da9c451b8c000b02c687d7"
lastfmSecret = "6b8c8647c71244ff4faca5aa5efc73ac"

@time_decorator
def main_search(artist_name, track_name):
    """Receive artist + track name and return music-tags from GraceNote API.
        If Pygn results are incomplete, runs a secondary search algorithm that searches
        discogs DB and LastFM DB (for now)
    """
    pygn_results = pygn.search(pygn_clientID, pygn_userID,
                               artist=artist_name, track=track_name)
    tags_dict = dict()
    tags_dict['Album'] = pygn_results["album_title"]
    tags_dict['Date'] = pygn_results["album_year"]
    tags_dict['Tracknumber'] = pygn_results["track_number"]
    tags_dict['Title'] = track_name
    tags_dict["Artist"] = artist_name
    tags_dict["Albumartist"] = pygn_results["album_artist_name"]
    tags_dict["Genre"] = pygn_results['genre']['3']['TEXT']
    album_art_url = pygn_results["album_art_url"]
    if album_art_url:
        image_binary_string = urllib.urlopen(album_art_url).read()
    else:
        print "No Pygn album art"   # Dev Purposes
        image_binary_string = lastfm_album_art(
            tags_dict["Artist"], tags_dict["Album"])
    validate_tags(tags_dict, artist_name, track_name)
    return tags_dict, image_binary_string


def validate_tags(tags_dict, artist_name, track_name):
    """Checks if Pygn search has returned all the required tags, if not
    will run secondary search algorithm.
    """
    for key in tags_dict:
        if not tags_dict[key]:
            discogs_search(tags_dict, tags_dict["Album"],
                           artist_name, track_name)
            return


def discogs_search(tags_dict, album_string, artist_name, track_name):
    """
    Working but needed to add an option to search without artist.
    :return:
    """
    print "Secondary search activated"
    client = discogs_client.Client(user_agent=discogs_user_agent,
                                   user_token=discogs_access_token)
    results = client.search(title=album_string,
                            artist=artist_name,
                            type="master")
    master_id = results[0].id
    master_result = client.master(master_id)
    album_result = master_result.main_release
    for track in album_result.tracklist:
        if track.title == track_name:
            tags_dict["Tracknumber"] = track.position
            break
    tags_dict["Genre"] = album_result.genres[0]
    tags_dict["Date"] = album_result.year


def lastfm_album_art(artist_name, album_name):
    """Returns Album Cover from lastfm API."""
    lastfm_client = pylast.LastFMNetwork(lastfmKey, lastfmSecret)
    album = lastfm_client.get_album(artist_name, album_name)
    cover_image_url = album.get_cover_image()
    image_binary_string = urllib.urlopen(cover_image_url).read()
    return image_binary_string


def brainz_album_art(album_name, artist_name):
    """Crawl the musicbrainz website in search for album art cover.

    Since Web Crawling takes time, this should be used only after all APIs
    failed to find album art.

    """
    parsed_album = album_name.replace(" ", "+")
    parsed_artist = artist_name.replace(" ", "+")
    search_url = \
        u"https://musicbrainz.org/" \
        u"taglookup?tag-lookup.artist={0}&tag-lookup.release={1}".format(
            parsed_artist, parsed_album)
    url = urllib.urlopen(search_url.encode("UTF-8"))
    html_string = url.read()
    soup = BeautifulSoup(html_string, "html.parser")
    table = soup.find("table", class_="tbl")
    table_soup = BeautifulSoup(str(table), "html.parser")
    string = table_soup.find(string=re.compile(album_name[:3]))
    links = string.find_parents("a")
    album_link = links[0]
    album_link = album_link["href"]
    album_page_html = urllib.urlopen("https://musicbrainz.org/" + album_link).read()
    album_page = BeautifulSoup(album_page_html, "html.parser")
    cover = album_page.find("div", class_="cover-art")
    cover_link = cover.img["src"]
    image_binary_string = urllib.urlopen("http:" + cover_link).read()
    return image_binary_string


def debug_print(tags_dict):
    """
    Printing For debuging purposes, won't be in final version.
    :param tags_dict:
    :return:
    """
    print tags_dict['Album']
    print tags_dict['Genre']
    print tags_dict['Date']
    print tags_dict['Tracknumber']
    print tags_dict["Title"]
    print tags_dict["Albumartist"]
    print tags_dict["Artist"]
