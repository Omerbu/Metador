from kivy.uix.modalview import ModalView
from kivy.properties import BooleanProperty


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
