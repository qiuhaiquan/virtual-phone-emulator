# src/ui/console_ui.py
import logging
from ...core import VirtualPhone

logger = logging.getLogger(__name__)


class ConsoleUI:
    """虚拟手机控制台界面"""

    def __init__(self):
        self.virtual_phone = VirtualPhone()

    def start(self) -> None:
        """启动用户界面"""
        print("===== 虚拟手机模拟器 =====")

        try:
            # 启动虚拟手机
            self.virtual_phone.start()

            # 显示硬件信息
            self._display_hardware_info()

            # 主循环
            while True:
                self._display_menu()
                choice = input("请选择操作 (1-4): ")

                if choice == "1":
                    self._run_apk()
                elif choice == "2":
                    self._display_hardware_info()
                elif choice == "3":
                    print("正在退出...")
                    break
                else:
                    print("无效选择，请重试")

        except KeyboardInterrupt:
            print("\n用户中断，正在退出...")
        finally:
            # 确保虚拟手机停止
            self.virtual_phone.stop()
            print("虚拟手机已关闭")

    def _manage_storage(self) -> None:
        """管理虚拟存储"""
        storage = self.virtual_phone.hardware_abstraction.get_storage()
        if not storage:
            print("虚拟存储不可用")
            return

        while True:
            print("\n--- 虚拟存储管理 ---")
            info = storage.get_info()
            print(f"总容量: {info['total_size'] / (1024 ** 3):.2f} GB")
            print(f"已使用: {info['used_size'] / (1024 ** 3):.2f} GB")
            print(f"可用空间: {info['free_size'] / (1024 ** 3):.2f} GB")
            print(f"文件数量: {info['file_count']}")

            print("\n1. 列出文件")
            print("2. 创建文件")
            print("3. 删除文件")
            print("4. 返回")

            choice = input("请选择操作 (1-4): ")

            if choice == "1":
                dir_path = input("请输入目录路径 (默认为/): ")
                if not dir_path:
                    dir_path = "/"
                files = storage.list_files(dir_path)
                if not files:
                    print("目录为空")
                else:
                    print(f"目录 {dir_path} 下的文件:")
                    for name, info in files.items():
                        print(f"- {name} ({info['size'] / (1024):.2f} KB)")

            elif choice == "2":
                file_path = input("请输入文件路径: ")
                size_mb = float(input("请输入文件大小 (MB): "))
                size_bytes = int(size_mb * 1024 * 1024)

                if storage.create_file(file_path, size_bytes):
                    print(f"文件 {file_path} 创建成功")
                else:
                    print(f"创建文件失败")

            elif choice == "3":
                file_path = input("请输入要删除的文件路径: ")
                if storage.delete_file(file_path):
                    print(f"文件 {file_path} 已删除")
                else:
                    print(f"删除文件失败")

            elif choice == "4":
                break

            else:
                print("无效选择，请重试")

    def _display_menu(self) -> None:
        """显示主菜单"""
        print("\n--- 主菜单 ---")
        print("1. 运行APK文件")
        print("2. 查看硬件信息")
        print("3. 退出")

    def _display_hardware_info(self) -> None:
        """显示检测到的硬件信息"""
        print("\n--- 检测到的硬件信息 ---")
        hardware_info = self.virtual_phone.get_hardware_info()

        for hardware, info in hardware_info.items():
            print(f"{hardware.capitalize()}: {info}")

    def _run_apk(self) -> None:
        """运行APK文件"""
        apk_path = input("请输入APK文件路径 (或拖放文件到窗口): ").strip()

        if not apk_path:
            print("路径不能为空")
            return

        if not apk_path.startswith('"') and ' ' in apk_path:
            # 如果路径包含空格但没有引号，则添加引号
            apk_path = f'"{apk_path}"'

        print(f"正在运行APK: {apk_path}")
        self.virtual_phone.run_apk(apk_path)