# -*- coding: utf-8 -*-
import re
import os
import os.path
import scandir
from tagging import EasyTagger
from kivy.core.window import Window
from kivy.core.image import ImageData
from kivy.clock import Clock
from kivy.config import Config
from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.carousel import Carousel
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel, TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty, BooleanProperty, ListProperty, \
                            ObjectProperty, NumericProperty
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from gui_classes import AnimatedBoxLayout, BorderLessNode,\
                        ToggleFlatButton, FlatButton
import meta_bio_retriever
import iconfonts
from progressspiner import ProgressSpinner
from meta_utils import time_decorator
from kivy.network.urlrequest import UrlRequest

"""Config """
Config.set('kivy', 'desktop', '1')


"""EXPERIMENTAL WIDGETS:"""


"""Layouts:"""


class RootLayout(BoxLayout):
    back_texture = Image(source="icons\\blur_blue.jpg",
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

    def node_select_handler(self, tree_view, tree_node):

        if tree_view.is_multiple_selection:
            self.multiple_nodes_handler(tree_view.selected_nodes)
        elif tree_node.node_type == "File":
            self.tagger = EasyTagger(tree_node.path)
            tags_dict = self.tagger.get_tags()
            self.previous_input_dict = tags_dict
            self.change_text_boxes(tags_dict)
           #  _ = meta_bio_retriever.BioRetriever().lastfm_bio_handler(tags_dict["Artist"],
                                                    # self.artist_bio_handler())
        else:
            for input_text in self.input_list:
                self.ids[input_text].text = str()
                self.ids[input_text].cursor = (0, 0)  # Resets cursor position.
                self.ids[input_text].cursor = (len(self.ids[input_text].text), 0)

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

    def change_text_boxes(self, tags_dict):
        for input_text in self.input_list:
            self.ids[input_text].text = tags_dict[
                re.sub("Input", "", input_text)]
            self.ids[input_text].cursor = (0, 0)  # Resets cursor position.
            self.ids[input_text].cursor = (len(self.ids[input_text].text), 0)

    def artist_bio_handler(self, results):

        self.ids['lbl_file'].text = results
        # if bio:
        #     self.ids['lbl_file'].text = bio
        # else:
        #     self.ids['lbl_file'].text = "No Artist Biography Found "


"""Labels and Buttons:"""


class AlbumLabel(Label):
        icon_src = Image(source="icons\\cd.png",
                         mipmap=True)


class GenreLabel(Label):
        icon_src = Image(source="icons\\electric_guitar.png",
                         mipmap=True)


class EditorLabel(Label):
    """Label Class for editor text input icons."""


class EditorTextInput(TextInput):

    underline_color = ListProperty([1, 1, 1, .4])

    def on_focus(self, _, enter_focus):
        if enter_focus:
            self.underline_color = [0, 1, 1, 1]
        else:
            self.underline_color = [1, 1, 1, .4]


class FileNode(BoxLayout, BorderLessNode):
    file_icon = Image(source="icons\\file_icon_white.png",
                      mipmap=True)
    file_size = StringProperty("")
    path = StringProperty("")
    is_mapped = BooleanProperty(True)
    node_type = StringProperty("File")
    text = StringProperty("")
    color_selected_ms = [0, .8, .9, .2]
    is_ms = BooleanProperty(False)
    color_selected = [.0, .0, .0, .03]
    even_color = [.5, .5, .5, 0]


class ConverterNode(FileNode):
    file_type = StringProperty("")
    file_duration = StringProperty("")
    no_selection = True


class FolderNode(BoxLayout, BorderLessNode):
    file_icon = Image(source="icons\\grey_folder.png",
                      mipmap=True)
    path = StringProperty("")
    is_mapped = BooleanProperty(True)
    is_sub_nodes = BooleanProperty(False)
    node_type = StringProperty("Folder")
    text = StringProperty("")
    color_selected = [.0, .0, .0, .03]
    color_selected_ms = [0, .8, .9, .2]
    folder_color_sub_nodes = [0, 1, 1, 1]
    folder_icon_color = [.6, .75, .8, 0.5]
    is_sub_nodes = BooleanProperty(False)
    is_ms = BooleanProperty(False)
    even_color = [.2, .2, .2, 0]


class RootNode(Label, TreeViewNode):

    path = StringProperty("")
    is_mapped = BooleanProperty(False)
    node_type = StringProperty("Root")
    color_selected = [.0, .0, .0, .03]
    color_selected_ms = [0, .8, .9, .2]
    is_ms = BooleanProperty(False)
    no_selection = True


class CoverArtImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(CoverArtImage, self).__init__(**kwargs)
        self.source = "icons\\cover_art.jpg"
        self.mipmap = False

"""APP MENU ELEMENTS:"""


"""COMPLEX GUI OBJECTS:"""


class BaseModal(ModalView):

    is_open = BooleanProperty(False)

    def on_open(self):
        self.is_open = True

    def on_dismiss(self):
        self.is_open = False


class DragModal(BaseModal):
    pass


class AboutModal(BaseModal):
    pass


class DynamicTree(TreeView):

    __events__ = ('on_node_expand', 'on_node_collapse', 'on_select',
                  'on_file_doubleclick', 'on_folder_doubleclick',
                  'on_root_doubleclick')

    FILE_FILTER = ".*\.(flac|mp3|m4a|m4p|wma|aiff|wv|mpc)$"
    MB_CONST = float(1048576)
    is_multiple_selection = BooleanProperty(False)
    selected_nodes = ListProperty(list())

    def __init__(self, *args, **kwargs):
        super(DynamicTree, self).__init__(*args, **kwargs)
        self.ms_event = None

    def on_touch_down(self, touch):
        node = self.get_node_at_pos(touch.pos)
        if not node:
            return
        if node.disabled:
            return
        # toggle node or selection ?
        if node.x - self.indent_start * 1.5 <= touch.x < node.x:
            self.toggle_node(node)
        elif node.x - self.indent_start <= touch.x:
            if touch.is_double_tap:
                if node.node_type == "File":
                    if self.is_multiple_selection:
                        return
                    else:
                        self.dispatch("on_file_doubleclick", node)
                elif node.node_type == "Root":
                    self.dispatch("on_root_doubleclick", node)
                else:
                    self.dispatch("on_folder_doubleclick", node)
            else:
                self.select_node(node)
        node.dispatch('on_touch_down', touch)
        return True

    def enable_multiple_selection(self, _):
        self.selected_node.is_ms = True
        self.is_multiple_selection = True
        self.selected_node.parent_node.is_sub_nodes = True

    def disable_multiple_selection(self):
        self.selected_node.is_ms = False
        for node in self.selected_nodes:  # Clear all selected nodes.
            node.is_selected = False
            node.is_ms = False
            if not any([x.is_selected for x in node.parent_node.nodes]):
                node.parent_node.is_sub_nodes = False
        self.selected_nodes = list()
        self.is_multiple_selection = False

    def ms_clock_on(self, _, touch,):
        self.ms_event = Clock.schedule_once(self.enable_multiple_selection, .6)

    def ms_clock_off(self, _, touch,):
        if self.ms_event:
            Clock.unschedule(self.ms_event)

    def select_node(self, node):
        if self.selected_node:
            self.deselected_node = self.selected_node
        else:
            self.deselected_node = None
        if node.no_selection:
            return
        if self.is_multiple_selection:
            if node in self.selected_nodes:
                node.is_ms = False
                node.is_selected = False
                if not any([x.is_selected for x in node.parent_node.nodes]):
                    node.parent_node.is_sub_nodes = False
                self.selected_nodes.remove(node)
                if not self.selected_nodes:
                    self.disable_multiple_selection()
            else:
                node.is_ms = True
                node.is_selected = True
                node.parent_node.is_sub_nodes = True
                self.selected_nodes.append(node)
        else:
            if self._selected_node:
                self._selected_node.is_selected = False
            node.is_selected = True
            self._selected_node = node
        self.dispatch("on_select", node)

    def on_node_expand(self, node):
        if node.is_mapped:
            return
        else:
            self.check_for_directory(node)

    def on_root_doubleclick(self, node):
        pass

    def on_file_doubleclick(self, node):
        pass

    def on_folder_doubleclick(self, node):
        pass

    def on_select(self, node):
        pass

    def check_for_directory(self, node):
        """Read the contents of the folder represented by 'node' argument."""
        node.is_mapped = True
        for sub_node in node.nodes:
            self.remove_node(sub_node)
        for sub_dir in self.filter_dir_gen(node.path):
            sub_dir_path = sub_dir.path
            if sub_dir.is_file():
                sub_dir_size = str(round(sub_dir.stat()[6] / self.MB_CONST, 1))
                self.add_node(FileNode(path=sub_dir_path,
                                       text=unicode(sub_dir.name),
                                       file_size=sub_dir_size), node)
            else:
                sub_folder = FolderNode(path=sub_dir.path, text=sub_dir.name)
                self.add_node(sub_folder, node)
                if self.empty_dir_check(sub_dir_path):
                    none_node = RootNode(path="", text="")
                    sub_folder.is_mapped = False
                    self.add_node(none_node, sub_folder)

    def populate_tree_view(self, path):
        """Only triggered at file tree initialization."""
        self.selected_nodes = list()
        path = unicode(path)
        self.root_node = RootNode(path=path, text=path, is_mapped=True)
        self.toggle_node(self.root_node)
        self.add_node(self.root_node)
        for some_dir in self.filter_dir_gen(path):
            some_dir_path = some_dir.path
            if some_dir.is_file():
                some_dir_size = str(round(some_dir.stat()[6] / self.MB_CONST, 1))
                self.add_node(FileNode(path=some_dir_path,
                                       text=unicode(some_dir.name),
                                       file_size=some_dir_size))
                yield
            else:
                folder = FolderNode(path=some_dir_path, text=unicode(some_dir.name))
                self.add_node(folder, self.root_node)
                if self.empty_dir_check(some_dir_path):
                    none_node = RootNode(path="", text="")
                    folder.is_mapped = False
                    self.add_node(none_node, folder)
                yield

    def empty_dir_check(self, directory):
        """Checks if the argument 'directory' is empty"""
        dir_generator = self.filter_dir_gen(directory)
        try:
            dir_generator.next()
        except StopIteration:
            return None
        return True

    def clear_tree_view(self):
        """Remove all tree items."""
        for node in [node for node in self.iterate_all_nodes()]:
            self.remove_node(node)

    def filter_dir_gen(self, path):
        """
        Wrapper for 'scandir' that returns only folders and
        compatible music files.
        Handles OSE exceptions caused by strict-access folders.

        """
        try:
            for filter_sub_dir in scandir.scandir(path):
                if filter_sub_dir.is_dir() or re.match(self.FILE_FILTER,
                                                       filter_sub_dir.name):
                    yield filter_sub_dir
        except OSError:
            yield


class ConverterList(DynamicTree):

    def __init__(self, *args, **kwargs):
        super(ConverterList, self).__init__(*args, **kwargs)
        self.explorer_instance = ObjectProperty()

    def populate_tree_view(self, path):
        pass

    def check_for_directory(self, node):
        pass

    def filter_dir_gen(self, path):
        pass

    def clear_tree_view(self):
        self.multiple_remove_from_list([node for node in self.iterate_all_nodes()
                                        if not node.text == "Root"])

    def remove_from_list(self, input_node):
        if not input_node:
            return
        self.node_list = [sub_node for sub_node in self.iterate_all_nodes() if
                          not sub_node.text == "Root"]
        [self.remove_node(to_remove_node) for to_remove_node in
            self.node_list if to_remove_node.path == input_node.path]

    def add_to_list(self, input_node):
        if not input_node:
            return
        if input_node.node_type == "Folder":
            self.add_folder_content(input_node)
        else:
            self.node_list = [sub_node for sub_node in self.iterate_all_nodes() if
                              not sub_node.text == "Root"]
            self.node_path_list = [n_path.path for n_path in self.node_list]
            if input_node.path not in self.node_path_list:
                input_node_duration = EasyTagger(input_node.path).get_duration()
                self.add_node(ConverterNode(path=input_node.path,
                                       text=input_node.text,
                                       file_size=input_node.file_size,
                                       file_duration=input_node_duration))

    def multiple_add_to_list(self, node_list):
        for node in node_list:
            print node.node_type
            self.add_to_list(node)

    def multiple_remove_from_list(self, node_list):
        for node in node_list:
            self.remove_from_list(node)

    def add_folder_content(self, folder_node):
        self.multiple_add_to_list(folder_node.nodes)






class MetadorGui(App):

    def build(self):
        iconfonts.register('default_font', 'fontawesome-webfont.ttf',
                           'font-awesome.fontd')
        Window.bind(on_dropfile=self.drop_file_event_handler)
        Window.size = (1350, 850)
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        self.icon = "icons\\music_cover.png"
        self.app_menu_layout = AppMenuLayout()
        self.modal_config()
        self.root_layout = RootLayout(orientation="vertical")
        self.upper_layout = AnimatedBoxLayout(orientation="horizontal",
                                              spacing=50, padding=[25, 0, 25, 0])
        self.editor_carousel = Carousel(scroll_timeout=-1, anim_move_duration=.4)
        self.center_layout = CenterLayout(orientation="vertical")
        self.center_layout.add_widget(self.editor_carousel)
        self.metador_layout = MetadorLayout()
        self.tag_editor = TagEditorLayout()
        self.left_layout = LeftLayout()
        self.tree_view_config()
        self.converter_layout = ConverterLayout()
        self.scroll_layout = ScrollView(bar_color=[.4, .6, .65, .35])
        self.scroll_layout.scroll_distance = 50
        self.scroll_layout.add_widget(self.tree_view)
        self.editor_carousel.add_widget(self.metador_layout)
        self.editor_carousel.add_widget(self.converter_layout)
        self.left_layout.add_widget(self.scroll_layout)
        self.upper_layout.add_widget(self.left_layout)
        self.upper_layout.add_widget(self.center_layout)
        self.upper_layout.add_widget(self.tag_editor)
        self.root_layout.add_widget(self.app_menu_layout)
        self.root_layout.add_widget(self.upper_layout)

        return self.root_layout

    """WIDGETS CONFIG"""

    def tree_view_config(self):
        """Create and configure file explorer (Tree view)."""
        self.tree_view = DynamicTree(size_hint_y=None, hide_root=True,
                                     indent_level=12)
        self.tree_view.bind(on_select=self.tree_view.ms_clock_on)
        self.tree_view.bind(on_touch_up=self.tree_view.ms_clock_off)
        self.tree_view.bind(is_multiple_selection=self.multiple_selection_handler)
        self.tree_view.bind(on_select=self.tag_editor.node_select_handler)
        self.tree_view.bind(minimum_height=self.tree_view.setter("height"))
        self.tree_view.bind(on_file_doubleclick=self.file_doubleclick_handler)
        self.tree_view.bind(on_folder_doubleclick=self.folder_doubleclick_handler)
        self.tree_view.bind(on_root_doubleclick=self.root_doubleclick_handler)
        self.tree_view.id = "tree_view_id"
        self.mapping_event("D:\The Music")
        self.left_layout.ids.filter_carousel.index = 1

    def modal_config(self):
        """Create and configure all modal (Popup) widgets."""
        self.drag_modal = DragModal(pos_hint={"x": 0, "y": 0.5})
        self.drag_modal.children[0].text = "Drag Here Your Music Folder"
        self.converter_modal = DragModal(pos_hint={"x": 0.36, "y": 0.5})
        self.converter_modal.children[0].text = "Drag Here Your Destination Folder"
        self.about_modal = AboutModal()

    """APP EVENTS"""

    def drop_file_event_handler(self, window_instance, drop_file_string):

        if self.scroll_layout.collide_point(window_instance.mouse_pos[0],
                                        window_instance.mouse_pos[1]):
            self.drag_modal.dismiss()
            self.mapping_event(drop_file_string)
        elif self.editor_carousel.collide_point(window_instance.mouse_pos[0],
                                         window_instance.mouse_pos[1]) and \
                                        self.editor_carousel.index == 2 and \
                                        self.converter_modal.is_open:

            self.converter_layout.ids.converter_text_input.text = drop_file_string
            self.converter_modal.dismiss()

    @staticmethod
    def change_carousel(carousel, slide_num):
        carousel.load_slide(carousel.slides[slide_num])

    def write_tags(self):
        input_tags = self.tag_editor.tags_input()
        if not input_tags:
            return
        if self.tree_view.is_multiple_selection:
            for node in self.tree_view.selected_nodes:
                EasyTagger(node.path).set_tags(input_tags)
        else:
            EasyTagger(self.tree_view.selected_node.path).set_tags(input_tags)

    """File Explorer Event Handlers"""

    def mapping_event(self, path_string):

        def mapping_callback(dt):
            try:
                self.tree_generator.next()
            except StopIteration:
                self.mapping_schedule.cancel()
                self.tree_loading_stop()

        if not os.path.isdir(path_string):
            return
        self.tree_loading_start()
        self.tree_view.clear_tree_view()
        self.tree_generator = self.tree_view.populate_tree_view(path_string)
        self.mapping_schedule = Clock.schedule_interval(mapping_callback, 0)

    def tree_refresh(self,):
        """Remaps the folder tree with the same root directory."""
        try:
            self.mapping_event(self.tree_view.root_node.path)
        except AttributeError:
            # In case there's no existing file tree.
            return

    def multiple_selection_handler(self, _, ms_value):
        filter_carousel = self.left_layout.ids.filter_carousel
        if ms_value:
            self.change_carousel(filter_carousel, 0)
            self.tree_view.selected_nodes.append(self.tree_view.selected_node)

        else:
            self.change_carousel(filter_carousel, 1)
            self.tree_view.disable_multiple_selection()

    def folder_doubleclick_handler(self, _, node):
        self.mapping_event(node.path)

    def file_doubleclick_handler(self, _, node):
        if self.editor_carousel.index == 1:
            self.converter_layout.ids.converter_list.add_to_list(node)
        else:
            return

    def root_doubleclick_handler(self, _, node):
        parent_path = os.path.split(node.path)[0]
        self.mapping_event(parent_path)

    def files_filter_handler(self):
        filter_chs = [self.left_layout.ids[widget].ext for widget in
                      self.left_layout.ids if "_ch" in widget and
                      self.left_layout.ids[widget].active]
        filter_chs = "|".join(filter_chs)
        self.tree_view.FILE_FILTER = ".*\.({0})$".format(filter_chs)
        self.tree_refresh()

    def tree_loading_start(self):
        self.app_menu_layout.ids.tree_progress.start_spinning()

    def tree_loading_stop(self):
        Clock.schedule_once(self.app_menu_layout.ids.tree_progress.stop_spinning,1)

if __name__ == '__main__':
    MetadorGui().run()
