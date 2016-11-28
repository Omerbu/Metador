# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2


def search_wiki(artist):
    """ Retrieve artist's bio from Wikipedia.

    Returns the first paragraph of a Wikipedia article as string.
    If no article found, returns None.
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
    return first_paragraph.text
