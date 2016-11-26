from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import BooleanProperty, ObjectProperty, \
                            ListProperty, StringProperty, NumericProperty
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.treeview import TreeViewNode
from kivy.uix.togglebutton import ToggleButtonBehavior


"""Color Buttons"""


class SimpleTransparentButton(Button):

    def __init__(self, **kwargs):
        super(SimpleTransparentButton, self).__init__(**kwargs)
        self.markup = True
        self.background_normal = ""
        self.background_down = ""
        self.background_color = [1, 1, 1, 0]


class FlatButton(SimpleTransparentButton):

    icon_color = StringProperty("5c7f8a")
    underline_color = ListProperty([1, 1, 1, 0])

    def on_state(self, _, new_state):
        if new_state == 'down':
            self.underline_color = [0, 1, 1, 1]
            self.icon_color = "00ffff"
        else:
            self.underline_color = [1, 1, 1, 0]
            self.icon_color = "5c7f8a"


class TransparentButton(Button):

    line_color = ListProperty([.4, .42, .45, 0])
    shade_color = ListProperty([0, 0, 0, 0])
    back_color = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super(TransparentButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = [1, 1, 1, 0]

    def on_state(self, _, new_state):
        if new_state == 'down':
            self.line_color[3] = .2
            self.shade_color[3] = .05
            self.back_color[3] = .08
            self.color = [.6, 1, 1, 1]
        else:
            self.line_color[3] = 0
            self.shade_color[3] = 0
            self.back_color[3] = 0
            self.color = 1, 1, 1, 1


class ToggleFlatButton(ToggleButtonBehavior, FlatButton):

    def on_touch_down(self, touch):
        if self.state == "down":
            return 
        super(ToggleFlatButton, self).on_touch_down(touch)


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
        pos = (pos[0], pos[1]-525)
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


class BorderLessNode(TreeViewNode):
    """Tree View Node without annoying borders"""
