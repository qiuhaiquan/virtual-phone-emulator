# src/config.py
import os
import platform
from configparser import ConfigParser
from typing import Any, Dict, Optional


class Config:
    def __init__(self, config_file=None):
        self.config = ConfigParser()

        # Ĭ������
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

        # ���������ļ���������ڣ�
        if config_file and os.path.exists(config_file):
            self.config.read(config_file)
        else:
            # ʹ��Ĭ������
            self.config.read_dict(self.default_config)

    def get_storage_path(self) -> str:
        """��ȡ�洢·�������ݲ���ϵͳ��"""
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
        """��ȡWindows�̷�"""
        return self.config.get("storage", "windows_drive_letter", fallback="G")

    def to_dict(self) -> dict[str, Any]:
        """������ת��Ϊ�ֵ�"""
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

            # ϵͳ��Ϣ
            self.os = platform.system()

            # Ĭ������
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

            # ���������ļ���������ڣ�
            if config_file and os.path.exists(config_file):
                self.config.read(config_file)
                # �ϲ�Ĭ�����ã�ȷ�����м������ڣ�
                for section, values in self.default_config.items():
                    if not self.config.has_section(section):
                        self.config.add_section(section)
                    for key, value in values.items():
                        if not self.config.has_option(section, key):
                            self.config.set(section, key, str(value))
            else:
                # ʹ��Ĭ������
                self.config.read_dict(self.default_config)

        def get_storage_path(self) -> str:
            """��ȡ�洢·�������ݲ���ϵͳ��"""
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
            """��ȡWindows�̷�"""
            return self.config.get("storage", "windows_drive_letter", fallback="G")

        def get_log_level(self) -> str:
            """��ȡ��־����"""
            return self.config.get("logging", "level", fallback="INFO").upper()

        def get_log_file(self) -> str:
            """��ȡ��־�ļ�·��"""
            return self.config.get("logging", "log_file", fallback="virtual_phone.log")

        def is_network_emulation_enabled(self) -> bool:
            """����Ƿ���������ģ��"""
            return self.config.getboolean("hardware", "enable_network_emulation", fallback=True)

        def get_packet_loss_rate(self) -> float:
            """��ȡ���綪����"""
            return self.config.getfloat("hardware", "packet_loss_rate", fallback=0.1)

        def get_latency_ms(self) -> int:
            """��ȡ�����ӳ٣����룩"""
            return self.config.getint("hardware", "latency_ms", fallback=50)

        def get_ui_theme(self) -> str:
            """��ȡUI����"""
            return self.config.get("ui", "theme", fallback="light")

        def get_window_size(self) -> Dict[str, int]:
            """��ȡ���ڳߴ�"""
            return {
                "width": self.config.getint("ui", "window_width", fallback=800),
                "height": self.config.getint("ui", "window_height", fallback=600)
            }

        def to_dict(self) -> Dict[str, Dict[str, Any]]:
            """������ת��Ϊ�ֵ�"""
            config_dict = {}
            for section in self.config.sections():
                config_dict[section] = dict(self.config.items(section))

                # ת������ֵ����ֵ����
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
            """�������õ��ļ�"""
            with open(config_file, 'w') as f:
                self.config.write(f)