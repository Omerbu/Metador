# -*- coding: utf-8 -*-
import re
import os
import os.path
import threading
from functools import partial
import scandir
import sys
import time
import random
from kivy.uix.progressbar import ProgressBar
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
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from garden.progressspinner import ProgressSpinner
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from meta_utils import time_decorator


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
    is_mapped = BooleanProperty(False)


class FolderViewLabel(FolderLabel, TreeViewNode):

    path = StringProperty("")
    is_mapped = BooleanProperty(False)


class StandardViewLabel(TreeViewLabel):

    path = StringProperty("")
    is_mapped = BooleanProperty(False)


class BottomLayout(FloatLayout):
    pass


class LeftLayout(BoxLayout):
    pass


class DragModal(ModalView):
    pass


class GeneratorTreeView(TreeView):
    """ NOT CURRENTLY USED!"""
    REC_COUNTER = 0

    __events__ = ('on_node_expand', 'on_node_collapse', 'on_select')

    FILTER_PATTERN = ".*\.(flac|mp3|m4a|m4p|wma|aiff|wv|mpc)"

    def select_node(self, node):
        super(GeneratorTreeView, self).select_node(node)

        self.dispatch("on_select", node)

    def on_select(self, node):
        pass

    def populate_tree_view(self, path, upper=None):
        if upper is None:
            self.root_options = {"text": path}
        path = unicode(path)
        for some_dir in scandir.scandir(path):
            some_dir_path = some_dir.path
            if some_dir.is_file():
                if re.match(self.FILTER_PATTERN, some_dir.name):
                    file_node = FileViewLabel()
                    file_node.path = some_dir_path
                    file_node.text = some_dir.name
                    self.add_node(file_node, upper)
            else:
                folder = FolderViewLabel(path=some_dir_path, text=unicode(some_dir.name))
                self.add_node(folder, upper)
                inner_generator = self.populate_tree_view(some_dir_path, folder)
                yield
                for x in inner_generator:
                    yield

    def clear_tree_view(self):
        node_list = [node for node in self.iterate_all_nodes()]
        for node in node_list:
            self.remove_node(node)


class DynamicTreeView(TreeView):
    """2-stepped dynamic tree widget."""

    __events__ = ('on_node_expand', 'on_node_collapse', 'on_select')

    FILTER_RE = "(^[^.]*$)|(.*\.(flac|mp3|m4a|m4p|wma|aiff|wv|mpc))"

    def on_touch_down(self, touch):
        node = self.get_node_at_pos(touch.pos)
        if not node:
            return
        if node.disabled:
            return
        # toggle node or selection ?
        if node.x - self.indent_start <= touch.x < node.x:
            self.toggle_node(node)
        elif node.x <= touch.x:
            if touch.is_double_tap:
                self.toggle_node(node)
            else:
                self.select_node(node)
                node.dispatch('on_touch_down', touch)
        return True

    def select_node(self, node):
        super(DynamicTreeView, self).select_node(node)

        self.dispatch("on_select", node)

    def on_node_expand(self, node):
        if node.is_mapped:
            return
        else:
            self.check_for_directory(node)

    def on_select(self, node):
        pass

    def check_for_directory(self, node):
        node.is_mapped = True
        for sub_node in node.nodes:
            sub_node_path = sub_node.path
            if type(sub_node).__name__ == "FolderViewLabel":
                for sub_node_sub_dir in self.filter_dir_gen(sub_node_path):
                    if sub_node_sub_dir.is_file():
                            self.add_node(FileViewLabel(
                                path=sub_node_sub_dir.path,
                                text=unicode(sub_node_sub_dir.name)), sub_node)
                    else:
                        self.add_node(FolderViewLabel(
                            path=sub_node_sub_dir.path,
                            text=unicode(sub_node_sub_dir.name)), sub_node)

    def populate_tree_view(self, path):
        """Only triggered at file tree initialization."""
        yield
        path = unicode(path)
        self.root_node = StandardViewLabel(path=path, text=path)
        self.toggle_node(self.root_node)
        self.add_node(self.root_node)
        for some_dir in self.filter_dir_gen(path):
            some_dir_path = some_dir.path
            if some_dir.is_file():
                    self.add_node(FileViewLabel(path=some_dir_path,
                                                text=unicode(some_dir.name)),
                                                self.root_node)
                    yield
            else:
                folder = FolderViewLabel(path=some_dir_path, text=unicode(some_dir.name))
                self.add_node(folder, self.root_node)
                for sub_dir in self.filter_dir_gen(some_dir_path):
                    if sub_dir.is_file():
                            self.add_node(FileViewLabel(path=sub_dir.path,
                                                        text=unicode(sub_dir.name)),
                                                        folder)
                            yield
                    else:
                        self.add_node(FolderViewLabel(path=sub_dir.path,
                                                    text=unicode(sub_dir.name)), folder)
                        yield

    def clear_tree_view(self):
        node_list = [node for node in self.iterate_all_nodes()]
        for node in node_list:
            self.remove_node(node)

    def filter_dir_gen(self, path):
        for filter_sub_dir in scandir.scandir(path):
            if re.match(self.FILTER_RE, filter_sub_dir.name):
                yield filter_sub_dir


