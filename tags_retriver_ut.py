# -*- coding: utf-8 -*-

import meta_tags_retriever
import metacore
import meta_result_parser
from meta_utils import time_decorator


@time_decorator
def retriever_check(artist, song_name):
    meta_tags_retriever.main_search(artist, song_name)


@time_decorator
def integration_check(input_file):
    result, org_dur = metacore.fingerprint_search(input_file)
    song = meta_result_parser.ResultParser(result, org_dur)
    artist, song_name = song.main()
    meta_tags_retriever.main_search(artist, song_name)


@time_decorator
def lastfm_check(artist_name, track_name):
    meta_tags_retriever.lastfm_album_art(artist_name, track_name)

if __name__ == "__main__":
    lastfm_check("The Civil Wars", "The Civil Wars")
