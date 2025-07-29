# src/core/graphics/surface_flinger.py
import logging
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


class Surface:
    """表示一个图形表面"""

    def __init__(self, width: int, height: int, format: str = "RGBA"):
        self.width = width
        self.height = height
        self.format = format
        self.image = Image.new(format, (width, height), color=(0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def clear(self, color: tuple = (0, 0, 0, 0)) -> None:
        """清除表面内容"""
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)

    def get_image(self) -> Image:
        """获取表面图像"""
        return self.image


class SurfaceFlinger:
    """Android SurfaceFlinger的模拟实现"""

    def __init__(self, hardware_abstraction):
        self.hardware_abstraction = hardware_abstraction
        self.surfaces = {}  # 存储所有注册的surface
        self.display_surface = None

    def create_surface(self, name: str, width: int, height: int) -> Surface:
        """创建一个新的surface"""
        surface = Surface(width, height)
        self.surfaces[name] = surface
        logger.info(f"创建Surface: {name} ({width}x{height})")
        return surface

    def set_display_surface(self, name: str) -> None:
        """设置要显示的surface"""
        if name in self.surfaces:
            self.display_surface = self.surfaces[name]
            logger.info(f"设置显示Surface: {name}")
        else:
            logger.error(f"Surface不存在: {name}")

    def composite(self) -> None:
        """执行合成操作，将所有surface合并到显示表面"""
        if not self.display_surface:
            logger.warning("没有设置显示Surface")
            return

        # 在实际实现中，这里会处理多个surface的合成
        # 简化版实现，仅更新显示
        self.hardware_abstraction.display.update(self.display_surface.get_image())