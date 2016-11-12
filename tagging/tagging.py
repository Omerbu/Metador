import re
from mutagen.id3 import ID3, ID3NoHeaderError, TPE1, TALB, TIT2, TRCK, TDRC, TCON, TPE2, APIC
from mutagen.mp4 import MP4
from mutagen.apev2 import APEv2, APENoHeaderError
from mutagen.flac import FLAC


class MP3Tagger(object):
    def __init__(self, filename):
        try:
            ID3(filename)
        except ID3NoHeaderError:
            ID3().save(filename)
        self.tags = ID3(filename)
        self.fname = filename

    def get_value(self, field):
        return unicode(self.tags[field].text[0])

    def edit_value(self, field, value):
        tag = globals().get(field)
        enc = 0 if value.isdigit() else 1   # Encoding.LATIN1 for numbers. Encoding.UTF16 otherwise.
        self.tags.add(tag(encoding=enc, text=value))
        self.tags.save(self.fname)

    def clear_tags(self):
        ID3().save(self.fname)
        self.tags = ID3(self.fname)


class MP4Tagger(object):
    def __init__(self, filename):
        self.tags = MP4(filename)
        self.fname = filename

    def get_value(self, field):
        if field == "trkn":
            return unicode(self.tags[field][0][0])
        else:
            return unicode(self.tags[field][0])

    def edit_value(self, field, value):
        if field == "trkn":
            try:
                value = (int(value), 0)
            except ValueError:
                value = self.tags["trkn"][0]
        else:
            value = unicode(value)
        self.tags[field] = [value]
        self.tags.save(self.fname)

    def clear_tags(self):
        self.tags.delete()
        MP4().save(self.fname)
        self.tags = MP4(self.fname)


class APEv2Tagger(object):
    def __init__(self, filename):
        try:
            self.tags = APEv2(filename)
        except APENoHeaderError:
            self.tags = APEv2()
        self.fname = filename

    def get_value(self, field):
        return unicode(self.tags[field].value)

    def edit_value(self, field, value):
        self.tags[field] = value
        self.tags.save(self.fname)

    def clear_tags(self):
        self.tags = APEv2()
        self.tags.save(self.fname)


class FlacTagger(object):
    def __init__(self, filename):
        self.tags = FLAC(filename)
        self.fname = filename

    def get_value(self, field):
        return unicode(self.tags[field][0])

    def edit_value(self, field, value):
        self.tags[field] = [unicode(value)]
        self.tags.save(self.fname)

    def clear_tags(self):
        self.tags = FLAC()
        self.tags.save(self.fname)


class MetadorTaggerError(Exception):
    pass


class EasyTagger(object):
    FIELDS = ['Album', 'Artist', 'Title', 'Tracknumber', 'Date', 'Genre', 'Albumartist']
    TAGGERS = {'.mp3': MP3Tagger,
               '.m4a': MP4Tagger,
               '.flac': FlacTagger,
               '.mpc': APEv2Tagger,
               '.wv': APEv2Tagger}

    def __init__(self, filename):
        self.fname = filename
        # use regex to determine the file's extension.
        try:
            self.extension = re.search(r"\.[^.]+$", self.fname).group()
        except AttributeError:
            self.extension = ''
        # choose appropriate tagger for this file type.
        try:
            self.tagger = self.TAGGERS[self.extension](filename)
        except KeyError:
            raise MetadorTaggerError("unsupported file type")

    @staticmethod
    def id3_trans(field):
        id3dict = {'album': 'TALB', 'artist': 'TPE1', 'title': 'TIT2', 'tracknumber': 'TRCK', 'date': 'TDRC',
                   'genre': 'TCON', 'albumartist': 'TPE2'}
        try:
            return id3dict[field.lower()]
        except KeyError:
            return field

    @staticmethod
    def mp4_trans(field):
        mp4dict = {'album': '\xa9alb', 'artist': '\xa9ART', 'title': '\xa9nam', 'tracknumber': 'trkn',
                   'date': '\xa9day', 'genre': '\xa9gen', 'albumartist': 'aART'}
        try:
            return mp4dict[field.lower()]
        except KeyError:
            return field

    def get_value(self, field):
        field = field.title()
        if self.extension in ['.mp3', '.aiff']:
            val = self.tagger.get_value(EasyTagger.id3_trans(field))
        elif self.extension in ['.m4a']:
            val = self.tagger.get_value(EasyTagger.mp4_trans(field))
        else:
            val = n self.tagger.get_value(field)
        if field == "Tracknumber":
            try:
                val = re.search(r"\d+(?=\D|\Z)", val).group()
            except AttributeError:
                pass
        return val

    def edit_value(self, field, value):
        field = field.title()
        if self.extension in ['.mp3', '.aiff']:
            self.tagger.edit_value(EasyTagger.id3_trans(field), value)
        elif self.extension in ['.m4a']:
            self.tagger.edit_value(EasyTagger.mp4_trans(field), value)
        else:
            self.tagger.edit_value(field, value)

    def get_tags(self):
        tags_dict = {}
        for key in self.FIELDS:
            try:
                tags_dict[key] = self.get_value(key)
            except KeyError:
                tags_dict[key] = ''
        return tags_dict

    def set_tags(self, tags_dict):
        self.tagger.clear_tags()
        for key in tags_dict:
            self.edit_value(key, tags_dict[key])

t = MP3Tagger("C:/Users/newma/Music/Camel/Camel/01-Slow Yourself Down.mp3")
print t.get_value("TRCK")