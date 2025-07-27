# src/config.py
import os
import platform
from configparser import ConfigParser
from typing import Any, Dict, Optional


class Config:
    def __init__(self, config_file=None):
        self.config = ConfigParser()

        # 默认配置
        self.os = platform.system()
        self.default_config = {
            "storage": {
                "root_path": "",
                "windows_drive_letter": "G",
                "linux_mount_point": os.path.join(os.path.expanduser("~"), "virtual_phone_drive"),
                "macos_mount_point": os.path.join(os.path.expanduser("~"), "virtual_phone_drive")
            },
            "logging": {
                "level": "INFO"
            }
        }

        # 加载配置文件（如果存在）
        if config_file and os.path.exists(config_file):
            self.config.read(config_file)
        else:
            # 使用默认配置
            self.config.read_dict(self.default_config)

    def get_storage_path(self) -> str:
        """获取存储路径（根据操作系统）"""
        path = self.config.get("storage", "root_path", fallback="")
        if not path:
            if self.os == "Windows":
                path = os.path.join(os.environ["TEMP"], "virtual_phone_storage")
            elif self.os == "Linux":
                path = os.path.join(os.path.expanduser("~"), ".virtual_phone_storage")
            else:  # macOS
                path = os.path.join(os.path.expanduser("~"), "Library/Application Support/virtual_phone_storage")
        return path

    def get_drive_letter(self) -> str:
        """获取Windows盘符"""
        return self.config.get("storage", "windows_drive_letter", fallback="G")

    def to_dict(self) -> dict[str, Any]:
        """将配置转换为字典"""
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config.items(section))
        return config_dict

    # src/config.py
    import os
    import platform
    from configparser import ConfigParser
    from typing import Any, Dict, Optional

    class Config:
        def __init__(self, config_file: Optional[str] = None):
            self.config = ConfigParser()

            # 系统信息
            self.os = platform.system()

            # 默认配置
            self.default_config = {
                "storage": {
                    "root_path": "",
                    "windows_drive_letter": "G",
                    "linux_mount_point": os.path.join(os.path.expanduser("~"), "virtual_phone_drive"),
                    "macos_mount_point": os.path.join(os.path.expanduser("~"), "virtual_phone_drive")
                },
                "logging": {
                    "level": "INFO",
                    "log_file": os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "virtual_phone.log")
                },
                "hardware": {
                    "enable_network_emulation": "True",
                    "packet_loss_rate": "0.1",
                    "latency_ms": "50"
                },
                "ui": {
                    "theme": "light",
                    "window_width": "800",
                    "window_height": "600"
                }
            }

            # 加载配置文件（如果存在）
            if config_file and os.path.exists(config_file):
                self.config.read(config_file)
                # 合并默认配置（确保所有键都存在）
                for section, values in self.default_config.items():
                    if not self.config.has_section(section):
                        self.config.add_section(section)
                    for key, value in values.items():
                        if not self.config.has_option(section, key):
                            self.config.set(section, key, str(value))
            else:
                # 使用默认配置
                self.config.read_dict(self.default_config)

        def get_storage_path(self) -> str:
            """获取存储路径（根据操作系统）"""
            path = self.config.get("storage", "root_path", fallback="")
            if not path:
                if self.os == "Windows":
                    path = os.path.join(os.environ.get("TEMP", "/tmp"), "virtual_phone_storage")
                elif self.os == "Linux":
                    path = os.path.join(os.path.expanduser("~"), ".virtual_phone_storage")
                else:  # macOS
                    path = os.path.join(os.path.expanduser("~"), "Library/Application Support/virtual_phone_storage")
            return path

        def get_drive_letter(self) -> str:
            """获取Windows盘符"""
            return self.config.get("storage", "windows_drive_letter", fallback="G")

        def get_log_level(self) -> str:
            """获取日志级别"""
            return self.config.get("logging", "level", fallback="INFO").upper()

        def get_log_file(self) -> str:
            """获取日志文件路径"""
            return self.config.get("logging", "log_file", fallback="virtual_phone.log")

        def is_network_emulation_enabled(self) -> bool:
            """检查是否启用网络模拟"""
            return self.config.getboolean("hardware", "enable_network_emulation", fallback=True)

        def get_packet_loss_rate(self) -> float:
            """获取网络丢包率"""
            return self.config.getfloat("hardware", "packet_loss_rate", fallback=0.1)

        def get_latency_ms(self) -> int:
            """获取网络延迟（毫秒）"""
            return self.config.getint("hardware", "latency_ms", fallback=50)

        def get_ui_theme(self) -> str:
            """获取UI主题"""
            return self.config.get("ui", "theme", fallback="light")

        def get_window_size(self) -> Dict[str, int]:
            """获取窗口尺寸"""
            return {
                "width": self.config.getint("ui", "window_width", fallback=800),
                "height": self.config.getint("ui", "window_height", fallback=600)
            }

        def to_dict(self) -> Dict[str, Dict[str, Any]]:
            """将配置转换为字典"""
            config_dict = {}
            for section in self.config.sections():
                config_dict[section] = dict(self.config.items(section))

                # 转换布尔值和数值类型
                for key, value in config_dict[section].items():
                    if value.lower() == "true":
                        config_dict[section][key] = True
                    elif value.lower() == "false":
                        config_dict[section][key] = False
                    elif value.replace('.', '', 1).isdigit():
                        try:
                            config_dict[section][key] = int(value)
                        except ValueError:
                            config_dict[section][key] = float(value)
            return config_dict

        def save(self, config_file: str) -> None:
            """保存配置到文件"""
            with open(config_file, 'w') as f:
                self.config.write(f)