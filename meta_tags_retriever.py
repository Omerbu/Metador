# -*- coding: utf-8 -*-
"""Module for returning track Metadata (music-tags)."""
import re
import pygn
import urllib
import discogs_client
from bs4 import BeautifulSoup
from meta_utils import FuncTimeitWrapper

pygn_userID = "27680793551513575-12D4F149E8C4D17B6E76872200F49455"
pygn_clientID = '1735505540-C6C936F2054DA76A0D98E82163189CF0'
# userID = pygn.register(clientID)        # register time is about 2 sec.
discogs_access_token = "LifLerwCJirFtBnEFUDXnhXOWPfZiuBpKutzuLVW"
discogs_user_agent = "Metador_Application_AutoTagger"

@FuncTimeitWrapper
def main(artist_name, track_name):
    """Receive artist + track name and return music-tags from GraceNote API.
        More DOCS!
    :param artist_name:
    :param track_name:
    :return: a dictionary containing music-tags

    """
    tags_results = pygn.search(pygn_clientID, pygn_userID,
                               artist=artist_name, track=track_name)
    tags_dictionary = dict()
    tags_dictionary['album'] = tags_results["album_title"]
    tags_dictionary['year'] = tags_results["album_year"]
    tags_dictionary['track_number'] = tags_results["track_number"]
    tags_dictionary['track_title'] = tags_results["track_title"]
    tags_dictionary["artist"] = artist_name
    tags_dictionary["album_artist"] = tags_results["album_artist_name"]
    tags_dictionary["genre"] = tags_results['genre']['3']['TEXT']
    image_url = tags_results["album_art_url"]
    if image_url:
        image_binary_string = urllib.urlopen(image_url).read()
        tags_dictionary["album_art"] = image_binary_string
    else:
        print "can't find album art"
        image_binary_string = album_art_finder(
            tags_dictionary["album"], artist_name)
        tags_dictionary["album_art"] = image_binary_string
    validate_tags(tags_dictionary, artist_name)
    debug_print(tags_results)
    return tags_dictionary


def validate_tags(tags_dictionary, artist_name):
    """
    DOC needed.
    :param tags_dictionary:
    :param artist_name:
    :return:
    """
    for key in tags_dictionary:
        if not tags_dictionary[key]:
            secondary_search(tags_dictionary, tags_dictionary["album"], artist_name)


def secondary_search(tags_dictionary, album_string, artist_name):
    """
    Discogs Based API.
    :return:
    """
    client = discogs_client.Client(user_agent=discogs_user_agent,
                                   user_token=discogs_access_token)
    results = client.search(title=album_string,
                            artist=artist_name,
                            type="master")
    master_id = results[0].id
    master_result = client.master(master_id)
    album_result = master_result.main_release
    tags_dictionary["genres"] = album_result.genres[0]
    tags_dictionary["year"] = album_result.year


def album_art_finder(album_name, artist_name):
    """
    Not Complete!

    :param album_name:
    :param artist_name:
    :return:
    """
    parsed_album = album_name.replace(" ", "+")
    parsed_artist = artist_name.replace(" ", "+")
    search_url = u"https://musicbrainz.org/taglookup?tag-lookup.artist={0}&tag-lookup.release={1}".format(
        parsed_artist, parsed_album)
    url = urllib.urlopen(search_url.encode("UTF-8"))
    html_string = url.read()
    soup = BeautifulSoup(html_string, "html.parser")
    table = soup.find("table", class_="tbl")
    table_soup = BeautifulSoup(str(table))
    string = table_soup.find(string=re.compile(album_name[:3]))
    links = string.find_parents("a")
    album_link = links[0]
    album_link = album_link["href"]
    album_page_html = urllib.urlopen("https://musicbrainz.org/" + album_link).read()
    album_page = BeautifulSoup(album_page_html, "html.parser")
    cover = album_page.find("div", class_="cover-art")
    cover_link = cover.img["src"]
    image_binary_string = urllib.urlopen(cover_link).read()
    urllib.urlretrieve(cover_link, "test_file.jpg")
    return image_binary_string


def debug_print(tags_results):
    """
    Printing For debuging purposes, won't be in final version.
    :param tags_results:
    :return:
    """
    print tags_results['album_title']
    print tags_results['genre']['3']['TEXT']
    print tags_results['album_year']
    print tags_results['track_number']
    print tags_results["album_art_url"]
    print tags_results["track_title"]
    print tags_results["album_artist_name"]
