# src/core/graphics/canvas.py
from PIL import ImageDraw, ImageFont


class Canvas:
    """Android Canvas API的模拟实现"""

    def __init__(self, surface):
        self.surface = surface
        self.draw = ImageDraw.Draw(surface.image)
        self.font = ImageFont.load_default()  # 默认字体

    def draw_rect(self, left: int, top: int, right: int, bottom: int, color: tuple) -> None:
        """绘制矩形"""
        self.draw.rectangle((left, top, right, bottom), fill=color)

    def draw_text(self, x: int, y: int, text: str, color: tuple) -> None:
        """绘制文本"""
        self.draw.text((x, y), text, fill=color, font=self.font)

    def draw_circle(self, x: int, y: int, radius: int, color: tuple) -> None:
        """绘制圆形"""
        self.draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

    def set_font(self, font_path: str, size: int) -> None:
        """设置字体"""
        try:
            self.font = ImageFont.truetype(font_path, size)
        except Exception as e:
            # 如果加载字体失败，使用默认字体
            self.font = ImageFont.load_default()
            print(f"加载字体失败: {e}")