class TagEditorLayout(BoxLayout):

    TAGS_DICT = {}

    def __init__(self):
        super(TagEditorLayout, self).__init__()
        self.input_list = [x for x in self.ids.keys() if "InputArtist" in x]

    def print_text_input(self):

        for input_text in self.input_list:
            self.TAGS_DICT[input_text] = self.ids[input_text].text
        print self.TAGS_DICT

    def input_text_change(self, tree, tree_node):
        self.ids["lbl_file"].text = tree_node.path
        debug_dict = {"Artist": "{}".format(tree_node.path)}
        for input_text in self.input_list:
            self.ids[input_text].text = debug_dict[
                re.sub("Input", "", input_text)]


class MetadorGui(App):

    DIFF = int()

    def build(self):
        Window.bind(on_dropfile=self.drop_file_event)
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        self.tree_loading_screen = TreeLoadingScreen()
        self.root_layout = BoxLayout(orientation="vertical")
        self.upper_layout = BoxLayout(orientation="horizontal")
        self.tag_editor = TagEditorLayout()
        self.left_layout = LeftLayout()
        self.tree_view = DynamicTreeView(size_hint_y=None, hide_root=True)
        self.tree_view.bind(on_select=self.tag_editor.input_text_change)
        self.tree_view.bind(minimum_height=self.tree_view.setter("height"))
        self.tree_view.id = "tree_view_id"
        self.drag_modal = DragModal()
        self.scroll_layout = ScrollView()
        self.bottom_layout = BottomLayout()
        self.scroll_layout.add_widget(self.tree_view)
        self.tree_loading_stop()
        self.left_layout.add_widget(self.scroll_layout)
        self.upper_layout.add_widget(self.left_layout)
        self.upper_layout.add_widget(self.tag_editor)
        self.root_layout.add_widget(self.upper_layout)
        self.root_layout.add_widget(self.bottom_layout)


        return self.root_layout

    def drop_file_event(self, window_instance, drop_file_string):

        def drop_file_callback(clocktime):
            self.tree_view.clear_tree_view()
            self.tree_view.populate_tree_view(drop_file_string)
            self.tree_loading_screen.dismiss()

        if self.scroll_layout.collide_point(window_instance.mouse_pos[0],
                                        window_instance.mouse_pos[1]):
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
        # Clock.schedule_once(drop_file_callback, 0)

    def tree_refresh(self):
        try:
            self.mapping_event(self.tree_view.root_node.path)
        except AttributeError:
            return

    def tree_loading_start(self):
        self.left_layout.ids.tree_progress.start_spinning()

    def tree_loading_stop(self):
        self.left_layout.ids.tree_progress.stop_spinning()


if __name__ == '__main__':
    MetadorGui().run()
