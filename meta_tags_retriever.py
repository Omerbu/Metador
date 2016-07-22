# -*- coding: utf-8 -*-
"""Module for returning track Metadata (music-tags)."""
import re
import pygn
import urllib
import discogs_client
from bs4 import BeautifulSoup
from meta_utils import func_decorator
import pylast

pygn_userID = "27680793551513575-12D4F149E8C4D17B6E76872200F49455"
pygn_clientID = '1735505540-C6C936F2054DA76A0D98E82163189CF0'
# userID = pygn.register(clientID)        # register time is about 2 sec.

discogs_access_token = "LifLerwCJirFtBnEFUDXnhXOWPfZiuBpKutzuLVW"
discogs_user_agent = "Metador_Application_AutoTagger"

lastfmKey = "78b2431b39da9c451b8c000b02c687d7"
lastfmSecret = "6b8c8647c71244ff4faca5aa5efc73ac"


@func_decorator
def main(artist_name, track_name):
    """Receive artist + track name and return music-tags from GraceNote API.
        If Pygn results are incomplete, runs a secondary search algorithm that searches
        discogs DB and LastFM DB (for now)
    """
    tags_results = pygn.search(pygn_clientID, pygn_userID,
                               artist=artist_name, track=track_name)
    tags_dictionary = dict()
    tags_dictionary['album'] = tags_results["album_title"]
    tags_dictionary['year'] = tags_results["album_year"]
    tags_dictionary['track_number'] = tags_results["track_number"]
    tags_dictionary['track_title'] = track_name
    tags_dictionary["artist"] = artist_name
    tags_dictionary["album_artist"] = tags_results["album_artist_name"]
    tags_dictionary["genre"] = tags_results['genre']['3']['TEXT']
    image_url = tags_results["album_art_url"]
    if image_url:
        image_binary_string = urllib.urlopen(image_url).read()
    else:
        print "No Pygn album art"
        image_binary_string = None
    validate_tags(tags_dictionary, artist_name, track_name)
    debug_print(tags_dictionary)
    return tags_dictionary, image_binary_string


def validate_tags(tags_dictionary, artist_name, track_name):
    """Checks if Pygn search has returned all the required tags, if not
    will run secondary search algorithm.
    """
    for key in tags_dictionary:
        if not tags_dictionary[key]:
            discogs_search(tags_dictionary, tags_dictionary["album"], artist_name, )


@func_decorator
def discogs_search(tags_dictionary, album_string, artist_name, track_name):
    """
    Working but needed to add an option to search without artist.
    :return:
    """
    print "seconary search activated"
    client = discogs_client.Client(user_agent=discogs_user_agent,
                                   user_token=discogs_access_token)
    results = client.search(title=artist_name,
                            artist=artist_name,
                            type="master")
    master_id = results[0].id
    master_result = client.master(master_id)
    album_result = master_result.main_release
    for track in album_result.tracklist:
        if track.title == track_name:
            tags_dictionary["track_number"] = track.position
            break
    tags_dictionary["genres"] = album_result.genres[0]
    tags_dictionary["year"] = album_result.year


def lastfm_search(artist_name, track_name):
    """
    Experimental Phase!!!
    :param artist_name:
    :param track_name:
    :return:
    """
    lastfm_client = pylast.LastFMNetwork(lastfmKey, lastfmSecret)
    result = lastfm_client.get_track(artist_name, track_name)
    album = result.get_album()
    album_url = album.get_url()
    print album.get_cover_image()
    url = urllib.urlopen(album_url.encode("UTF-8"))
    album_soup = BeautifulSoup(url.read(), "html.parser")


def brainz_album_art(album_name, artist_name):
    """Crawl the musicbrainz website in search for album art cover."""
    parsed_album = album_name.replace(" ", "+")
    parsed_artist = artist_name.replace(" ", "+")
    search_url = \
        u"https://musicbrainz.org/taglookup?tag-lookup.artist={0}&tag-lookup.release={1}"\
            .format(parsed_artist, parsed_album)
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


def debug_print(tags_dictionary):
    """
    Printing For debuging purposes, won't be in final version.
    :param tags_dictionary:
    :return:
    """
    print tags_dictionary['album']
    print tags_dictionary['genre']
    print tags_dictionary['year']
    print tags_dictionary['track_number']
    print tags_dictionary["track_title"]
    print tags_dictionary["album_artist"]
    print tags_dictionary["artist"]

