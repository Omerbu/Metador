# -*- coding: utf-8 -*-
import re
from tagging import EasyTagger
import scandir
from os import renames
from os.path import exists, join, realpath

FILE_FILTER = ".*\.(flac|mp3|m4a|wv|mpc)$"


def move_file(old_path, new_path):
    """ Safely rename a file. Make a copy if the destination file name is taken. """
    try:
        ext = re.search(r"\.[^.]+$", old_path).group()
    except AttributeError:
        ext = ""
    dst = new_path
    n = 1
    while dst != old_path and exists(dst):
        # insert a number at the end of the file name if it is taken.
        dst = re.sub(r"\.[^.]+$", " (" + str(n) + ")" + ext, new_path)
        n += 1
    renames(old_path, dst)


def create_name(file_path):
    """ Return a name based on the file's metadata. """
    tags = EasyTagger(file_path).get_tags()
    for field in tags:
        # change empty values
        if tags[field] == "":
            if field == "Tracknumber":
                tags[field] = "--"
            else:
                tags[field] = "Unknown"
        # replace forbidden characters
        tags[field] = re.sub(r"[\\/:*?<>|]", "-", tags[field])
        tags[field] = re.sub(r"\"", "'", tags[field])
    try:
        ext = re.search(r"\.[^.]+$", file_path).group()
    except AttributeError:
        ext = ""
    return join(tags["Albumartist"], tags["Album"], (tags["Tracknumber"].zfill(2) + ". " + tags["Title"] + ext))


def sort_file(filename, root_path):
    """ Rename a file and move it to an appropriate folder based on it's metadata. """
    move_file(realpath(filename), realpath(join(root_path, create_name(realpath(filename)))))


def organize(root_path):
    """ Run through all audio files under the given directory and rename them appropriately. """
    for root, dirs, files in scandir.walk(root_path):
        for name in files:
            if re.match(FILE_FILTER, name):
                sort_file(join(root, name), root_path)
