# src/core/hardware/display.py
import logging
from PIL import Image

logger = logging.getLogger(__name__)


class Display:
    """显示设备的硬件抽象"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.current_image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))

    def update(self, image: Image) -> None:
        """更新显示内容"""
        self.current_image = image
        logger.info("显示内容已更新")

    def get_framebuffer(self) -> bytes:
        """获取帧缓冲区数据"""
        return self.current_image.tobytes()