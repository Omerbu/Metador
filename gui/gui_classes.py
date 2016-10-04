from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout,GridLayoutException
from kivy.uix.scrollview import ScrollView
from kivy.properties import BooleanProperty, ObjectProperty, \
                            ListProperty, StringProperty,NumericProperty
from kivy.core.window import Window
from kivy.uix.button import Button


"""Color Buttons"""


class ColorButton(Button):
    """
    Button with a possibility to change the color on on_press (similar to background_down in normal Button widget)
    """
    background_color_normal = ListProperty([0, 0.4, 0.8, 1])
    background_color_down = ListProperty([0, 0.7, 1, 1])

    def __init__(self, **kwargs):
        super(ColorButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = self.background_color_normal

    def on_press(self):
        self.background_color = self.background_color_down

    def on_release(self):
        self.background_color = self.background_color_normal


class BlackButton(ColorButton):
    background_color_normal = ListProperty([0, 0, 0, 1])
    background_color_down = ListProperty([0, 0, 0, 1])


class BlueButton(ColorButton):
    background_color_normal = ListProperty([0, 0.4, 0.8, 1])
    background_color_down = ListProperty([0, 0.7, 1, 1])


class GreenButton(ColorButton):
    background_color_normal = ListProperty([0, 0.6, 0.1, 1])
    background_color_down = ListProperty([0, 1, 0, 1])


class RedButton(ColorButton):
    background_color_normal= ListProperty([0.75, 0, 0, 1])
    background_color_down= ListProperty([1, 0, 0, 2])


class AppMenuColor(ColorButton):
    background_color_normal= ListProperty([0, 0, 0, 1])
    background_color_down = ListProperty([0, 0.4, 0.8, 1])

"""Custom Widgets"""


class ScrollableLabel(ScrollView):
    text = StringProperty("")
    font_size = NumericProperty(15)


class HoverBehavior(object):
    """Hover behavior.

    :Events:
        `on_enter`
            Fired when mouse enter the bbox of the widget.
        `on_leave`
            Fired when the mouse exit the widget
    """

    hovered = BooleanProperty(False)
    border_point = ObjectProperty(None)
    '''Contains the last relevant point received by the Hoverable. This can
    be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        pos = args[1]
        inside = self.collide_point(*pos)
        if self.hovered == inside:
            # We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass


class AppMenuHoverBehavior(HoverBehavior):

    def on_mouse_pos(self, *args):
        pos = args[1]
        pos = (pos[0], pos[1]-530)
        inside = self.collide_point(*pos)
        if self.hovered == inside:
            # We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

"""Layouts"""


class AnimatedBoxLayout(BoxLayout):

    def do_layout(self, *largs):
        # optimize layout by preventing looking at the same attribute in a loop
        len_children = len(self.children)
        if len_children == 0:
            return
        selfx = self.x
        selfy = self.y
        selfw = self.width
        selfh = self.height
        padding_left = self.padding[0]
        padding_top = self.padding[1]
        padding_right = self.padding[2]
        padding_bottom = self.padding[3]
        spacing = self.spacing
        orientation = self.orientation
        padding_x = padding_left + padding_right
        padding_y = padding_top + padding_bottom

        # calculate maximum space used by size_hint
        stretch_weight_x = 0.
        stretch_weight_y = 0.
        minimum_size_x = padding_x + spacing * (len_children - 1)
        minimum_size_y = padding_y + spacing * (len_children - 1)
        for w in self.children:
            shw = w.size_hint_x
            shh = w.size_hint_y
            if shw is None:
                minimum_size_x += w.width
            else:
                stretch_weight_x += shw
            if shh is None:
                minimum_size_y += w.height
            else:
                stretch_weight_y += shh

        if orientation == 'horizontal':
            x = padding_left
            stretch_space = max(0.0, selfw - minimum_size_x)
            for c in reversed(self.children):
                shw = c.size_hint_x
                shh = c.size_hint_y
                w = c.width
                h = c.height
                cx = selfx + x
                cy = selfy + padding_bottom

                if shw:
                    w = stretch_space * shw / stretch_weight_x
                if shh:
                    h = max(0, shh * (selfh - padding_y))

                for key, value in c.pos_hint.items():
                    posy = value * (selfh - padding_y)
                    if key == 'y':
                        cy += posy
                    elif key == 'top':
                        cy += posy - h
                    elif key == 'center_y':
                        cy += posy - (h / 2.)

                c.x = int(cx)
                c.y = int(cy)
                c.width = int(w)
                c.height = int(h)
                x += w + spacing

        if orientation == 'vertical':
            y = padding_bottom
            stretch_space = max(0.0, selfh - minimum_size_y)
            for c in self.children:
                shw = c.size_hint_x
                shh = c.size_hint_y
                w = c.width
                h = c.height
                cx = selfx + padding_left
                cy = selfy + y

                if shh:
                    h = stretch_space * shh / stretch_weight_y
                if shw:
                    w = max(0, shw * (selfw - padding_x))

                for key, value in c.pos_hint.items():
                    posx = value * (selfw - padding_x)
                    if key == 'x':
                        cx += posx
                    elif key == 'right':
                        cx += posx - w
                    elif key == 'center_x':
                        cx += posx - (w / 2.)

                c.x = int(cx)
                c.y = int(cy)
                c.width = int(w)
                c.height = int(h)
                y += h + spacing
