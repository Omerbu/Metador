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
    example_dict = {"[Title]": "Epitaph",
                    "[Album]": "The Snow Goose",
                    "[Artist]": "Camel",
                    "[Track]": "13",
                    "[Year]": "1975"}

    def add_to_format(self, input_string):
        self.ids["sorting_text_input"].text += "[{}] ".format(input_string)

    def update_example(self):
        self.example_text = str()
        self.new_text = self.ids["sorting_text_input"].text
        self.new_text = self.new_text.split()
        for word in self.new_text:
            try:
                self.example_text += "{} - ".format(self.example_dict[word])
            except KeyError:
                self.example_text += word
        self.ids["example_label"].text = self.example_text
