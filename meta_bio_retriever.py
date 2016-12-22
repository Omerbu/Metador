# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
from kivy.network.urlrequest import UrlRequest


def search_wiki(artist, maxchars=300):
    """ Retrieve artist's bio from Wikipedia.

    Args:
        artist (string): The name of the artist (or band) to be searched.
        maxchars (int): The maximum number of characters to return.

    Returns:
        A tuple containing the retrieved text (up to maxchars) and the url of the page.
        If no data was found, returns None.
    """

    url_wiki = "https://en.wikipedia.org/wiki/"
    url_search = "https://en.wikipedia.org/w/index.php?search="
    article = artist.replace(" ", "_")
    s_article = artist.replace(" ", "+")
    try:
        html_content = urllib2.urlopen(url_wiki + article + "_(band)")
    except urllib2.HTTPError:
        html_content = urllib2.urlopen(url_search + s_article)
    soup = BeautifulSoup(html_content, "html.parser")
    page_title = soup.find("h1", {"id": "firstHeading", "class": "firstHeading"})
    if page_title.text == "Search results":
        search_results = soup.find("div", {"class": "searchresults"})
        url_result = search_results.ul.li.a.get("href")        # getting the link from the first result
        if url_result.startswith("http"):
            html_content = urllib2.urlopen(url_result)
            soup = BeautifulSoup(html_content, "html.parser")
        else:
            return
    first_paragraph = soup.p
    for cite in first_paragraph.find_all("sup"):
        cite.decompose()
    for ipa in first_paragraph.find_all("span", {"class": "IPA"}):
        ipa.parent.decompose()
    return first_paragraph.text[:maxchars], html_content.geturl()


class BioRetriever(object):

    def lastfm_bio_handler(self, artist, callback_function):
        url_lastfm = "http://www.last.fm/music/"
        page = artist.replace(" ", "+") + "/+wiki"
        full_address = url_lastfm + page
        self.callback_function = callback_function
        url_req = UrlRequest(full_address, self.search_lastfm)

    def search_lastfm(self, req, html_content, maxchars=300):
        """ Retrieve artist's bio from LastFM.

        Args:
            artist (string): The name of the artist (or band) to be searched.
            maxchars (int): The maximum number of characters to return.

        Returns:
            A tuple containing the retrieved text (up to maxchars) and the url of the page.
            If no data was found, returns None.
        """

        soup = BeautifulSoup(html_content, "html.parser")
        wiki_content = soup.find("div", {"class": "wiki-content"})
        try:
            text = wiki_content.get_text(separator="\n", strip=True)
        except AttributeError:
            return None
        parsed_bio = text[:maxchars]
        self.callback_function(parsed_bio)
