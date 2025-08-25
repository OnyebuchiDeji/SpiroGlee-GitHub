from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')    ##  Make it fullscreen
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, ReferenceListProperty, ObservableList
from kivy.uix.slider import Slider 
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.uix.popup import Popup

import math
import os
# from random import randrange

# g_file_save_path = os.path.dirname(App()._get_user_data_dir())
g_file_save_path = ""

# print(g_file_save_path)

def angle_to_rad(angle: float):
    return angle * (math.pi/180)

# Window.size = (324, 666)
Builder.load_file("spiro.kv")

g_colors = {"white":(1.0, 1.0, 1.0, 1.0), "app_bg_col":(0.04, 0.03, 0.07, 1)}

class SaveDialog(FloatLayout):
    # spacing = (0, 0, 0,)
    # padding = (0)
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MiscPopup(Popup):
    ...

class Gear(Widget):
    diameter = NumericProperty(0)       
    # size_for_drawing = ListProperty([0.0, 0.0])
    # pos_for_drawing = ListProperty([0.0, 0.0])
    color_outline = ListProperty([0.0, 0.0, 0.0, 1.0])
    color_fill = ListProperty([0.0, 0.0, 0.0, 1.0])

    def update_pos(self, angle, rootRef=None):
        ...

    def get_pos(self, angle, root):
        self.update_pos(root.accumulated_time, root)
        # print("Get Pos Called")
        return self.pos

    def update_color(self, outlineCol, fillCol):
        self.color_outline[0] = outlineCol[0]
        self.color_outline[1] = outlineCol[1]
        self.color_outline[2] = outlineCol[2]
        self.color_fill[0] = fillCol[0]
        self.color_fill[1] = fillCol[1]
        self.color_fill[2] = fillCol[2]
        

class OuterGear(Gear):
    diameter = NumericProperty(100)

    def update_pos(self, rootRef):
        self.pos = rootRef.r_draw_area.center[0] - rootRef.s_outer_gear.value / 2, rootRef.r_draw_area.center[1] - rootRef.s_outer_gear.value / 2
        # print("Outer")
        # print("Pos: ", self.pos )

    def get_start_pos(self, parent_center, rootRef):
        sliderRef = rootRef.s_outer_gear
        self.pos = parent_center[0] - sliderRef.value / 2, parent_center[1] - sliderRef.value / 2
        # print("Outer")
        # print("Start Pos: ", self.pos )
        return self.pos

class InnerGear(Gear):
    diameter = NumericProperty(50)

    def update_pos(self, rootRef):
        angle = rootRef.accumulated_time
        outerGearRef = rootRef.r_outer_gear
        rad_diff = (outerGearRef.diameter - self.diameter) /2
        self.pos = outerGearRef.pos[0] + outerGearRef.diameter/2 - self.diameter / 2 + rad_diff * math.cos(angle_to_rad(angle)), outerGearRef.pos[1] + outerGearRef.diameter / 2- self.diameter / 2 + rad_diff * math.sin(angle_to_rad(angle))

    
    def get_start_pos(self, outerGearPos, outerGearDiameter, rootRef):
        angle = rootRef.accumulated_time
        rad_diff = (outerGearDiameter - self.diameter) /2
        self.pos = outerGearPos[0] + outerGearDiameter/2 - self.diameter / 2 + rad_diff * math.cos(angle_to_rad(angle)), outerGearPos[1] + outerGearDiameter / 2- self.diameter / 2 + rad_diff * math.sin(angle_to_rad(angle))
        # print("Inner")
        # print("Start Pos: ", self.pos)
        
        return self.pos



