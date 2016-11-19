# -*- coding: utf-8 -*-
import re
import os
import os.path
import scandir
from tagging import EasyTagger
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.modalview import ModalView
from kivy.uix.dropdown import DropDown
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel, TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Rectangle
from kivy.properties import StringProperty, BooleanProperty,ListProperty
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.garden.progressspinner import ProgressSpinner
from kivy.core.window import Window
from kivy.core.image import ImageData
from gui_classes import AnimatedBoxLayout, HoverBehavior,\
                         BorderLessNode, ToggleFlatButton,\
                        FlatButton
from kivy.garden.iconfonts import iconfonts

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

    def __init__(self):
        super(TagEditorLayout, self).__init__()
        self.input_list = [x for x in self.ids.keys() if "Input" in x]
        self.previous_input_dict = {re.sub("Input", "", key): "" for key in self.input_list}
        self.differentiated_input_dict = dict()
        self.current_tags = self.previous_input_dict

    def print_text_input(self):
        """
        Future 'Apply Changes' method for writing tags to the selected
        music file.

        Feature DOES NOT WORK PROPERLY!!!!
        """
        for input_text in self.input_list:
            self.current_tags[re.sub("Input", "", input_text)] = self.ids[input_text].text
        self.differentiated_input_dict = {key: self.current_tags[key] for key in
                                          self.current_tags if self.current_tags[key] !=
                                          self.previous_input_dict[key]}
        print self.differentiated_input_dict
        print self.previous_input_dict
        self.previous_input_dict = self.current_tags
        print self. current_tags

    def input_text_change(self, _, tree_node):
        if tree_node.node_type == "File":
            self.tagger = EasyTagger(tree_node.path)
            tags_dict = self.tagger.get_tags()
            self.previous_input_dict = tags_dict
            for input_text in self.input_list:
                self.ids[input_text].text = tags_dict[
                    re.sub("Input", "", input_text)]
                self.ids[input_text].cursor = (0, 0)    # Resets cursor position.
                self.ids[input_text].cursor = (len(self.ids[input_text].text), 0)


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
    shorten = BooleanProperty(True)
    color_selected = [.0, .0, .0, .07]
    even_color = [.5, .5, .5, 0]


class FolderNode(BoxLayout, BorderLessNode):
    file_icon = Image(source="icons\\grey_folder.png",
                      mipmap=True)
    path = StringProperty("")
    is_mapped = BooleanProperty(True)
    node_type = StringProperty("Folder")
    text = StringProperty("")
    shorten = BooleanProperty(True)
    color_selected = [.0, .0, .0, .07]
    even_color = [.2, .2, .2, 0]


class RootNode(Label, TreeViewNode):

    path = StringProperty("")
    is_mapped = BooleanProperty(False)
    node_type = StringProperty("Root")
    color_selected = [.0, .0, .0, .07]
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
                elif node.node_type == "Root":
                    self.dispatch("on_root_doubleclick", node)
                else:
                    self.dispatch("on_folder_doubleclick", node)
            else:
                self.select_node(node)
                node.dispatch('on_touch_down', touch)
        return True

    def select_node(self, node):
        if self.selected_node:
            self.deselected_node = self.selected_node
        else:
            self.deselected_node = None
        super(DynamicTree, self).select_node(node)
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
        if self.deselected_node:
            self.deselected_node.shorten = True
        node.shorten = False

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

    def populate_tree_view(self, path):
        pass

    def check_for_directory(self, node):
        pass

    def filter_dir_gen(self, path):
        pass

    def modify_list(self, input_node):
        """
        A 2 in 1 method, that allows do add\ remove nodes from the list widget.
        If input_node already exists in the list widget, it removes it.

        """
        if not input_node:
            return
        self.node_list = [sub_node for sub_node in self.iterate_all_nodes() if
                          not sub_node.text == "Root"]
        self.node_path_list = [n_path.path for n_path in self.node_list]
        if input_node.path not in self.node_path_list:
            self.add_node(FileNode(path=input_node.path,
                                    text=input_node.text,
                                   file_size=input_node.file_size))
        else:
            [self.remove_node(to_remove_node) for to_remove_node in
             self.node_list if to_remove_node.path == input_node.path]


class MetadorGui(App):

    def build(self):
        iconfonts.register('default_font', 'fontawesome-webfont.ttf',
                           'font-awesome.fontd')
        Window.bind(on_dropfile=self.drop_file_event_handler)
        Window.size = (1300, 850)
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        self.icon = "icons\\music_cover.png"
        self.modal_config()
        self.root_layout = RootLayout(orientation="vertical")
        self.upper_layout = AnimatedBoxLayout(orientation="horizontal",
                                              spacing=50, padding=[25, 0, 25, 0])
        self.editor_carousel = Carousel(scroll_timeout=-1, anim_move_duration=.3)
        self.bottom_layout = BottomLayout(orientation="vertical")
        self.center_layout = CenterLayout(orientation="vertical")
        self.app_menu_layout = AppMenuLayout()
        self.center_layout.add_widget(self.editor_carousel)
        self.metador_layout = MetadorLayout()
        self.converter_layout = ConverterLayout()
        self.tag_editor = TagEditorLayout()
        self.left_layout = LeftLayout()
        self.tree_view_config()
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
        # self.root_layout.add_widget(self.bottom_layout)

        return self.root_layout

    """WIDGETS CONFIG"""

    def tree_view_config(self):
        """Create and configure file explorer (Tree view)."""
        self.tree_view = DynamicTree(size_hint_y=None, hide_root=True,
                                     indent_level=12)
        self.tree_view.bind(on_select=self.tag_editor.input_text_change)
        self.tree_view.bind(minimum_height=self.tree_view.setter("height"))
        self.tree_view.bind(on_file_doubleclick=self.file_doubleclick_handler)
        self.tree_view.bind(on_folder_doubleclick=self.folder_doubleclick_handler)
        self.tree_view.bind(on_root_doubleclick=self.root_doubleclick_handler)
        self.tree_view.id = "tree_view_id"
        self.mapping_event("D:\The Music")

    def modal_config(self):
        """Create and configure all modal (Popup) widgets."""
        self.drag_modal = DragModal(pos_hint={"x": 0.05, "y": 0.45})
        self.drag_modal.children[0].text = "Drag Here Your Music Folder"
        self.converter_modal = DragModal(pos_hint={"x": 0.6, "y": 0.5})
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

    """File Explorer Event Handlers"""
    def folder_doubleclick_handler(self, tree_instance, node):
        self.mapping_event(node.path)

    def file_doubleclick_handler(self, tree_instnace, node):
        if self.editor_carousel.index == 1:
            self.converter_layout.ids.converter_list.modify_list(node)
        else:
            return

    def root_doubleclick_handler(self, tree_instance, node):
        parent_path = os.path.split(node.path)[0]
        self.mapping_event(parent_path)

    def change_editor_carousel(self, slide_num):

            self.editor_carousel.load_slide(self.editor_carousel.slides[slide_num])

    def tree_loading_start(self):
        self.app_menu_layout.ids.tree_progress.start_spinning()

    def tree_loading_stop(self):
        self.app_menu_layout.ids.tree_progress.stop_spinning()

if __name__ == '__main__':
    MetadorGui().run()
