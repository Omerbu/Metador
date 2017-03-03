from kivy.uix.boxlayout import BoxLayout
from base_classes import AnimatedBoxLayout
from utils.tagging import EasyTagger
from kivy.uix.image import Image
import re
from utils import bio_retriever
from kivy.core.image import Image as CoreImage
from io import BytesIO
import Tkinter
import tkFileDialog


class RootLayout(BoxLayout):
    back_texture = Image(source=r"C:\Users\Dell\PycharmProjects\Metador"
                                r"\res\images\blur_blue.jpg",
                        mipmap=True)


class AppMenuLayout(BoxLayout):
    pass


class MetadorLayout(BoxLayout):
    pass


class ConverterLayout(BoxLayout):
    """Layout that hosts the file converter widgets"""


class BottomLayout(BoxLayout):
    pass


class LeftLayout(BoxLayout):
    pass


class CenterLayout(AnimatedBoxLayout):
    pass


class TagEditorLayout(BoxLayout):
    """
    Layout for the all widgets related to the manual tag editor.

    When pressing the 'Apply Changes' button, only the text inputs that were
    modified by the user are to be input-argument for tags-writing method.
    (Purpose of the Differentiated input dictionary)

    """

    MULTIPLE_TAGS_CONST = "*Multiple*"

    def __init__(self):
        super(TagEditorLayout, self).__init__()
        self.input_list = [x for x in self.ids.keys() if "Input" in x]
        self.previous_input_dict = {re.sub("Input", "", key): "" for key in self.input_list}
        self.differentiated_input_dict = dict()
        self.current_tags = dict()
        self.last_artist = str()
        self.last_album = str()
        self.tagger = None

    def check_for_tagger(func):
        def func_wrapper(*args, **kwargs):
            if args[0].tagger:
                results = func(*args, **kwargs)
                return results

        return func_wrapper

    def tags_input(self):
        """
        Future 'Apply Changes' method for writing tags to the selected
        music file.

        """
        for input_text in self.input_list:
            self.current_tags[re.sub("Input", "", input_text)] = self.ids[input_text].text
        self.differentiated_input_dict = {key: self.current_tags[key] for key in
                                          self.current_tags if self.current_tags[key] !=
                                          self.previous_input_dict[key]}
        self.differentiated_input_dict = {k: v for k, v in
              self.differentiated_input_dict.iteritems() if v != self.MULTIPLE_TAGS_CONST}
        self.previous_input_dict = {key: self.current_tags[key] for key in self.current_tags}
        return self.differentiated_input_dict

    def read_cover_art(self):
        coverart_string = self.tagger.get_cover()
        if coverart_string:
            coverart_string = BytesIO(coverart_string)
            core_image = CoreImage(coverart_string, ext="png",)
            self.ids["cover_art"].texture = core_image.texture
        else:
            self.ids["cover_art"].reload()

    def node_select_handler(self, tree_view, tree_node):

        if tree_view.is_multiple_selection:
            self.multiple_nodes_handler(tree_view.selected_nodes)
        elif tree_node.node_type == "File":
            self.tagger = EasyTagger(tree_node.path)
            tags_dict = self.tagger.get_tags()
            self.previous_input_dict = tags_dict
            self.change_text_boxes(tags_dict)
            if self.last_artist != self.tagger["Artist"]:
                bio_retriever.lastfm_bio_handler(self.tagger["Artist"],
                                                 self.artist_bio_handler)
            self.read_cover_art()
            self.last_artist = self.tagger["Artist"]

        else:
            for input_text in self.input_list:
                self.ids[input_text].text = str()
                self.ids[input_text].cursor = (0, 0)  # Resets cursor position.
                self.ids[input_text].cursor = (len(self.ids[input_text].text), 0)
                self.ids["cover_art"].reload()
                self.ids['lbl_file'].text = "Artist Biography"
                self.last_artist = self.last_album = self.tagger = None

    def multiple_nodes_handler(self, nodes_list):
        tag_dictionary_list = [EasyTagger(node.path).get_tags() for node
                               in nodes_list if node.node_type == "File"]
        if tag_dictionary_list:
            first_dictionary = tag_dictionary_list[0]
            combined_dictionary = {key: first_dictionary[key] if all(
                [comp_dict[key] == first_dictionary[key] for comp_dict
                    in tag_dictionary_list[1:]]) else
                    self.MULTIPLE_TAGS_CONST for key in first_dictionary}
            self.change_text_boxes(combined_dictionary)

            if not all(cmp_dict["Artist"] == first_dictionary["Artist"] for cmp_dict in
                    tag_dictionary_list[1:]):
                self.ids['lbl_file'].text = "Artist Biography"
            if not all(cmp_dict["Album"] == first_dictionary["Album"] for cmp_dict in
                       tag_dictionary_list[1:]):
                self.ids['cover_art'].reload()

    def change_text_boxes(self, tags_dict):
        for input_text in self.input_list:
            self.ids[input_text].text = tags_dict[
                re.sub("Input", "", input_text)]
            self.ids[input_text].cursor = (0, 0)  # Resets cursor position.
            self.ids[input_text].cursor = (len(self.ids[input_text].text), 0)

    def artist_bio_handler(self, results):

        self.ids['lbl_file'].text = results


    @check_for_tagger
    def remove_cover_art(self):
        self.tagger["coverart"] = str()
        self.read_cover_art()

    @check_for_tagger
    def add_cover_art(self):
        """ WIP! Design TBD"""
        Tkinter.Tk().withdraw()
        new_art_path = tkFileDialog.askopenfilename()
        if new_art_path:
            print new_art_path
            with open(new_art_path, 'rb') as cover_art_obj:
                image_string = cover_art_obj.read()
            self.tagger.set_cover(image_string)
            self.read_cover_art()