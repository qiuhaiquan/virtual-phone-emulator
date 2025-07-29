# src/core/graphics/canvas.py
from PIL import ImageDraw, ImageFont


class Canvas:
    """Android Canvas API��ģ��ʵ��"""

    def __init__(self, surface):
        self.surface = surface
        self.draw = ImageDraw.Draw(surface.image)
        self.font = ImageFont.load_default()  # Ĭ������

    def draw_rect(self, left: int, top: int, right: int, bottom: int, color: tuple) -> None:
        """���ƾ���"""
        self.draw.rectangle((left, top, right, bottom), fill=color)

    def draw_text(self, x: int, y: int, text: str, color: tuple) -> None:
        """�����ı�"""
        self.draw.text((x, y), text, fill=color, font=self.font)

    def draw_circle(self, x: int, y: int, radius: int, color: tuple) -> None:
        """����Բ��"""
        self.draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

    def set_font(self, font_path: str, size: int) -> None:
        """��������"""
        try:
            self.font = ImageFont.truetype(font_path, size)
        except Exception as e:
            # �����������ʧ�ܣ�ʹ��Ĭ������
            self.font = ImageFont.load_default()
            print(f"��������ʧ��: {e}")