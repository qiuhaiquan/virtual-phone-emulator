# src/core/hardware/abstraction.py
import os
import logging
from typing import Dict, Any, Optional
from .detector import HardwareDetector
from .virtual_storage import VirtualStorage  # 新增导入

logger = logging.getLogger(__name__)


class HardwareAbstractionLayer:
    """为虚拟手机提供统一的硬件接口"""

    def __init__(self, hardware_info: Dict[str, Any]):
        self.hardware_info = hardware_info
        self.virtual_camera = None
        self.virtual_microphone = None
        self.virtual_gps = None
        self.virtual_storage = None  # 新增属性
        self.virtual_network = None

    def initialize_virtual_devices(self) -> None:
        """初始化所有虚拟硬件设备"""
        self._initialize_virtual_camera()
        self._initialize_virtual_microphone()
        self._initialize_virtual_gps()
        self._initialize_virtual_storage()  # 新增方法
        self._initialize_virtual_network()

    def _initialize_virtual_storage(self) -> None:
        """初始化虚拟存储设备"""
        try:
            # 创建虚拟G盘存储目录
            storage_dir = os.path.expanduser("~/.virtual_phone/g_drive")
            os.makedirs(storage_dir, exist_ok=True)

            # 初始化虚拟存储 (默认16GB)
            self.virtual_storage = VirtualStorage(
                storage_path=storage_dir,
                total_size_gb=16.0
            )

            logger.info(f"虚拟G盘已初始化: {storage_dir}")
        except Exception as e:
            logger.error(f"初始化虚拟存储失败: {e}")
            self.virtual_storage = None

    def get_storage(self):
        """获取虚拟存储设备"""
        return self.virtual_storage