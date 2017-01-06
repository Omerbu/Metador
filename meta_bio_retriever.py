# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
from kivy.network.urlrequest import UrlRequest


def lastfm_bio_handler(artist, callback_function):

    def search_lastfm(_, html_content, maxchars=300):
        if not html_content:
            lastfm_bio_handler.callback("No Artist Biography Found ")
        soup = BeautifulSoup(html_content, "html.parser")
        wiki_content = soup.find("div", {"class": "wiki-content"})
        try:
            text = wiki_content.get_text(separator=" ", strip=True)
        except AttributeError:
            return None
        parsed_bio = text[:maxchars]
        lastfm_bio_handler.callback(parsed_bio)

    url_lastfm = "http://www.last.fm/music/"
    page = artist.replace(" ", "+") + "/+wiki"
    full_address = url_lastfm + page
    lastfm_bio_handler.callback = callback_function
    url_req = UrlRequest(full_address, on_success=search_lastfm)

