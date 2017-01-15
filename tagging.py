# -*- coding: utf-8 -*-

import re
from mutagen import MutagenError, File
from mutagen.id3 import ID3, ID3NoHeaderError, TPE1, TALB, TIT2, TRCK, TDRC, TCON, TPE2, APIC
from mutagen.mp4 import MP4, MP4Cover
from mutagen.apev2 import APEv2, APENoHeaderError
from mutagen.flac import FLAC, Picture
from PIL import Image
from StringIO import StringIO


class MP3Tagger(object):
    def __init__(self, filename):
        try:
            ID3(filename)
        except ID3NoHeaderError:
            ID3().save(filename)
        self.tags = ID3(filename)
        self.fname = filename

    def __getitem__(self, item):
        return unicode(self.tags[item].text[0])

    def __setitem__(self, key, value):
        tag = globals().get(key)            # translates the string to a class name
        enc = 0 if value.isdigit() else 3   # Encoding.LATIN1 for numbers. Encoding.UTF8 otherwise.
        self.tags.setall(key, [tag(encoding=enc, text=unicode(value))])
        self.tags.save(self.fname)

    def get_cover(self):
        if 'APIC:' in self.tags:
            return self.tags['APIC:'].data
        else:
            return

    def set_cover(self, image_string):
        cover = APIC(
                    encoding=3,     # 3 is for utf-8
                    mime="image/jpeg",
                    type=3,         # 3 is for the cover image
                    desc=u'Front Cover',
                    data=image_string
                )
        self.tags.setall("APIC:", [cover])
        self.tags.save(self.fname)

    def clear_tags(self):
        ID3().save(self.fname)
        self.tags = ID3(self.fname)


class MP4Tagger(object):
    def __init__(self, filename):
        self.tags = MP4(filename)
        self.fname = filename

    def __getitem__(self, item):
        if item == "trkn":
            return unicode(self.tags[item][0][0])
        else:
            return unicode(self.tags[item][0])

    def __setitem__(self, key, value):
        if key == "trkn":
            try:
                value = (int(value), 0)
            except ValueError:
                value = self.tags["trkn"][0]
        else:
            value = unicode(value)
        self.tags[key] = [value]
        self.tags.save(self.fname)

    def get_cover(self):
        if 'covr' in self.tags:
            return bytes(self.tags['covr'][0])
        else:
            return

    def set_cover(self, image_string):
        cover = MP4Cover(image_string, MP4Cover.FORMAT_JPEG)
        self.tags['covr'] = [cover]
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

    def __getitem__(self, item):
        return unicode(self.tags[item].value)

    def __setitem__(self, key, value):
        self.tags[key] = value
        self.tags.save(self.fname)

    def get_cover(self):
        # to be added
        return

    def set_cover(self, image_string):
        # to be added
        pass

    def clear_tags(self):
        self.tags = APEv2()
        self.tags.save(self.fname)


class FlacTagger(object):
    def __init__(self, filename):
        self.tags = FLAC(filename)
        self.fname = filename

    def __getitem__(self, item):
        return unicode(self.tags[item][0])

    def __setitem__(self, key, value):
        self.tags[key] = [unicode(value)]
        self.tags.save(self.fname)

    def get_cover(self):
        if self.tags.pictures:
            return self.tags.pictures[0].data
        else:
            return

    def set_cover(self, image_string):
        pic = Picture()
        pic.data = image_string
        pic.type = 3
        pic.desc = u'Front Cover'
        pic.mime = "image/jpeg"
        self.tags.clear_pictures()
        self.tags.add_picture(pic)
        self.tags.save(self.fname)

    def clear_tags(self):
        self.tags.delete()
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
        try:
            self.extension = re.search(r"\.[^.]+$", self.fname).group()
        except AttributeError:
            self.extension = ''

        if self.extension in self.TAGGERS:
            self.tagger = EasyTagger.TAGGERS[self.extension](filename)
        else:
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

    @staticmethod
    def as_jpeg(image_string):
        im = Image.open(StringIO(image_string))
        if im.format == "JPEG":
            return image_string
        out_string_io = StringIO()
        im.save(out_string_io, "JPEG")
        jpeg_str = out_string_io.getvalue()
        return jpeg_str

    def get_duration(self, minute_string=True):
        seconds = int(File(self.fname).info.length)
        if minute_string:
            return str(seconds / 60) + ':' + str(seconds % 60).zfill(2)
        return seconds

    def get_cover(self):
        img_str = self.tagger.get_cover()
        return EasyTagger.as_jpeg(img_str)

    def set_cover(self, image_string):
        image_string = EasyTagger.as_jpeg(image_string)
        self.tagger.set_cover(image_string)

    def __getitem__(self, item):
        item = item.title()
        try:
            if self.extension in ['.mp3', '.aiff']:
                val = self.tagger[EasyTagger.id3_trans(item)]
            elif self.extension in ['.m4a']:
                val = self.tagger[EasyTagger.mp4_trans(item)]
            else:
                val = self.tagger[item]
        except KeyError:
            return u''
        if item == "Tracknumber":
            try:
                val = re.search(r"\d+(?=\D|\Z)", val).group()       # the first digit-only characters
            except AttributeError:
                pass
        return val

    def __setitem__(self, key, value):
        # will raise MutagenError if the file is read-only.
        key = key.title()
        if self.extension in ['.mp3']:
            key = EasyTagger.id3_trans(key)
        if self.extension in ['.m4a']:
            key = EasyTagger.mp4_trans(key)
        self.tagger[key] = value

    def get_tags(self):
        return {key: self[key] for key in EasyTagger.FIELDS}

    def set_tags(self, tags_dict):
        self.clean_tags()
        for key in tags_dict:
            self[key] = tags_dict[key]

    def clean_tags(self):
        old_tags = self.get_tags()
        self.tagger.clear_tags()
        for key in old_tags:
            self[key] = old_tags[key]
