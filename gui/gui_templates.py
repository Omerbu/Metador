from kivy.config import Config
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.selectableview import SelectableView
from kivy.adapters.listadapter import ListAdapter
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from os.path import sep, expanduser, isdir, dirname
import sys
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

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
        if node.x - self.indent_start * 1.5 <= touch.x < node.x:
            self.toggle_node(node)
        elif node.x - self.indent_start <= touch.x:
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
                                                text=unicode(some_dir.name)))
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
