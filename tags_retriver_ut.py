# -*- coding: utf-8 -*-

import meta_tags_retriever
import metacore
import meta_result_parser
from meta_utils import func_decorator

@func_decorator
def retriever_check(artist, song_name):

    meta_tags_retriever.main(artist, song_name)

@func_decorator
def integration_check(input_file):
    result, org_dur = metacore.fingerprint_search(input_file)
    song = meta_result_parser.ResultParser(result, org_dur)
    artist, song_name = song.main()
    meta_tags_retriever.main(artist, song_name)

if __name__ == "__main__":
    integration_check()
