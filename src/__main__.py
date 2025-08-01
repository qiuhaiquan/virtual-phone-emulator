# src/__main__.py
import argparse
import atexit
import logging
from ext.ui.console_ui import ConsoleUI
import os
import sys

from src.config import Config
from src.core.dalvik.android_runtime import AndroidRuntime
from src.core.hardware.abstraction import HardwareAbstractionLayer

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def setup_logging(level=logging.INFO):
    """配置日志"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("virtual_phone.log"),
            logging.StreamHandler()
        ],
    )


"""主函数"""

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='虚拟手机模拟器')
    parser.add_argument('-v', '--verbose', action='store_true', help='启用详细日志')
    parser.add_argument('-g', '--gui', action='store_true', help='使用图形界面')
    args = parser.parse_args()
    config = Config().to_dict()
    hardware = HardwareAbstractionLayer(config)
    runtime = AndroidRuntime(hardware, "src/core/android_libs.zip")
    atexit.register(hardware.cleanup)

    # 设置日志级别
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    setup_logging(log_level)

    # 选择界面类型
    from src.ext.ui.console_ui import ConsoleUI
    from src.ext.ui.gui_ui import GUIUI,run_gui

    if args.gui:
        # 运行图形界面
        run_gui()
    else:
        # 运行控制台界面
        ui = ConsoleUI()
        ui.start()

if __name__ == "__main__":
    main()