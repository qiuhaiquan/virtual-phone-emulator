# src/core/dalvik/android_runtime.py
import logging
from .vm import DalvikVM

logger = logging.getLogger(__name__)


class AndroidRuntime:
    """Android运行时环境"""

    def __init__(self, hardware_abstraction):
        self.vm = DalvikVM()
        self.hardware_abstraction = hardware_abstraction
        self._register_native_methods()

    def _register_native_methods(self) -> None:
        """注册本地方法"""
        # 注册硬件相关的本地方法
        self.vm.register_native_method("android/os/Build.getDevice", self._get_device)
        self.vm.register_native_method("android/os/Build.getModel", self._get_model)
        self.vm.register_native_method("android/content/Context.getFilesDir", self._get_files_dir)

    def load_and_execute_dex(self, dex_data: bytes) -> None:
        """加载并执行DEX文件"""
        if self.vm.load_dex(dex_data):
            logger.info("DEX文件加载成功，准备执行")
            self.vm.execute_main(dex_data)
        else:
            logger.error("DEX文件加载失败")

    def _get_device(self, vm, method, parser) -> None:
        """模拟android/os/Build.getDevice本地方法"""
        hardware_info = self.hardware_abstraction.hardware_info
        device_name = hardware_info.get('device_name', 'VirtualPhone')
        logger.info(f"返回设备名: {device_name}")

        # 在实际实现中，需要将结果返回给虚拟机
        # 这里简化处理，只记录日志

    def _get_model(self, vm, method, parser) -> None:
        """模拟android/os/Build.getModel本地方法"""
        model_name = "Doubao Virtual Phone"
        logger.info(f"返回设备型号: {model_name}")

    def _get_files_dir(self, vm, method, parser) -> None:
        """模拟android/content/Context.getFilesDir本地方法"""
        storage = self.hardware_abstraction.get_storage()
        if storage:
            logger.info(f"返回文件目录: /data/data/com.example.app")
        else:
            logger.warning("存储不可用")