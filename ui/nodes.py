from kivy.uix.treeview import TreeViewNode
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from DragNDropWidget import DragNDropWidget


class BorderLessNode(TreeViewNode):

    """Tree View Node without annoying borders"""


class BaseNode(BorderLessNode):

    path = StringProperty("")
    is_mapped = BooleanProperty(True)
    node_type = StringProperty("")
    text = StringProperty("")
    color_selected_ms = [0, .8, .9, .2]
    is_ms = BooleanProperty(False)
    color_selected = [.5, .5, .85, .08]
    even_color = [.5, .5, .5, 0]


class FileNode(BoxLayout, BaseNode):
    file_icon = Image(source=r"res\icons\\file_icon_white.png",
                      mipmap=True)
    node_type = StringProperty("File")
    file_size = StringProperty("")


class ListNode(FileNode):
    file_type = StringProperty("")
    file_duration = StringProperty("")


class FolderNode(BoxLayout, BaseNode):
    file_icon = Image(source=r"res\icons\grey_folder.png",
                      mipmap=True)
    is_sub_nodes = BooleanProperty(False)
    node_type = StringProperty("Folder")
    folder_color_sub_nodes = [0, 1, 1, 1]
    folder_icon_color = [.6, .75, .8, 0.5]
    is_ms = BooleanProperty(False)

    def debug(self):
        print "debug"


class RootNode(Label, TreeViewNode):

    path = StringProperty("")
    is_mapped = BooleanProperty(False)
    node_type = StringProperty("Root")
    color_selected = [.0, .0, .0, .03]
    color_selected_ms = [0, .8, .9, .2]
    is_ms = BooleanProperty(False)
    no_selection = True