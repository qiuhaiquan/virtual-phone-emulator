# src/core/hardware/physical_storage.py
import os
import platform
import subprocess
import logging

logger = logging.getLogger(__name__)


class PhysicalStorage:
    def __init__(self, root_path: str = None, drive_letter: str = "G"):
        self.os = platform.system()
        self.drive_letter = drive_letter.upper()

        # 跨平台默认存储路径
        if not root_path:
            if self.os == "Windows":
                root_path = os.path.join(os.environ["TEMP"], "virtual_phone_storage")
            elif self.os == "Linux":
                root_path = os.path.join(os.path.expanduser("~"), ".virtual_phone_storage")
            else:  # macOS
                root_path = os.path.join(os.path.expanduser("~"), "Library/Application Support/virtual_phone_storage")

        self.root_path = root_path
        os.makedirs(self.root_path, exist_ok=True)
        logger.info(f"物理存储路径: {self.root_path}")

        # 仅在Windows上尝试挂载盘符
        if self.os == "Windows":
            self._mount_as_drive()

    def _mount_as_drive(self) -> bool:
        """根据操作系统选择挂载方式"""
        if self.os == "Windows":
            return self._mount_windows_drive()
        elif self.os == "Linux":
            return self._mount_linux_drive()
        else:  # macOS
            return self._mount_macos_drive()

    def _mount_windows_drive(self) -> bool:
        """在Windows上挂载目录为虚拟驱动器"""
        try:
            # 检查盘符是否已被使用
            if os.system(f"if exist {self.drive_letter}:\\ echo exists") == 0:
                logger.warning(f"盘符 {self.drive_letter}: 已被使用，无法挂载")
                return False

            subprocess.run(
                f"subst {self.drive_letter}: {self.root_path}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"成功将 {self.root_path} 挂载为 {self.drive_letter}:")
            return True
        except Exception as e:
            logger.error(f"挂载盘符失败: {e}")
            return False

    def _mount_linux_drive(self) -> bool:
        """在Linux上创建挂载点（使用符号链接模拟）"""
        try:
            # 创建用户主目录下的链接
            link_path = os.path.join(os.path.expanduser("~"), "virtual_phone_drive")
            if os.path.exists(link_path):
                if not os.path.islink(link_path):
                    logger.warning(f"{link_path} 已存在且不是符号链接")
                    return False
                os.unlink(link_path)

            os.symlink(self.root_path, link_path)
            logger.info(f"已在 {link_path} 创建指向 {self.root_path} 的符号链接")
            return True
        except Exception as e:
            logger.error(f"创建符号链接失败: {e}")
            return False

    def _mount_macos_drive(self) -> bool:
        """在macOS上创建挂载点（使用符号链接模拟）"""
        try:
            # 创建用户主目录下的链接
            link_path = os.path.join(os.path.expanduser("~"), "virtual_phone_drive")
            if os.path.exists(link_path):
                if not os.path.islink(link_path):
                    logger.warning(f"{link_path} 已存在且不是符号链接")
                    return False
                os.unlink(link_path)

            os.symlink(self.root_path, link_path)
            logger.info(f"已在 {link_path} 创建指向 {self.root_path} 的符号链接")
            return True
        except Exception as e:
            logger.error(f"创建符号链接失败: {e}")
            return False

    def unmount_drive(self) -> bool:
        """根据操作系统卸载挂载点"""
        if self.os == "Windows":
            return self._unmount_windows_drive()
        elif self.os == "Linux":
            return self._unmount_linux_drive()
        else:  # macOS
            return self._unmount_macos_drive()

    def _unmount_windows_drive(self) -> bool:
        """卸载Windows虚拟驱动器"""
        try:
            subprocess.run(
                f"subst {self.drive_letter}: /D",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"成功卸载盘符 {self.drive_letter}:")
            return True
        except Exception as e:
            logger.error(f"卸载盘符失败: {e}")
            return False

    def _unmount_linux_drive(self) -> bool:
        """删除Linux符号链接"""
        try:
            link_path = os.path.join(os.path.expanduser("~"), "virtual_phone_drive")
            if os.path.islink(link_path):
                os.unlink(link_path)
                logger.info(f"已删除符号链接 {link_path}")
            return True
        except Exception as e:
            logger.error(f"删除符号链接失败: {e}")
            return False

    def _unmount_macos_drive(self) -> bool:
        """删除macOS符号链接"""
        return self._unmount_linux_drive()  # 与Linux实现相同

    def create_file(self, path: str, content: str) -> bool:
        """创建文件"""
        try:
            full_path = os.path.join(self.root_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"文件创建成功: {full_path}")
            return True
        except Exception as e:
            logger.error(f"创建文件失败 {path}: {e}")
            return False

    def read_file(self, path: str) -> str:
        """读取文件"""
        try:
            full_path = os.path.join(self.root_path, path)
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {path}: {e}")
            return None

    def list_files(self, directory: str = "") -> list:
        """列出目录下的所有文件和文件夹"""
        try:
            full_path = os.path.join(self.root_path, directory)
            if not os.path.exists(full_path):
                return []
            return os.listdir(full_path)
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []

    def delete_file(self, path: str) -> bool:
        """删除文件"""
        try:
            full_path = os.path.join(self.root_path, path)
            if os.path.isfile(full_path):
                os.remove(full_path)
                logger.info(f"文件删除成功: {full_path}")
                return True
            logger.warning(f"文件不存在: {full_path}")
            return False
        except Exception as e:
            logger.error(f"删除文件失败 {path}: {e}")
            return False