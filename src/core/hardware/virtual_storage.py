# src/core/hardware/virtual_storage.py
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VirtualStorage:
    """虚拟存储设备，模拟手机内部存储和外部SD卡"""

    def __init__(self, storage_path: str, total_size_gb: float = 16.0):
        """
        初始化虚拟存储

        Args:
            storage_path: 物理存储路径
            total_size_gb: 虚拟存储总容量(GB)
        """
        self.storage_path = storage_path
        self.total_size = total_size_gb * 1024 * 1024 * 1024  # 转换为字节
        self.used_size = 0
        self.files = {}  # 存储文件元数据

        # 创建存储目录
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
            logger.info(f"创建虚拟存储目录: {storage_path}")

        # 加载存储状态
        self._load_state()

    def _load_state(self) -> None:
        """从文件加载存储状态"""
        state_file = os.path.join(self.storage_path, ".storage_state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
                    self.used_size = state.get("used_size", 0)
                    self.files = state.get("files", {})
                logger.info(f"加载虚拟存储状态: {self.used_size} 字节已使用")
            except Exception as e:
                logger.error(f"加载存储状态失败: {e}")

    def _save_state(self) -> None:
        """保存存储状态到文件"""
        state_file = os.path.join(self.storage_path, ".storage_state.json")
        try:
            with open(state_file, "w") as f:
                json.dump({
                    "used_size": self.used_size,
                    "files": self.files
                }, f)
            logger.debug("保存虚拟存储状态")
        except Exception as e:
            logger.error(f"保存存储状态失败: {e}")

    def get_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        return {
            "total_size": self.total_size,
            "used_size": self.used_size,
            "free_size": self.total_size - self.used_size,
            "file_count": len(self.files)
        }

    def create_file(self, virtual_path: str, size_bytes: int) -> bool:
        """
        创建虚拟文件

        Args:
            virtual_path: 虚拟文件路径
            size_bytes: 文件大小(字节)

        Returns:
            是否创建成功
        """
        # 检查是否有足够空间
        if self.used_size + size_bytes > self.total_size:
            logger.warning(f"存储已满，无法创建文件: {virtual_path}")
            return False

        # 检查路径是否存在
        physical_path = self._get_physical_path(virtual_path)
        dir_path = os.path.dirname(physical_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 创建文件
        try:
            with open(physical_path, "wb") as f:
                f.write(b'\0' * size_bytes)  # 预分配空间

            # 更新文件元数据
            self.files[virtual_path] = {
                "size": size_bytes,
                "created_at": os.path.getctime(physical_path),
                "modified_at": os.path.getmtime(physical_path)
            }

            # 更新使用空间
            self.used_size += size_bytes
            self._save_state()

            logger.info(f"创建虚拟文件: {virtual_path}, 大小: {size_bytes} 字节")
            return True
        except Exception as e:
            logger.error(f"创建文件失败: {e}")
            return False

    def write_file(self, virtual_path: str, data: bytes, offset: int = 0) -> bool:
        """
        写入数据到虚拟文件

        Args:
            virtual_path: 虚拟文件路径
            data: 要写入的数据
            offset: 写入偏移量

        Returns:
            是否写入成功
        """
        if virtual_path not in self.files:
            logger.warning(f"文件不存在: {virtual_path}")
            return False

        physical_path = self._get_physical_path(virtual_path)

        try:
            with open(physical_path, "r+b") as f:
                f.seek(offset)
                f.write(data)

            # 更新修改时间
            self.files[virtual_path]["modified_at"] = os.path.getmtime(physical_path)
            self._save_state()

            logger.debug(f"写入 {len(data)} 字节到文件: {virtual_path}")
            return True
        except Exception as e:
            logger.error(f"写入文件失败: {e}")
            return False

    def read_file(self, virtual_path: str, size: int = -1, offset: int = 0) -> Optional[bytes]:
        """
        从虚拟文件读取数据

        Args:
            virtual_path: 虚拟文件路径
            size: 读取大小(-1表示读取全部)
            offset: 读取偏移量

        Returns:
            读取的数据或None
        """
        if virtual_path not in self.files:
            logger.warning(f"文件不存在: {virtual_path}")
            return None

        physical_path = self._get_physical_path(virtual_path)

        try:
            with open(physical_path, "rb") as f:
                f.seek(offset)
                if size == -1:
                    return f.read()
                else:
                    return f.read(size)
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return None

    def delete_file(self, virtual_path: str) -> bool:
        """
        删除虚拟文件

        Args:
            virtual_path: 虚拟文件路径

        Returns:
            是否删除成功
        """
        if virtual_path not in self.files:
            logger.warning(f"文件不存在: {virtual_path}")
            return False

        physical_path = self._get_physical_path(virtual_path)

        try:
            # 删除文件
            os.remove(physical_path)

            # 更新使用空间
            self.used_size -= self.files[virtual_path]["size"]
            del self.files[virtual_path]
            self._save_state()

            logger.info(f"删除虚拟文件: {virtual_path}")
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False

    def list_files(self, virtual_dir: str = "/") -> Dict[str, Any]:
        """
        列出目录下的文件

        Args:
            virtual_dir: 虚拟目录路径

        Returns:
            文件列表
        """
        result = {}
        for path, info in self.files.items():
            if path.startswith(virtual_dir) and path != virtual_dir:
                # 获取文件名
                rel_path = os.path.relpath(path, virtual_dir)
                parts = rel_path.split(os.path.sep)
                if len(parts) == 1:
                    result[parts[0]] = info
        return result

    def _get_physical_path(self, virtual_path: str) -> str:
        """将虚拟路径转换为物理路径"""
        # 移除开头的斜杠
        if virtual_path.startswith("/"):
            virtual_path = virtual_path[1:]

        # 替换Windows风格路径分隔符
        virtual_path = virtual_path.replace("\\", os.path.sep)

        # 构建物理路径
        return os.path.join(self.storage_path, virtual_path)