# -*- coding: utf-8 -*-
import os
import os.path
import Tkinter
import tkFileDialog
from io import BytesIO
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.config import Config
from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.carousel import Carousel
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty, BooleanProperty, ListProperty, \
                            ObjectProperty, NumericProperty
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from gui_classes import AnimatedBoxLayout,\
                        ToggleFlatButton, FlatButton, CoverArtImage
from progressspiner import ProgressSpinner
from layouts import *
from containers import *
from nodes import *


"""Config """
Config.set('kivy', 'desktop', '1')


"""EXPERIMENTAL WIDGETS:"""


"""Layouts:"""





"""Labels and Buttons:"""

class AlbumLabel(Label):
        icon_src = Image(source=r"res\icons\cd.png",
                         mipmap=True)


class GenreLabel(Label):
        icon_src = Image(source=r"res\icons\electric_guitar.png",
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

"""Nodes"""





"""APP MENU ELEMENTS:"""


"""COMPLEX GUI OBJECTS:"""


class BaseModal(ModalView):

    is_open = BooleanProperty(False)

    def on_open(self):
        self.is_open = True

    def on_dismiss(self):
        self.is_open = False


class AboutModal(BaseModal):
    pass


class SettingsModal(BaseModal):
    pass




class MetadorGui(App):

    def build(self):
        Window.bind(on_dropfile=self.drop_file_event_handler)
        Window.size = (1350, 850)
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        self.icon = r"res\icons\music_cover.png"
        self.app_menu_layout = AppMenuLayout()
        self.root_layout = RootLayout(orientation="vertical")
        self.upper_layout = AnimatedBoxLayout(orientation="horizontal",
                                              spacing=50, padding=[25, 0, 25, 0])
        self.center_carousel = Carousel(scroll_timeout=-1, anim_move_duration=.3)
        self.center_layout = CenterLayout(orientation="vertical")
        self.center_layout.add_widget(self.center_carousel)
        self.tag_editor = TagEditorLayout()
        self.left_layout = LeftLayout()
        self.tree_view_config()
        self.modal_config()
        self.converter_layout = ConverterLayout()
        self.metador_layout = MetadorLayout()
        self.lists_config()
        self.scroll_layout = ScrollView(bar_color=[.4, .6, .65, .35])
        self.scroll_layout.scroll_distance = 50
        self.scroll_layout.add_widget(self.tree_view)
        self.center_carousel.add_widget(self.metador_layout)
        self.center_carousel.add_widget(self.converter_layout)
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
        self.tree_view.bind(is_multiple_selection=self.multiple_selection_handler)
        self.tree_view.bind(on_select=self.clear_selection_handler)
        self.tree_view.bind(on_select=self.tag_editor.node_select_handler)
        self.tree_view.bind(minimum_height=self.tree_view.setter("height"))
        self.tree_view.bind(on_file_doubleclick=self.selected_list_node_add_handler)
        self.tree_view.bind(on_folder_doubleclick=self.folder_doubleclick_handler)
        self.tree_view.bind(on_root_doubleclick=self.root_doubleclick_handler)
        self.tree_view.id = "tree_view_id"
        self.mapping_event("D:\The Music")
        self.left_layout.ids.filter_carousel.index = 1

    def lists_config(self):
        self.converter_layout.ids.converter_list.bind(
            on_select=self.clear_selection_handler)
        self.metador_layout.ids.metador_list.bind(
            on_select=self.clear_selection_handler)
        self.converter_layout.ids.converter_list.bind(
            on_select=self.tag_editor.node_select_handler)
        self.metador_layout.ids.metador_list.bind(
            on_select=self.tag_editor.node_select_handler)

    def modal_config(self):
        """Create and configure all modal (Popup) widgets."""
        self.about_modal = AboutModal()
        self.settings_modal = SettingsModal()

    """APP EVENTS"""

    def drop_file_event_handler(self, window_instance, drop_file_string):

        if self.scroll_layout.collide_point(window_instance.mouse_pos[0],
                                        window_instance.mouse_pos[1]):
            self.mapping_event(drop_file_string)

    def change_explorer(self):
        Tkinter.Tk().withdraw()
        new_explorer_path = tkFileDialog.askdirectory()
        self.mapping_event(new_explorer_path)

    def change_dest_folder(self):
        Tkinter.Tk().withdraw()
        new_dest_path = tkFileDialog.askdirectory()
        self.converter_layout.ids.converter_text_input.text = new_dest_path

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

    def tree_refresh(self):
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
        else:
            self.change_carousel(filter_carousel, 1)

    def folder_doubleclick_handler(self, _, node):
        self.mapping_event(node.path)

    def root_doubleclick_handler(self, _, node):
        parent_path = os.path.split(node.path)[0]
        self.mapping_event(parent_path)

    def selected_list_node_add_handler(self, _, node):
        if self.center_carousel.index == 1:
            self.converter_layout.ids.converter_list.add_to_list(node)
        else:
            self.metador_layout.ids.metador_list.add_to_list(node)

    def files_filter_handler(self):
        filter_chs = [self.left_layout.ids[widget].ext for widget in
                      self.left_layout.ids if "_ch" in widget and
                      self.left_layout.ids[widget].active]
        filter_chs = "|".join(filter_chs)
        self.tree_view.FILE_FILTER = ".*\.({0})$".format(filter_chs)
        self.tree_refresh()

    def clear_selection_handler(self, selected_node_widget, _):
        node_widgets = [self.converter_layout.ids.converter_list,
                        self.metador_layout.ids.metador_list,
                        self.tree_view]
        node_widgets.remove(selected_node_widget)
        for node_widget in node_widgets:
            node_widget.clear_selection()

    def tree_loading_start(self):
        self.app_menu_layout.ids.tree_progress.start_spinning()

    def tree_loading_stop(self):
        Clock.schedule_once(self.app_menu_layout.ids.tree_progress.stop_spinning, 1)

if __name__ == '__main__':
    MetadorGui().run()