class Pen(Widget):
    displacement = NumericProperty(0)
    diameter = NumericProperty(10)

    #   This represents the actual position to make the lines be drawn from relative to the pen's position
    #   It offsets the Pen's position, taking into account that the Circle is within a box
    #   and the origin of that box is at the bottom left corner.
    #   Currently, the self.pos of the pen is set so that the bottom left corner is positioned in a way
    #   that makes the Pen appear exactly in the middle of the InnerCircle
    #   But the points to be given to the line points to be drawn from should be a positive offset from the Pen's center
    true_pen_pos_x = NumericProperty(0)
    true_pen_pos_y = NumericProperty(0)
    true_pen_pos = ReferenceListProperty(true_pen_pos_x, true_pen_pos_y)

    def update_pos(self, rootRef=None):
        angle = rootRef.accumulated_time
        angle *= -rootRef.gear_ratio
        innerGearRef = rootRef.r_inner_gear
        self.pos = innerGearRef.pos[0] + innerGearRef.diameter/2 + self.displacement * math.cos(angle_to_rad(angle)), innerGearRef.pos[1] + innerGearRef.diameter / 2 + self.displacement * math.sin(angle_to_rad(angle))
        # print("Pos: ", self.pos)
        # print("True Pos: ")
        self.true_pen_pos[0] = self.pos[0] + self.diameter/2
        self.true_pen_pos[1] = self.pos[1] + self.diameter/2


    def get_start_pos(self, innerGearPos, innerGearDiameter, rootRef):
        angle = rootRef.accumulated_time
        angle *= -rootRef.gear_ratio
        self.pos = innerGearPos[0] + innerGearDiameter/2 + self.displacement * math.cos(angle_to_rad(angle)), innerGearPos[1] + innerGearDiameter / 2 + self.displacement * math.sin(angle_to_rad(angle))
        # print("Pen")
        # print("Start Pos: ", self.pos)
        # print("True Pos: ")
        self.true_pen_pos[0] = self.pos[0] + self.diameter/2
        self.true_pen_pos[1] = self.pos[1] + self.diameter/2
        
        return self.pos





