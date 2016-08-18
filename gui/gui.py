from kivy.config import Config
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.selectableview import SelectableView
from kivy.adapters.listadapter import ListAdapter
from filebrowser import FileBrowser
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from os.path import sep, expanduser, isdir, dirname
import sys

class TestApp(App):

    def build(self):
        if sys.platform == 'win':
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        root_widget = GridLayout(cols=2)
        self.browser = FileBrowser(select_string='Select',
                              favorites=[(user_path, 'Documents')])
        self.browser.dirselect = True
        self.browser.bind(
            on_success=self._fbrowser_success,
            on_canceled=self._fbrowser_canceled)
        self.open_button = Button(text="Open Browser")
        self.label = Label()
        self.popup_browser= Popup(title="File Browser", content=self.browser,
                                  auto_dismiss=False)
        self.open_button.bind(on_press=self.popup_browser.open)
        self.label.text = "Default text"
        self.test_list = [str(x) for x in xrange(20)]
        self.list_adapter = ListAdapter(cls=ListItemButton, data=self.test_list)
        self.list_widget = ListView(adapter=self.list_adapter)
        self.list_label = Label(text="default")
        self.list_adapter.bind(on_selection_change=self.change_list_label)

        root_widget.add_widget(self.open_button)
        root_widget.add_widget(self.label)
        root_widget.add_widget(self.list_widget)
        root_widget.add_widget(self.list_label)

        return root_widget

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
    TestApp().run()
