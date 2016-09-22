# -*- coding: utf-8 -*-
import re
from io import BytesIO
import os
import os.path
import threading
import scandir
import sys
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.listview import ListView,ListItemButton
from kivy.adapters.listadapter import ListAdapter
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.modalview import ModalView
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel, TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.graphics import Rectangle
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.garden.progressspinner import ProgressSpinner
from kivy.core.window import Window
from kivy.core.image import ImageData
from gui_classes import AnimatedBoxLayout
from meta_utils import time_decorator


class ConverterLayout(BoxLayout):
    pass



class EditorLabel(Label):
    """Label Class for editor text input headers."""


class TreeLoadingScreen(ModalView):
    """Tree Loading Screen."""


class FileLabel(Label):
    file_icon = Image(source="C:\Users\Master\Pictures\icons\music_icon_4.png",
                      mipmap=True)


class FolderLabel(Label):
    folder_icon = Image(source="C:\Users\Master\Pictures\icons\\folder.png",
                        mipmap=True)


class FileViewLabel(FileLabel, TreeViewNode):

    path = StringProperty("")
    is_mapped = BooleanProperty(True)
    node_type = StringProperty("File")


class FolderViewLabel(FolderLabel, TreeViewNode):

    path = StringProperty("")
    is_mapped = BooleanProperty(True)
    node_type = StringProperty("Folder")


class StandardViewLabel(TreeViewLabel):

    path = StringProperty("")
    is_mapped = BooleanProperty(False)
    node_type = StringProperty("Root")


class BottomLayout(FloatLayout):
    pass


class LeftLayout(BoxLayout):
    pass


class DragModal(ModalView):
    pass


