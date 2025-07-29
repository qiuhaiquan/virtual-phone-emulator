# src/core/hardware/display.py
import logging
from PIL import Image

logger = logging.getLogger(__name__)


class Display:
    """��ʾ�豸��Ӳ������"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.current_image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))

    def update(self, image: Image) -> None:
        """������ʾ����"""
        self.current_image = image
        logger.info("��ʾ�����Ѹ���")

    def get_framebuffer(self) -> bytes:
        """��ȡ֡����������"""
        return self.current_image.tobytes()