# src/core/graphics/surface_flinger.py
import logging
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


class Surface:
    """��ʾһ��ͼ�α���"""

    def __init__(self, width: int, height: int, format: str = "RGBA"):
        self.width = width
        self.height = height
        self.format = format
        self.image = Image.new(format, (width, height), color=(0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def clear(self, color: tuple = (0, 0, 0, 0)) -> None:
        """�����������"""
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)

    def get_image(self) -> Image:
        """��ȡ����ͼ��"""
        return self.image


class SurfaceFlinger:
    """Android SurfaceFlinger��ģ��ʵ��"""

    def __init__(self, hardware_abstraction):
        self.hardware_abstraction = hardware_abstraction
        self.surfaces = {}  # �洢����ע���surface
        self.display_surface = None

    def create_surface(self, name: str, width: int, height: int) -> Surface:
        """����һ���µ�surface"""
        surface = Surface(width, height)
        self.surfaces[name] = surface
        logger.info(f"����Surface: {name} ({width}x{height})")
        return surface

    def set_display_surface(self, name: str) -> None:
        """����Ҫ��ʾ��surface"""
        if name in self.surfaces:
            self.display_surface = self.surfaces[name]
            logger.info(f"������ʾSurface: {name}")
        else:
            logger.error(f"Surface������: {name}")

    def composite(self) -> None:
        """ִ�кϳɲ�����������surface�ϲ�����ʾ����"""
        if not self.display_surface:
            logger.warning("û��������ʾSurface")
            return

        # ��ʵ��ʵ���У�����ᴦ����surface�ĺϳ�
        # �򻯰�ʵ�֣���������ʾ
        self.hardware_abstraction.display.update(self.display_surface.get_image())