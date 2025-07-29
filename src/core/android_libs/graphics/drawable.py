# android_libs/graphics/drawable.py
class Drawable:
    """模拟 android.graphics.drawable.Drawable 类"""

    def __init__(self, hardware_abstraction):
        self.hardware_abstraction = hardware_abstraction

    def draw(self, canvas):
        """在Canvas上绘制"""
        pass


class ColorDrawable(Drawable):
    """模拟 android.graphics.drawable.ColorDrawable 类"""

    def __init__(self, hardware_abstraction, color):
        super().__init__(hardware_abstraction)
        self.color = color

    def draw(self, canvas):
        # 获取边界
        bounds = self.get_bounds()
        if bounds:
            left, top, right, bottom = bounds
            canvas.draw_rect(left, top, right, bottom, self.color)

    def get_bounds(self):
        pass