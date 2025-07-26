# src/__main__.py
import argparse
import logging
from ext.ui.console_ui import ConsoleUI
from ext.ui.gui_ui import run_gui
import os
import sys
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
        ]
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='虚拟手机模拟器')
    parser.add_argument('-v', '--verbose', action='store_true', help='启用详细日志')
    parser.add_argument('-g', '--gui', action='store_true', help='使用图形界面')
    args = parser.parse_args()

    # 设置日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)

    # 选择界面类型
    if args.gui:
        # 运行图形界面
        run_gui()
    else:
        # 运行控制台界面
        ui = ConsoleUI()
        ui.start()


if __name__ == "__main__":
    main()