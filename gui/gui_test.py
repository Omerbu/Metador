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

class SomeButton(Button):

    def __init__(self):
        super(SomeButton, self).__init__()

    def on_touch_down(self, touch):
        if touch.button == "left":
            super(SomeButton, self).on_touch_down(touch=touch)
        if touch.button == "right":
            return True



class TemplateApp(App):

    ALLOW_DRAG = False

    def build(self):
        Window.bind(on_dropfile=self.drop_file)
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        root_widget = GridLayout(cols=2)
        self.browser = FileChooserListView()
        self.browser.bind(
            on_success=self._fbrowser_success,
            on_canceled=self._fbrowser_canceled)
        self.open_button = SomeButton()
        self.label = Label()
        self.popup_browser= Popup(title="File Browser", content=self.browser,
                                  auto_dismiss=True)
        self.popup_browser.size_hint_x = 0.7
        self.popup_browser.set_center_x(50)
        self.open_button.bind(on_press=self.popup_browser.open)
        self.test_list = [str(x) for x in xrange(30)]
        self.list_adapter = ListAdapter(cls=ListItemButton, data=self.test_list)
        self.list_widget = ListView(adapter=self.list_adapter)
        self.list_label = Label(text="default")
        self.list_adapter.bind(on_selection_change=self.change_list_label)


        root_widget.add_widget(self.open_button)
        root_widget.add_widget(self.label)
        root_widget.add_widget(self.list_widget)
        root_widget.add_widget(self.list_label)
        self.text_input = TextInput()
        root_widget.add_widget(self.text_input)
        return root_widget

    def drop_file(self,window,string):
        print string
        self.ALLOW_DRAG = False

    def _fbrowser_canceled(self, instance):
        self.popup_browser.dismiss()

    def _fbrowser_success(self, instance):
        text = str(instance.selection)
        print self.browser.filters
        self.label.text = text
        self.popup_browser.dismiss()

    def change_list_label(self, adapter):
        print self.list_adapter.selection
        if self.list_adapter.selection:
            self.list_label.text = self.list_adapter.selection[0].text


if __name__ == '__main__':
    TemplateApp().run()
