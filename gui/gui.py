# -*- coding: utf-8 -*-
import re
import os
import os.path
import sys
import random
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from os.path import sep, expanduser, isdir, dirname
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout


class FileViewLabel(TreeViewLabel):

    path = StringProperty("")
    is_mapped = BooleanProperty(False)


class BottomLayout(FloatLayout):
    pass


class SelectTreeView(TreeView):

    __events__ = ('on_node_expand', 'on_node_collapse', 'on_select')

    def select_node(self, node):
        super(SelectTreeView, self).select_node(node)

        self.dispatch("on_select", node)

    def on_select(self, node):
        pass

    def populate_tree_view(self, path, upper=None):
        path = unicode(path)
        path_list = os.listdir(path)
        for some_dir in path_list:
            if os.path.isfile(os.path.join(path, some_dir)) is True:
                self.add_node(TreeViewLabel(text=unicode(some_dir)), upper)
            else:
                folder = TreeViewLabel(text=unicode(some_dir))
                self.add_node(folder, upper)
                self.populate_tree_view(os.path.join(path, some_dir), folder)


class AlternateTreeView(TreeView):

    __events__ = ('on_node_expand', 'on_node_collapse', 'on_select')

    def select_node(self, node):
        super(AlternateTreeView, self).select_node(node)

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
        for nod in node.nodes:
            sub_node_path = nod.path
            if os.path.isdir(sub_node_path):
                nod.is_mapped = True
                sub_dir = os.listdir(sub_node_path)
                for sub_dir_file in sub_dir:
                    self.add_node(FileViewLabel(path=os.path.join(
                        sub_node_path, sub_dir_file), text=sub_dir_file), nod)

    def populate_tree_view(self, path, upper=None):
        path = unicode(path)
        path_list = os.listdir(path)
        for some_dir in path_list:
            if os.path.isfile(os.path.join(path, some_dir)) is True:
                self.add_node(FileViewLabel(path=os.path.join(path, some_dir),
                                            text=unicode(some_dir)), upper)
            else:
                folder = FileViewLabel(path=os.path.join
                (path, some_dir), text=unicode(some_dir))
                self.add_node(folder, upper)
                # self.populate_tree_view(os.path.join(path, some_dir), folder)
                folder_listdir = os.listdir(os.path.join(path, some_dir))
                for sub_dir in folder_listdir:
                    self.add_node(FileViewLabel(path=os.path.join(path, some_dir, sub_dir), text=unicode(sub_dir)), folder)


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
        debug_dict = {"Artist": "{}".format(tree_node.text)}
        for input_text in self.input_list:
            self.ids[input_text].text = debug_dict[
                re.sub("Input", "", input_text)]


class MetadorGui(App):

    def build(self):
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        root_layout = BoxLayout(orientation="vertical")
        upper_layout = BoxLayout(orientation="horizontal")
        tag_editor = TagEditorLayout()
        tree_view = AlternateTreeView(size_hint_y=None)
        tree_view.bind(on_select=tag_editor.input_text_change)
        tree_view.bind(minimum_height=tree_view.setter("height"))
        tree_view.populate_tree_view(
            "D:\The Music")
        scroll_layout = ScrollView()
        scroll_layout.add_widget(tree_view)
        bottom_layout = BottomLayout()
        upper_layout.add_widget(scroll_layout)
        upper_layout.add_widget(tag_editor)
        root_layout.add_widget(upper_layout)
        root_layout.add_widget(bottom_layout)
        return root_layout


if __name__ == '__main__':
    MetadorGui().run()
