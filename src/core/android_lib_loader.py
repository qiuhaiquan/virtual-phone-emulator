# src/core/android_lib_loader.py
# -*- coding: utf-8 -*-
import os
import zipfile
import importlib.util
import tempfile
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AndroidLibLoader:
    """Android库加载器，支持从ZIP文件按需加载模块"""

    def __init__(self, lib_zip_path: str):
        self.lib_zip_path = lib_zip_path
        self.zip_file = zipfile.ZipFile(lib_zip_path, 'r')
        self.loaded_modules: Dict[str, Any] = {}
        self.temp_dir = tempfile.mkdtemp(prefix="android_lib_")

    def load_class(self, class_name: str) -> Optional[Any]:
        """从ZIP中加载指定类"""
        # 将Java类名转换为Python模块路径
        module_path = self._convert_class_to_module(class_name)

        # 检查模块是否已加载
        if module_path in self.loaded_modules:
            return self.loaded_modules[module_path]

        # 查找ZIP中的文件
        try:
            file_info = self.zip_file.getinfo(module_path + ".py")
        except KeyError:
            logger.warning(f"未找到类: {class_name}")
            return None

        # 解压文件到临时目录
        extracted_path = self.zip_file.extract(file_info, self.temp_dir)

        # 动态导入模块
        spec = importlib.util.spec_from_file_location(module_path, extracted_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 缓存已加载的模块
        self.loaded_modules[module_path] = module

        # 提取类
        class_parts = class_name.split('.')
        class_name_only = class_parts[-1]

        if hasattr(module, class_name_only):
            return getattr(module, class_name_only)
        else:
            logger.warning(f"模块 {module_path} 中未找到类 {class_name_only}")
            return None

    def _convert_class_to_module(self, class_name: str) -> str:
        """将Java类名转换为Python模块路径"""
        # 例如: "android.os.Build" -> "android_libs.base.os.Build"
        parts = class_name.split('.')
        package_parts = parts[:-1]

        # 映射Android包到我们的库结构
        if package_parts[0] == "android":
            package_parts[0] = "android_libs"

            # 特殊映射
            if len(package_parts) > 1:
                if package_parts[1] == "os":
                    package_parts[1] = "base"
                elif package_parts[1] == "hardware":
                    package_parts[1] = "hardware"
                # 可以添加更多包映射...

        return ".".join(package_parts) + "." + parts[-1]

    def cleanup(self) -> None:
        """清理临时文件"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"清理临时目录: {self.temp_dir}")