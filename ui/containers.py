import scandir
import re
from kivy.uix.treeview import TreeView
from kivy.properties import BooleanProperty, ListProperty, \
    ObjectProperty, NumericProperty
from kivy.clock import Clock
from nodes import FileNode, FolderNode, RootNode, ListNode
from utils.tagging import EasyTagger


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
        for node in self.selected_nodes:  # Clear all selected nodes.
            node.is_selected = False
            node.is_ms = False
            if not any([x.is_selected for x in node.parent_node.nodes]):
                node.parent_node.is_sub_nodes = False
        self.selected_nodes = list()
        self.is_multiple_selection = False

    def on_is_multiple_selection(self,_,ms_value):
        if ms_value:
            self.selected_nodes.append(self.selected_node)

        else:
            self.disable_multiple_selection()


    def ms_clock_on(self):
        self.ms_event = Clock.schedule_once(self.enable_multiple_selection, .6)

    def ms_clock_off(self):
        if self.ms_event:
            Clock.unschedule(self.ms_event)

    def clear_selection(self):
        if self.selected_node:
            self.selected_node.is_selected = False
        for node in self.selected_nodes:  # Clear all selected nodes.
            node.is_selected = False
            node.is_ms = False
        self.selected_nodes = list()
        self.is_multiple_selection = False

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
        self.ms_clock_on()

    def on_touch_up(self, touch):
        self.ms_clock_off()

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
        self.clear_selection()
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


class SelectedList(DynamicTree):

    list_counter = NumericProperty()

    def __init__(self, *args, **kwargs):
        super(SelectedList, self).__init__(*args, **kwargs)
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
        self.list_counter = 0

    def remove_from_list(self, input_node):
        if not input_node:
            return
        self.node_list = [sub_node for sub_node in self.iterate_all_nodes() if
                          not sub_node.text == "Root"]
        for to_remove_node in self.node_list:
            if to_remove_node.path == input_node.path:
                self.remove_node(to_remove_node)
                self.list_counter -= 1

    def add_to_list(self, node_list, done_callback):
        def mapping_callback(dt):
            try:
                self.add_generator.next()
            except StopIteration:
                self.adding_schedule.cancel()
                done_callback()

        self.add_generator = self.adding_generator(node_list)
        self.adding_schedule = Clock.schedule_interval(mapping_callback, 0)

    def adding_generator(self, input_list_node):
        if not input_list_node:
            return
        nodes_list = list()
        try:
            _ = iter(input_list_node)
            for node in input_list_node:
                yield
                if node.node_type == "Folder":
                    self.folder_building(node)
                    nodes_list += self.folder_reader(node)
                    yield
                else:
                    nodes_list.append(node)
        except TypeError:
            nodes_list.append(input_list_node)
        yield
        self.node_list = [sub_node for sub_node in self.iterate_all_nodes() if
                          not sub_node.text == "Root"]
        for node in nodes_list:
            yield
            self.node_path_list = [n_path.path for n_path in self.node_list]
            if node.path not in self.node_path_list:
                input_node_duration = EasyTagger(node.path).get_duration()
                self.add_node(ListNode(path=node.path,
                                       text=node.text,
                                       file_size=node.file_size,
                                       file_duration=input_node_duration))
                yield
                self.list_counter += 1

    def folder_building(self, folder_node):

        if not folder_node.is_mapped:
            self.explorer_instance.check_for_directory(folder_node)
        for folder_sub_node in [node for node in folder_node.nodes
                                 if node.node_type == "Folder"]:
            self.folder_building(folder_sub_node)

    def folder_reader(self, folder_node):
        return [node for node in
                self.explorer_instance.iterate_all_nodes(folder_node)
                if node.node_type == "File"]

    def multiple_remove_from_list(self, node_list):
        for node in node_list:
            self.remove_from_list(node)