# src/ui/gui_ui.py
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QFileDialog, QWidget, QLabel, QDialog, QGroupBox, QListWidget,
                             QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt
from src.core.virtual_phone import VirtualPhone

logger = logging.getLogger(__name__)


class GUIUI(QMainWindow):
    """虚拟手机图形界面"""

    def __init__(self):
        super().__init__()
        self.virtual_phone = VirtualPhone()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("虚拟手机模拟器")
        self.setGeometry(100, 100, 800, 600)

        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 顶部状态区域
        status_layout = QHBoxLayout()
        self.status_label = QLabel("虚拟手机已停止")
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)

        # 硬件信息区域
        hardware_group = QWidget()
        hardware_layout = QVBoxLayout(hardware_group)
        hardware_label = QLabel("检测到的硬件信息:")
        hardware_layout.addWidget(hardware_label)

        self.hardware_info = QTextEdit()
        self.hardware_info.setReadOnly(True)
        hardware_layout.addWidget(self.hardware_info)

        main_layout.addWidget(hardware_group)

        # 控制按钮区域
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("启动虚拟手机")
        self.start_button.clicked.connect(self.start_virtual_phone)
        button_layout.addWidget(self.start_button)

        self.apk_button = QPushButton("选择并运行APK")
        self.apk_button.clicked.connect(self.select_and_run_apk)
        self.apk_button.setEnabled(False)
        button_layout.addWidget(self.apk_button)

        self.refresh_button = QPushButton("刷新硬件信息")
        self.refresh_button.clicked.connect(self.refresh_hardware_info)
        button_layout.addWidget(self.refresh_button)

        self.storage_button = QPushButton("管理虚拟存储")
        self.storage_button.clicked.connect(self.manage_storage)
        button_layout.addWidget(self.storage_button)

        main_layout.addLayout(button_layout)

        # 日志区域
        log_label = QLabel("运行日志:")
        main_layout.addWidget(log_label)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        # 配置日志处理器
        log_handler = TextEditHandler(self.log_area)
        logger.addHandler(log_handler)
        logger.setLevel(logging.INFO)

        # 显示窗口
        self.show()

    def start_virtual_phone(self):
        """启动虚拟手机"""
        self.log_area.clear()
        logger.info("正在启动虚拟手机...")

        try:
            self.virtual_phone.start()
            self.status_label.setText("虚拟手机已启动")
            self.apk_button.setEnabled(True)
            self.refresh_hardware_info()
            logger.info("虚拟手机启动成功")
        except Exception as e:
            logger.error(f"启动虚拟手机失败: {e}")

    def manage_storage(self):
        """打开存储管理对话框"""
        if not self.virtual_phone.running:
            logger.error("虚拟手机未启动，请先启动虚拟手机")
            return

        storage = self.virtual_phone.hardware_abstraction.get_storage()
        if not storage:
            logger.error("虚拟存储不可用")
            return

        # 创建存储管理对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("虚拟存储管理")
        dialog.setMinimumWidth(600)

        layout = QVBoxLayout(dialog)

        # 显示存储信息
        info_group = QGroupBox("存储信息")
        info_layout = QVBoxLayout(info_group)

        info = storage.get_info()
        self.storage_info = QTextEdit()
        self.storage_info.setReadOnly(True)
        self.storage_info.setText(f"""
        总容量: {info['total_size'] / (1024 ** 3):.2f} GB
        已使用: {info['used_size'] / (1024 ** 3):.2f} GB
        可用空间: {info['free_size'] / (1024 ** 3):.2f} GB
        文件数量: {info['file_count']}
        """)

        info_layout.addWidget(self.storage_info)
        layout.addWidget(info_group)

        # 文件列表区域
        file_group = QGroupBox("文件列表")
        file_layout = QVBoxLayout(file_group)

        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)

        refresh_button = QPushButton("刷新文件列表")
        refresh_button.clicked.connect(lambda: self.refresh_file_list(storage))
        file_layout.addWidget(refresh_button)

        layout.addWidget(file_group)

        # 操作按钮
        button_layout = QHBoxLayout()

        create_button = QPushButton("创建文件")
        create_button.clicked.connect(lambda: self.create_file(storage))
        button_layout.addWidget(create_button)

        delete_button = QPushButton("删除文件")
        delete_button.clicked.connect(lambda: self.delete_file(storage))
        button_layout.addWidget(delete_button)

        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        # 初始化文件列表
        self.refresh_file_list(storage)

        dialog.exec_()

    def refresh_file_list(self, storage):
        """刷新文件列表"""
        self.file_list.clear()
        files = storage.list_files("/")
        for name, info in files.items():
            size_str = f"{info['size'] / (1024):.2f} KB"
            self.file_list.addItem(f"{name} ({size_str})")

    def create_file(self, storage):
        """创建新文件"""
        file_path, ok = QInputDialog.getText(self, "创建文件", "文件路径:")
        if not ok or not file_path:
            return

        size, ok = QInputDialog.getDouble(self, "创建文件", "文件大小 (MB):", 1.0, 0.1, 1024.0, 1)
        if not ok:
            return

        size_bytes = int(size * 1024 * 1024)

        if storage.create_file(file_path, size_bytes):
            logger.info(f"文件 {file_path} 创建成功")
            self.refresh_file_list(storage)
            self.update_storage_info(storage)
        else:
            logger.error(f"创建文件失败")

    def delete_file(self, storage):
        """删除选中的文件"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            logger.warning("请先选择要删除的文件")
            return

        file_name = selected_items[0].text().split(" (")[0]

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除文件 '{file_name}' 吗?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if storage.delete_file(file_name):
                logger.info(f"文件 {file_name} 已删除")
                self.refresh_file_list(storage)
                self.update_storage_info(storage)
            else:
                logger.error(f"删除文件失败")

    def update_storage_info(self, storage):
        """更新存储信息显示"""
        info = storage.get_info()
        self.storage_info.setText(f"""
        总容量: {info['total_size'] / (1024 ** 3):.2f} GB
        已使用: {info['used_size'] / (1024 ** 3):.2f} GB
        可用空间: {info['free_size'] / (1024 ** 3):.2f} GB
        文件数量: {info['file_count']}
        """)

    def refresh_hardware_info(self):
        """刷新硬件信息显示"""
        hardware_info = self.virtual_phone.get_hardware_info()
        info_text = ""

        for hardware, info in hardware_info.items():
            info_text += f"{hardware.capitalize()}: {info}\n"

        self.hardware_info.setText(info_text)

    def select_and_run_apk(self):
        """选择并运行APK文件"""
        if not self.virtual_phone.running:
            logger.error("虚拟手机未启动，请先启动虚拟手机")
            return

        apk_path, _ = QFileDialog.getOpenFileName(
            self, "选择APK文件", "", "APK Files (*.apk);;All Files (*)"
        )

        if apk_path:
            logger.info(f"正在运行APK: {apk_path}")
            self.virtual_phone.run_apk(apk_path)


class TextEditHandler(logging.Handler):
    """自定义日志处理器，将日志输出到QTextEdit控件"""

    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)
        # 滚动到底部
        self.text_edit.verticalScrollBar().setValue(
            self.text_edit.verticalScrollBar().maximum()
        )


def run_gui():
    """运行图形界面应用"""
    app = QApplication(sys.argv)
    window = GUIUI()
    sys.exit(app.exec_())