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

    def _initialize_virtual_camera(self):
        # 这里可以添加实际的相机初始化逻辑
        pass

    def _initialize_virtual_microphone(self):
        try:
            # 可以使用第三方库如 pyaudio 来模拟麦克风
            import pyaudio
            self.virtual_microphone = pyaudio.PyAudio()
            logger.info("虚拟麦克风已初始化")
        except ImportError:
            logger.error("未找到 pyaudio 库，请安装 pyaudio 以使用虚拟麦克风功能")
            self.virtual_microphone = None
        except Exception as e:
            logger.error(f"初始化虚拟麦克风失败: {e}")
            self.virtual_microphone = None

    def _initialize_virtual_gps(self):
        try:
            # 可以使用随机坐标来模拟 GPS 数据
            import random
            self.virtual_gps = {
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180)
            }
            logger.info(f"虚拟 GPS 已初始化，坐标: {self.virtual_gps}")
        except Exception as e:
            logger.error(f"初始化虚拟 GPS 失败: {e}")
            self.virtual_gps = None

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

    def _initialize_virtual_network(self):
        try:
            # 可以使用 socket 来模拟网络连接
            import socket
            self.virtual_network = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info("虚拟网络已初始化")
        except Exception as e:
            logger.error(f"初始化虚拟网络失败: {e}")
            self.virtual_network = None

    def get_storage(self):
        """获取虚拟存储设备"""
        return self.virtual_storage
