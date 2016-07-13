from mutagen import File
from mutagen.easymp4 import EasyMP4 # used for .m4a and .mp4 files
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3 # used for .mp3 files

# the AUDIO_TYPES constant dict is used to refer to the mutagen subclasses according to the file format
#
# the TAGS_MAPS constant dict is used to refer to the correct tag names for each file format.
# currently all tags appear the same. that is because the use of EasyID3 and EasyMP4, which mimic the APEv2 format. 
# regardless, this structure is kept for probable future use.
AUDIO_TYPES = {"mp3":EasyID3, "mp4":EasyMP4, "flac":FLAC}
TAGS_MAPS = {'mp3':{'artist':'artist','album':'album','title':'title','track':'tracknumber','year':'date','genre':'genre','albumartist':'albumartist'}, # mp3 tags are EasyID3
             'mp4':{'artist':'artist','album':'album','title':'title','track':'tracknumber','year':'date','genre':'genre','albumartist':'albumartist'}, # mp4 tags are EasyMP4
             'flac':{'artist':'artist','album':'album','title':'title','track':'tracknumber','year':'date','genre':'genre','albumartist':'albumartist'}}


class AudioFile:
    def __init__(self,filename):
        audiotype = File(filename).mime[0].split("/")[1]    # determine the file format
        self.meta = AUDIO_TYPES[audiotype](filename)        # create the tags instance of the appropriate mutagen subclass
        self.tag_map = TAGS_MAPS[audiotype]                 # used to call the tags of any format by the same names
        
    def tag_entry(self,tags_dict):
        '''
            takes a dict of tags. notice the tags_dict keys should match tags2func keys.
            deletes any old tags on the file and sets the new tags.
        '''
        tag2func = {'artist':self.artist,'album':self.album,'title':self.title,'track':self.track,'year':self.year,'genre':self.genre,'albumartist':self.albumartist}
        self.delete_tags()
        for tagname in tags_dict:
            tag2func[tagname](tags_dict[tagname])
        self.meta.save()
    
    def delete_tags(self):
        '''
            remove all the tags from the file.
            this leaves the tags as an empty dict. 
        '''
        self.meta.clear()
        self.meta.save()
    
    def artist(self,entry=None):
        '''
            return or set the file's artist
        '''
        if entry:
            entry = str(entry)
            self.meta[self.tag_map['artist']] = [entry.decode("UTF-8")]
            self.meta.save()
        return self.meta[self.tag_map['artist']][0]
    
    def album(self,entry=None):
        '''
            return or set the file's album
        '''
        if entry:
            entry = str(entry)
            self.meta[self.tag_map['album']] = [entry.decode("UTF-8")]
            self.meta.save()
        return self.meta[self.tag_map['album']][0]
    
    def title(self,entry=None):
        '''
            return or set the file's title
        '''
        if entry:
            entry = str(entry)
            self.meta[self.tag_map['title']] = [entry.decode("UTF-8")]
            self.meta.save()
        return self.meta[self.tag_map['title']][0]
    
    def track(self,entry=None):
        '''
            return or set the file's track number
        '''
        if entry:
            entry = str(entry)
            self.meta[self.tag_map['track']] = [entry.decode("UTF-8")]
            self.meta.save()
        return self.meta[self.tag_map['track']][0]
    
    def year(self,entry=None):
        '''
            return or set the file's year
        '''
        if entry:
            entry = str(entry)
            self.meta[self.tag_map['year']] = [entry.decode("UTF-8")]
            self.meta.save()
        return self.meta[self.tag_map['year']][0]
    
    def genre(self,entry=None):
        '''
            return or set the file's genre
        '''
        if entry:
            entry = str(entry)
            self.meta[self.tag_map['genre']] = [entry.decode("UTF-8")]
            self.meta.save()
        return self.meta[self.tag_map['genre']][0]
    
    def albumartist(self,entry=None):
        '''
            return or set the file's albumartist
        '''
        if entry:
            entry = str(entry)
            self.meta[self.tag_map['albumartist']] = [entry.decode("UTF-8")]
            self.meta.save()
        return self.meta[self.tag_map['albumartist']][0]
    
    def tag_print(self):
        """
            nicely prints the tags. 
            should probably be removed when the project is finished
        """
        print 'Artist:      ' + self.meta[self.tag_map['artist']][0]
        print 'Album:       ' + self.meta[self.tag_map['album']][0]
        print 'Title:       ' + self.meta[self.tag_map['title']][0]
        print 'Track:       ' + self.meta[self.tag_map['track']][0]
        print 'Year:        ' + self.meta[self.tag_map['year']][0]
        print 'Genre:       ' + self.meta[self.tag_map['genre']][0]
        print 'AlbumArtist: ' + self.meta[self.tag_map['albumartist']][0]


def edit_tags(filename,tags_dict):
    '''
       receive a file name to edit and the newly fetched tags.
       delete any old tags located on the file and save the new tags.
       
       current version works only with mp3, flac, and mp4(m4a)
    '''
    audio = AudioFile(filename)
    audio.tag_entry(tags_dict)
    return


def compare_tags(filename, tags2compare):
    '''
        should be used as a last resort for checking best match of new tags.
        
        get a dict of new tags and compare each tag to the corresponding old tag
        returns a float between 0 to 1 as a result, where 1 is a perfect match.
    '''
    def _compare_words(word1, word2):
        c = 0.0     # initiated as float for the last division
        str1 = word1.replace(" ","").lower()    # ignore all spaces and case
        str2 = word2.replace(" ","").lower()    # ignore all spaces and case
        if len(str1) != len(str2): 
            # assign the longer string to str1
            str1, str2 = max([str1,str2],key=len), min([str1,str2], key=len)
        for i in range(len(str1)):
            if i < len(str2) and str1[i] == str2[i]:
                c += 1
            else:
                c += 0
        return c / len(str1)
    
    audio = AudioFile(filename)
    result = 0.0    # initiated as float for the last division
    for tag in TAGS_MAPS['mp3']:
        if audio.meta[audio.tag_map[tag]] and tags2compare[tag]:
            result += _compare_words(tags2compare[tag],audio.meta[audio.tag_map[tag]][0])  
        else:
            result += 0
    return result / len(TAGS_MAPS['mp3'])
    
    

def check_tags(filename):
    '''
        for testing. 
        should be removed when work on this module is done.
    '''
    audio = AudioFile(filename)
    audio.tag_print()
    
    test  ={'artist':'Cat Stevens','album':'Tea For The Tillerman','title':'Sad Lisa','track':'4','year':'1970','genre':'Folk Rock','albumartist':'Cat Stevens'}
    print compare_tags(filename, test)
    
    return audio.meta

if __name__ == '__main__':
    check_tags("sadlisa.mp3")
    
