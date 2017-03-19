from kivy.uix.modalview import ModalView
from kivy.properties import BooleanProperty, ListProperty, \
                            ObjectProperty, NumericProperty
from kivy.clock import Clock
from PIL import Image, ImageDraw, ImageFilter
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from kivymd.dialog import MDDialog
RAD_MULT = 0.25 # PIL GBlur seems to be stronger than Chrome's so I lower the radius


class BaseModal(ModalView):
    is_open = BooleanProperty(False)

    def on_open(self):
        self.is_open = True

    def on_dismiss(self):
        self.is_open = False


class MaterialModal(ModalView):

    shadow_texture1 = ObjectProperty(None)
    shadow_pos1 = ListProperty([0, 0])
    shadow_size1 = ListProperty([0, 0])

    shadow_texture2 = ObjectProperty(None)
    shadow_pos2 = ListProperty([0, 0])
    shadow_size2 = ListProperty([0, 0])

    elevation = NumericProperty(5)

    _shadows = {
        1: (1, 3, 0.12, 1, 2, 0.24),
        2: (3, 6, 0.16, 3, 6, 0.23),
        3: (10, 20, 0.19, 6, 6, 0.23),
        4: (14, 28, 0.25, 10, 10, 0.22),
        5: (19, 38, 0.30, 15, 12, 0.22)
    }

    def __init__(self, *args, **kwargs):
        super(MaterialModal, self).__init__(*args, **kwargs)

        self._update_shadow = Clock.create_trigger(self._create_shadow)

    def on_size(self, *args, **kwargs):
        self._update_shadow()

    def on_pos(self, *args, **kwargs):
        self._update_shadow()

    def on_elevation(self, *args, **kwargs):
        self._update_shadow()

    def _create_shadow(self, *args):
        # print "update shadow"
        ow, oh = self.size[0], self.size[1]

        offset_x = 0

        # Shadow 1
        shadow_data = self._shadows[self.elevation]
        offset_y = shadow_data[0]
        radius = shadow_data[1]
        w, h = ow + radius * 6.0, oh + radius * 6.0
        t1 = self._create_boxshadow(ow, oh, radius, shadow_data[2])
        self.shadow_texture1 = t1
        self.shadow_size1 = w, h
        self.shadow_pos1 = self.x - \
                           (w - ow) / 2. + offset_x, self.y - (h - oh) / 2. - offset_y

        # Shadow 2
        shadow_data = self._shadows[self.elevation]
        offset_y = shadow_data[3]
        radius = shadow_data[4]
        w, h = ow + radius * 6.0, oh + radius * 6.0
        t2 = self._create_boxshadow(ow, oh, radius, shadow_data[5])
        self.shadow_texture2 = t2
        self.shadow_size2 = w, h
        self.shadow_pos2 = self.x - \
                           (w - ow) / 2. + offset_x, self.y - (h - oh) / 2. - offset_y

    def _create_boxshadow(self, ow, oh, radius, alpha):
        # We need a bigger texture to correctly blur the edges
        w = ow + radius * 6.0
        h = oh + radius * 6.0
        w = int(w)
        h = int(h)
        texture = Texture.create(size=(w, h), colorfmt='rgba')
        im = Image.new('RGBA', (w, h), color=(1, 1, 1, 0))

        draw = ImageDraw.Draw(im)
        # the rectangle to be rendered needs to be centered on the texture
        x0, y0 = (w - ow) / 2., (h - oh) / 2.
        x1, y1 = x0 + ow - 1, y0 + oh - 1
        draw.rectangle((x0, y0, x1, y1), fill=(0, 0, 0, int(255 * alpha)))
        im = im.filter(ImageFilter.GaussianBlur(radius * RAD_MULT))
        texture.blit_buffer(im.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        return texture


class AboutModal(MaterialModal):
    pass


class LoadingModal(BaseModal):
    pass


class MessageModal(MaterialModal):

    icon_string = StringProperty("fa-remove")

    def message(self, icon, header, content):
        self.ids["content_label"].text = content
        self.ids["header_label"].text = header
        self.icon_string = icon
        self.open()


class SettingsModal(MaterialModal):
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


class TestModal(MDDialog):
    pass