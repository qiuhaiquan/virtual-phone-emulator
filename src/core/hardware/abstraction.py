# src/core/hardware/abstraction.py
import os
import logging
import pyaudio
import random
import socket
import time
from typing import Dict, Any, Optional
from .detector import HardwareDetector
from .virtual_storage import VirtualStorage
from .physical_storage import PhysicalStorage


logger = logging.getLogger(__name__)


class HardwareAbstractionLayer:
    """为虚拟手机提供统一的硬件接口"""

    def __init__(self, hardware_info: Dict[str, Any]):
        self.hardware_info = hardware_info
        self.virtual_camera = None
        self.virtual_microphone = None
        self.virtual_gps = None
        self.virtual_storage = None
        self.virtual_network = None
        self.storage = PhysicalStorage(drive_letter="G")

    def _initialize_virtual_camera(self):
        try:
            # 这里可以使用 OpenCV 来模拟相机
            import cv2
            # 尝试打开默认相机
            self.virtual_camera = cv2.VideoCapture(0)
            if self.virtual_camera.isOpened():
                logger.info("虚拟相机已初始化")
            else:
                logger.error("无法打开相机，虚拟相机初始化失败")
        except ImportError:
            logger.error("未找到 OpenCV 库，请安装 OpenCV 以使用虚拟相机功能")
            self.virtual_camera = None
        except Exception as e:
            logger.error(f"初始化虚拟相机失败: {e}")
            self.virtual_camera = None

    def _initialize_virtual_microphone(self):
        try:
            # 使用 pyaudio 来模拟麦克风
            self.virtual_microphone = pyaudio.PyAudio()
            # 打开音频输入流
            stream = self.virtual_microphone.open(format=pyaudio.paInt16,
                                                  channels=1,
                                                  rate=44100,
                                                  input=True,
                                                  frames_per_buffer=1024)
            if stream.is_active():
                logger.info("虚拟麦克风已初始化")
            else:
                logger.error("无法打开音频输入流，虚拟麦克风初始化失败")
        except ImportError:
            logger.error("未找到 pyaudio 库，请安装 pyaudio 以使用虚拟麦克风功能")
            self.virtual_microphone = None
        except Exception as e:
            logger.error(f"初始化虚拟麦克风失败: {e}")
            self.virtual_microphone = None

    def _initialize_virtual_gps(self):
        try:
            # 模拟 GPS 信号的变化
            self.virtual_gps = {
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180),
                "altitude": random.uniform(0, 1000),
                "speed": random.uniform(0, 100),
                "heading": random.uniform(0, 360)
            }
            # 模拟 GPS 信号的更新
            def update_gps():
                while True:
                    # 模拟位置的微小变化
                    self.virtual_gps["latitude"] += random.uniform(-0.0001, 0.0001)
                    self.virtual_gps["longitude"] += random.uniform(-0.0001, 0.0001)
                    self.virtual_gps["altitude"] += random.uniform(-1, 1)
                    self.virtual_gps["speed"] += random.uniform(-1, 1)
                    self.virtual_gps["heading"] += random.uniform(-1, 1)
                    # 确保速度和高度不会为负数
                    self.virtual_gps["speed"] = max(0, self.virtual_gps["speed"])
                    self.virtual_gps["altitude"] = max(0, self.virtual_gps["altitude"])
                    # 确保航向在 0 到 360 度之间
                    self.virtual_gps["heading"] = self.virtual_gps["heading"] % 360
                    logger.info(f"虚拟 GPS 已更新，坐标: {self.virtual_gps}")
                    time.sleep(1)

            import threading
            gps_thread = threading.Thread(target=update_gps)
            gps_thread.daemon = True
            gps_thread.start()
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
            # 使用 socket 来模拟网络连接
            self.virtual_network = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 模拟网络带宽、延迟和丢包率
            def simulate_network():
                while True:
                    # 模拟网络延迟
                    delay = random.uniform(0, 1)
                    time.sleep(delay)
                    # 模拟丢包率
                    if random.random() < 0.1:
                        logger.warning("模拟网络丢包")
                    else:
                        logger.info("网络数据包正常传输")

            import threading
            network_thread = threading.Thread(target=simulate_network)
            network_thread.daemon = True
            network_thread.start()
            logger.info("虚拟网络已初始化")
        except Exception as e:
            logger.error(f"初始化虚拟网络失败: {e}")
            self.virtual_network = None

    def get_storage(self):
        """获取虚拟存储设备"""
        return self.virtual_storage

    def initialize_virtual_devices(self) -> None:
        """初始化所有虚拟硬件设备"""
        # 不再需要初始化虚拟存储
        self._initialize_virtual_camera()
        self._initialize_virtual_microphone()
        self._initialize_virtual_gps()
        self._initialize_virtual_network()

    # 文件操作方法映射到物理存储
    def create_file(self, path: str, content: str) -> bool:
        return self.storage.create_file(path, content)

    def list_files(self) -> list:
        return self.storage.list_files()

    def read_file(self, path: str) -> str:
        return self.storage.read_file(path)

    def delete_file(self, path: str) -> bool:
        return self.storage.delete_file(path)

    # 程序退出时卸载盘符
    def cleanup(self) -> None:
        self.storage.unmount_drive()