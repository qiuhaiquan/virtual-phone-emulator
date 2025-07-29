# android_libs/graphics/drawable.py
class Drawable:
    """ģ�� android.graphics.drawable.Drawable ��"""

    def __init__(self, hardware_abstraction):
        self.hardware_abstraction = hardware_abstraction

    def draw(self, canvas):
        """��Canvas�ϻ���"""
        pass


class ColorDrawable(Drawable):
    """ģ�� android.graphics.drawable.ColorDrawable ��"""

    def __init__(self, hardware_abstraction, color):
        super().__init__(hardware_abstraction)
        self.color = color

    def draw(self, canvas):
        # ��ȡ�߽�
        bounds = self.get_bounds()
        if bounds:
            left, top, right, bottom = bounds
            canvas.draw_rect(left, top, right, bottom, self.color)

    def get_bounds(self):
        pass