# src/core/apk/python_apk_loader.py
import os
import zipfile
import logging
from ..dalvik.android_runtime import AndroidRuntime  # 新增导入

logger = logging.getLogger(__name__)


class PythonAPKLoader:
    """APK加载器，使用Python实现"""

    def __init__(self, apk_path: str, hardware_abstraction):
        self.apk_path = apk_path
        self.hardware_abstraction = hardware_abstraction
        self.android_runtime = AndroidRuntime(hardware_abstraction)  # 新增
        self.temp_dir = None

    def load(self) -> bool:
        """加载APK文件"""
        try:
            logger.info(f"正在加载APK: {self.apk_path}")

            # 检查文件是否存在
            if not os.path.exists(self.apk_path):
                logger.error(f"APK文件不存在: {self.apk_path}")
                return False

            # 创建临时目录
            self.temp_dir = os.path.join(os.path.dirname(self.apk_path), "temp_apk")
            os.makedirs(self.temp_dir, exist_ok=True)

            # 解压APK
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)

            logger.info(f"APK已解压到: {self.temp_dir}")

            # 查找classes.dex文件
            dex_path = os.path.join(self.temp_dir, "classes.dex")
            if not os.path.exists(dex_path):
                logger.error("未找到classes.dex文件")
                return False

            # 读取DEX文件内容
            with open(dex_path, 'rb') as f:
                self.dex_data = f.read()

            logger.info(f"找到DEX文件，大小: {len(self.dex_data)} 字节")
            return True

        except Exception as e:
            logger.error(f"加载APK失败: {e}")
            return False

    def run(self) -> None:
        """运行APK"""
        if not hasattr(self, 'dex_data'):
            logger.error("DEX文件未加载，请先调用load()方法")
            return

        logger.info("开始执行APK...")

        # 使用Android运行时执行DEX文件
        self.android_runtime.load_and_execute_dex(self.dex_data)

        logger.info("APK执行完成")

    def cleanup(self) -> None:
        """清理临时文件"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info(f"已清理临时目录: {self.temp_dir}")