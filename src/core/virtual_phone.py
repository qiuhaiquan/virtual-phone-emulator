# src/core/virtual_phone.py
import logging
from .hardware.detector import HardwareDetector
from .hardware.abstraction import HardwareAbstractionLayer
from .apk.python_apk_loader import PythonAPKLoader

logger = logging.getLogger(__name__)


class VirtualPhone:
    """虚拟手机主类，整合所有模块"""

    def __init__(self):
        self.hardware_detector = HardwareDetector()
        self.hardware_info = self.hardware_detector.detect_all_hardware()
        self.hardware_abstraction = HardwareAbstractionLayer(self.hardware_info)
        self.apk_executor = None
        self.running = False

    def start(self) -> None:
        """启动虚拟手机"""
        logger.info("正在启动虚拟手机...")
        self.hardware_abstraction.initialize_virtual_devices()
        self.running = True
        logger.info("虚拟手机已启动")

    def install_apk(self, apk_path: str) -> bool:
        """安装APK文件"""
        if not self.running:
            logger.error("虚拟手机未启动，请先调用start方法")
            return False

        logger.info(f"正在安装APK: {apk_path}")

        # 尝试加载C++/Java APK执行器
        try:
            from apk_loader import APKExecutor
            logger.info("使用C++/Java APK执行器")
            self.apk_executor = APKExecutor(self.hardware_abstraction)
        except ImportError:
            # 回退到纯Python实现
            from .apk.python_apk_loader import PythonAPKLoader
            logger.info("使用纯Python APK执行器（功能有限）")
            self.apk_executor = PythonAPKLoader(apk_path, self.hardware_abstraction)

        return self.apk_executor.load()

    def run_apk(self, apk_path: str) -> None:
        """运行指定APK文件"""
        if not self.running:
            logger.error("虚拟手机未启动，请先调用start方法")
            return

        if self.install_apk(apk_path):
            logger.info(f"正在运行APK: {apk_path}")
            self.apk_executor.run()
        else:
            logger.error(f"无法运行APK: {apk_path}")

    def stop(self) -> None:
        """停止虚拟手机运行"""
        if self.running:
            logger.info("正在停止虚拟手机...")
            # 清理资源
            if hasattr(self.apk_executor, 'cleanup'):
                self.apk_executor.cleanup()

            self.running = False
            logger.info("虚拟手机已停止")

    def get_hardware_info(self) -> dict:
        """获取检测到的硬件信息"""
        return self.hardware_info