class DynamicTree(TreeView):

    __events__ = ('on_node_expand', 'on_node_collapse', 'on_select',
                  'on_file_doubleclick')

    FILTER_RE = "(^[^.]*$)|(.*\.(flac|mp3|m4a|m4p|wma|aiff|wv|mpc))"
    FILE_EXT_RE = ".*\.(flac|mp3|m4a|m4p|wma|aiff|wv|mpc)$"

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
                    self.dispatch("on_file_doubleclick", node)
                else:
                    self.toggle_node(node)
            else:
                self.select_node(node)
                node.dispatch('on_touch_down', touch)
        return True

    def select_node(self, node):
        super(DynamicTree, self).select_node(node)
        self.dispatch("on_select", node)

    def on_node_expand(self, node):
        if node.is_mapped:
            return
        else:
            self.check_for_directory(node)

    def on_file_doubleclick(self, node):
        pass

    def on_select(self, node):
        pass

    def check_for_directory(self, node):
        node.is_mapped = True
        for sub_node in node.nodes:
            self.remove_node(sub_node)
        for sub_dir in self.filter_dir_gen(node.path):
            sub_dir_path = sub_dir.path
            if sub_dir.is_file():
                self.add_node(FileViewLabel(path=sub_dir_path,
                                            text=unicode(sub_dir.name)), node)
            else:
                sub_folder = FolderViewLabel(path=sub_dir.path, text=sub_dir.name)
                self.add_node(sub_folder, node)
                if self.empty_dir_check(sub_dir_path):
                    none_node = FileViewLabel(path="", text="")
                    sub_folder.is_mapped = False
                    self.add_node(none_node, sub_folder)

    def populate_tree_view(self, path):
        """Only triggered at file tree initialization."""
        yield
        path = unicode(path)
        self.root_node = StandardViewLabel(path=path, text=path, is_mapped=True)
        self.toggle_node(self.root_node)
        self.add_node(self.root_node)
        for some_dir in self.filter_dir_gen(path):
            some_dir_path = some_dir.path
            if some_dir.is_file():
                self.add_node(FileViewLabel(path=some_dir_path,
                                            text=unicode(some_dir.name)))
                yield
            else:
                folder = FolderViewLabel(path=some_dir_path, text=unicode(some_dir.name))
                self.add_node(folder, self.root_node)
                if self.empty_dir_check(some_dir_path):
                    none_node = FileViewLabel(path="", text="")
                    folder.is_mapped = False
                    self.add_node(none_node, folder)
                yield

    def empty_dir_check(self, directory):
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

        """
        for filter_sub_dir in scandir.scandir(path):
            if filter_sub_dir.is_dir() or re.match(self.FILE_EXT_RE,
                                                   filter_sub_dir.name):
                yield filter_sub_dir


class ConverterList(DynamicTree):

    def populate_tree_view(self, path):
        pass

    def check_for_directory(self, node):
        pass

    def filter_dir_gen(self, path):
        pass

    def add_to_list(self, root_tree, node):
        self.node_list = [sub_node.path for sub_node in self.iterate_all_nodes() if
                          not sub_node.text == "Root"]
        if node.path not in self.node_list:
            self.add_node(FileViewLabel(path=node.path,text=node.text))

    def remove_from_list(self,node):
        self.remove_node(node)


class TagEditorLayout(BoxLayout):
    """Layout for the all widgets related to the manual tag editor."""

    TAGS_DICT = {}

    def __init__(self):
        super(TagEditorLayout, self).__init__()
        self.input_list = [x for x in self.ids.keys() if "InputArtist" in x]
        self.previous_input_dict = {"InputArtist": ""}
        self.differentiated_input_dict = {}

    def print_text_input(self):
        for input_text in self.input_list:
            self.TAGS_DICT[input_text] = self.ids[input_text].text
        self.differentiated_input_dict = {key: self.TAGS_DICT[key] for key in
                                          self.TAGS_DICT if self.TAGS_DICT[key] !=
                                          self.previous_input_dict[key]}
        print self.differentiated_input_dict

    def input_text_change(self, tree, tree_node):
        self.ids["lbl_file"].text = tree_node.path
        debug_dict = {"Artist": "{}".format(tree_node.path)}
        self.previous_input_dict = {"InputArtist": "{}".format(tree_node.path)}
        for input_text in self.input_list:
            self.ids[input_text].text = debug_dict[
                re.sub("Input", "", input_text)]
            self.ids[input_text].cursor = (0, 0)
            self.ids[input_text].cursor = (len(self.ids[input_text].text), 0)


class MetadorGui(App):

    DIFF = int()

    def build(self):
        Window.bind(on_dropfile=self.drop_file_event)
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        self.tree_loading_screen = TreeLoadingScreen()
        self.root_layout = BoxLayout(orientation="vertical")
        self.upper_layout = AnimatedBoxLayout(orientation="horizontal")
        self.editor_carousel = Carousel()
        self.converter_layout = ConverterLayout()
        self.tag_editor = TagEditorLayout()
        self.left_layout = LeftLayout()
        self.tree_view = DynamicTree(size_hint_y=None, hide_root=True)
        self.tree_view.bind(on_select=self.tag_editor.input_text_change)
        self.tree_view.bind(minimum_height=self.tree_view.setter("height"))
        self.tree_view.bind(on_file_doubleclick=self.converter_layout.ids.converter_list.add_to_list)
        self.mapping_event("D:\The Music")
        self.tree_view.id = "tree_view_id"
        self.drag_modal = DragModal()
        self.scroll_layout = ScrollView()
        self.scroll_layout.scroll_distance = 30
        self.bottom_layout = BottomLayout()
        self.scroll_layout.add_widget(self.tree_view)
        self.tree_loading_stop()
        self.editor_carousel.add_widget(self.tag_editor)
        self.editor_carousel.add_widget(self.converter_layout)
        self.left_layout.add_widget(self.scroll_layout)
        self.upper_layout.add_widget(self.left_layout)
        self.upper_layout.add_widget(self.editor_carousel)
        self.root_layout.add_widget(self.upper_layout)
        self.root_layout.add_widget(self.bottom_layout)

        return self.root_layout

    def drop_file_event(self, window_instance, drop_file_string):

        if self.scroll_layout.collide_point(window_instance.mouse_pos[0],
                                        window_instance.mouse_pos[1])and \
                                        os.path.isdir(drop_file_string):
            self.drag_modal.dismiss()
            self.mapping_event(drop_file_string)

    def mapping_event(self, path_string):

        def mapping_callback(dt):
            try:
                self.tree_generator.next()
            except StopIteration:
                self.mapping_schedule.cancel()
                self.tree_loading_stop()

        self.tree_loading_start()
        self.tree_view.clear_tree_view()
        self.tree_generator = self.tree_view.populate_tree_view(path_string)
        self.mapping_schedule = Clock.schedule_interval(mapping_callback, 0)

    def tree_refresh(self):
        """Remaps the folder tree with the same root directory."""
        try:
            self.mapping_event(self.tree_view.root_node.path)
        except AttributeError:
            # In case there's no existing file tree.
            return

    def tree_loading_start(self):
        self.left_layout.ids.tree_progress.start_spinning()

    def tree_loading_stop(self):
        self.left_layout.ids.tree_progress.stop_spinning()




if __name__ == '__main__':
    MetadorGui().run()