class AppLayout(Widget):
    accumulated_time : float = 0.0
    elapsed_time : float = 0.0
    
    r_outer_gear = ObjectProperty(OuterGear)
    r_inner_gear = ObjectProperty(InnerGear)
    r_pen = ObjectProperty(Pen)
    r_draw_area = ObjectProperty(Widget)

    s_outer_gear = ObjectProperty(Slider)
    s_inner_gear = ObjectProperty(Slider)
    s_pen_displacement = ObjectProperty(Slider)

    points = ListProperty([])

    line_color_prop = ListProperty([1, 0, 0, 1])
    draw_flag = False

    b_first = True
    b_display_gears = True
    gear_ratio = 0    

    def slider_value(self, caller, *args):
        # print(caller.value)
        self.r_outer_gear.update_pos(self)
        # self.r_inner_gear.update_pos(self.accumulated_time, self)
        self.r_inner_gear.update_pos(self)
        # self.r_pen.update_pos(self.accumulated_time, self)
        self.r_pen.update_pos(self)

    
    def on_draw_btn_press(self, caller):
        if (not self.draw_flag):
            self.draw_flag = True
            caller.text = "Stop"
            self.clock_ref = Clock.schedule_interval(self.update, 1/60.0)
        else:
            self.draw_flag = False
            caller.text = "Draw"
            self.clock_ref.cancel()
    
    def on_clear_btn_press(self, caller):
        """Clear the points to be rendered."""
        self.points.clear()
        self.update(dt=0)

    def on_pen_color_btn_press(self, caller):
        """Create Color Picker and Popup Window"""
        self.color_picker = ColorPicker(size_hint_y=None)#,
                                        # height = 400,
                                        # size_hint_x=None,
                                        # width= 300)
        self.color_picker.size[0] = self.r_draw_area.size[0] * 1.1
        self.color_picker.size[1] = self.r_draw_area.size[1] * 1.1
        self.color_picker.bind(color=self.color_choice)
        
        self.temp_popup = MiscPopup()
        self.temp_popup.title = "Color Picker"

        print(self.temp_popup.children)
        grid_layout_ref = self.temp_popup.children[0]
        grid_layout_ref.gap = 10
        popup_button = Button(
            text="Close",
            font_size=14,
            on_release=self.on_close_popup,
            size_hint = (0.4, 0.4),
            pos_hint = {"center_x": 1}
        )

        grid_layout_ref.add_widget(self.color_picker)
        grid_layout_ref.add_widget(popup_button)
        self.temp_popup.open()
    
    def color_choice(self, caller, value):
        # print("RGBA: ", str(value))
        # print("HSV: ", str(caller.hsv))
        # print("HEX: ", str(caller.hex_color))
        self.line_color_prop[0] = value[0]
        self.line_color_prop[1] = value[1]
        self.line_color_prop[2] = value[2]
    
    def on_close_popup(self, *args):
        ##  Args for any other additional arguments passed in though may not be needed
        self.temp_popup.dismiss()

    def create_save_dialog(self):
        content = SaveDialog(save=self.save_image, cancel=self.on_close_popup)
        self.temp_popup = Popup(title=f"Save Image as PNG to {g_file_save_path}", content=content,
                                size_hint=(.9, .9))
        content.ids['id_filechooser'].path = g_file_save_path
        # print(content.ids['id_filechooser'].path)
        self.temp_popup.open()

    def on_save_btn_press(self, caller):
        self.create_save_dialog()
    
    def save_image(self, path: str, filename: str):
        """
            Saves what is Displayed on the Draw Area
            There are two methods:
                1.  `export_as_image()`
                    This returns an core ~kivy.core.image.Image of the actual widget.
                    this Image object can be saved simply by calling its
                    `.save("path")` method.
                2.  `export_as_png(<filename: str>, <scale=1 (default)>)`
                    Saves an image of the widget and its children in png format at the specified filename. Works by removing the widget canvas from its
                    parent, rendering to an ~kivy.graphics.fbo.Fbo, and calling
                    ~kivy.graphics.texture.Texture.save.
        """
    
        image_pixels_obj = self.r_draw_area.export_as_image()
        filename = filename.strip()
        filename += ".png"
        image_pixels_obj.save(os.path.join(path, filename))

        self.on_close_popup()


    def on_hide_gear_btn_press(self, caller):
        """
            Uses these:
                1. b_display_gears flag
                2. The sizes of the gears
            The latter because to draw the Ellipses of the gears
            their sizes are used.
        """
        self.b_display_gears = not self.b_display_gears
        # print("Gear Display State: ", self.b_display_gears)

        outline_col = g_colors['white'] if self.b_display_gears else self.r_draw_area.background_color
        fill_col = g_colors['app_bg_col'] if self.b_display_gears else self.r_draw_area.background_color
        self.r_inner_gear.update_color(outline_col, fill_col)
        self.r_outer_gear.update_color(outline_col, fill_col)

        #   Update text
        caller.text = "Hide\nGears" if self.b_display_gears else "Show\nGears"

    # def update_color(self, dt):
    #     # return (math.sin(dt) * 255, math.cos(dt + 90) * 255, (math.sin(dt) * math.cos(dt-90)) * 255, 1)
    #     return (randrange(0, 255), randrange(55, 196), randrange(0, 205) , 1)

    def update(self, dt):
        # print("called")
        # print(dt)
        self.gear_ratio = self.r_outer_gear.diameter / self.r_inner_gear.diameter

        ##  To ensure that when the Clear Button is clicked,
        ##  nothing moves as long as the `draw_flag` is not True.
        if self.draw_flag:
            self.time_elapsed = Clock.get_time() * 1e-6 * self.ids['s_ds_id'].value
            self.r_outer_gear.update_pos(self)
            self.r_inner_gear.update_pos(self)
            self.r_pen.update_pos(self)
        else:
            time_elapsed = 0
            
        if (self.b_first):
            self.points.append(self.r_pen.true_pen_pos[0])
            self.points.append(self.r_pen.true_pen_pos[1])
            self.b_first = False
        
        # color = self.update_color(dt)

        self.points.append(self.r_pen.true_pen_pos[0])
        self.points.append(self.r_pen.true_pen_pos[1])

        # with self.ids['w_draw_area_id'].canvas:
        #     Color(color[0], color[1], color[2], color[3], mode="rgba")
        #     Line(points=self.points)


        self.accumulated_time += self.time_elapsed 
    
        

class SpiroGlee(App):
    background_color = g_colors['app_bg_col']
    # g_file_save_path = ''
    def build(self):
        self.title = "SpiroGlee"
        Window.clearcolor = self.background_color
        self.icon = "data/icon.ico"
        # Window.fullscreen = True  ##  Don't use this
        global g_file_save_path
        g_file_save_path = os.path.dirname(self._get_user_data_dir())
        # print(g_file_save_path)
        return AppLayout()


if __name__ == "__main__":
    SpiroGlee().run()