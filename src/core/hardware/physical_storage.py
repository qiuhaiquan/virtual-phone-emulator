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

        # ��ƽ̨Ĭ�ϴ洢·��
        if not root_path:
            if self.os == "Windows":
                root_path = os.path.join(os.environ["TEMP"], "virtual_phone_storage")
            elif self.os == "Linux":
                root_path = os.path.join(os.path.expanduser("~"), ".virtual_phone_storage")
            else:  # macOS
                root_path = os.path.join(os.path.expanduser("~"), "Library/Application Support/virtual_phone_storage")

        self.root_path = root_path
        os.makedirs(self.root_path, exist_ok=True)
        logger.info(f"����洢·��: {self.root_path}")

        # ����Windows�ϳ��Թ����̷�
        if self.os == "Windows":
            self._mount_as_drive()

    def _mount_as_drive(self) -> bool:
        """���ݲ���ϵͳѡ����ط�ʽ"""
        if self.os == "Windows":
            return self._mount_windows_drive()
        elif self.os == "Linux":
            return self._mount_linux_drive()
        else:  # macOS
            return self._mount_macos_drive()

    def _mount_windows_drive(self) -> bool:
        """��Windows�Ϲ���Ŀ¼Ϊ����������"""
        try:
            # ����̷��Ƿ��ѱ�ʹ��
            if os.system(f"if exist {self.drive_letter}:\\ echo exists") == 0:
                logger.warning(f"�̷� {self.drive_letter}: �ѱ�ʹ�ã��޷�����")
                return False

            subprocess.run(
                f"subst {self.drive_letter}: {self.root_path}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"�ɹ��� {self.root_path} ����Ϊ {self.drive_letter}:")
            return True
        except Exception as e:
            logger.error(f"�����̷�ʧ��: {e}")
            return False

    def _mount_linux_drive(self) -> bool:
        """��Linux�ϴ������ص㣨ʹ�÷�������ģ�⣩"""
        try:
            # �����û���Ŀ¼�µ�����
            link_path = os.path.join(os.path.expanduser("~"), "virtual_phone_drive")
            if os.path.exists(link_path):
                if not os.path.islink(link_path):
                    logger.warning(f"{link_path} �Ѵ����Ҳ��Ƿ�������")
                    return False
                os.unlink(link_path)

            os.symlink(self.root_path, link_path)
            logger.info(f"���� {link_path} ����ָ�� {self.root_path} �ķ�������")
            return True
        except Exception as e:
            logger.error(f"������������ʧ��: {e}")
            return False

    def _mount_macos_drive(self) -> bool:
        """��macOS�ϴ������ص㣨ʹ�÷�������ģ�⣩"""
        try:
            # �����û���Ŀ¼�µ�����
            link_path = os.path.join(os.path.expanduser("~"), "virtual_phone_drive")
            if os.path.exists(link_path):
                if not os.path.islink(link_path):
                    logger.warning(f"{link_path} �Ѵ����Ҳ��Ƿ�������")
                    return False
                os.unlink(link_path)

            os.symlink(self.root_path, link_path)
            logger.info(f"���� {link_path} ����ָ�� {self.root_path} �ķ�������")
            return True
        except Exception as e:
            logger.error(f"������������ʧ��: {e}")
            return False

    def unmount_drive(self) -> bool:
        """���ݲ���ϵͳж�ع��ص�"""
        if self.os == "Windows":
            return self._unmount_windows_drive()
        elif self.os == "Linux":
            return self._unmount_linux_drive()
        else:  # macOS
            return self._unmount_macos_drive()

    def _unmount_windows_drive(self) -> bool:
        """ж��Windows����������"""
        try:
            subprocess.run(
                f"subst {self.drive_letter}: /D",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"�ɹ�ж���̷� {self.drive_letter}:")
            return True
        except Exception as e:
            logger.error(f"ж���̷�ʧ��: {e}")
            return False

    def _unmount_linux_drive(self) -> bool:
        """ɾ��Linux��������"""
        try:
            link_path = os.path.join(os.path.expanduser("~"), "virtual_phone_drive")
            if os.path.islink(link_path):
                os.unlink(link_path)
                logger.info(f"��ɾ���������� {link_path}")
            return True
        except Exception as e:
            logger.error(f"ɾ����������ʧ��: {e}")
            return False

    def _unmount_macos_drive(self) -> bool:
        """ɾ��macOS��������"""
        return self._unmount_linux_drive()  # ��Linuxʵ����ͬ

    def create_file(self, path: str, content: str) -> bool:
        """�����ļ�"""
        try:
            full_path = os.path.join(self.root_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"�ļ������ɹ�: {full_path}")
            return True
        except Exception as e:
            logger.error(f"�����ļ�ʧ�� {path}: {e}")
            return False

    def read_file(self, path: str) -> str:
        """��ȡ�ļ�"""
        try:
            full_path = os.path.join(self.root_path, path)
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"��ȡ�ļ�ʧ�� {path}: {e}")
            return None

    def list_files(self, directory: str = "") -> list:
        """�г�Ŀ¼�µ������ļ����ļ���"""
        try:
            full_path = os.path.join(self.root_path, directory)
            if not os.path.exists(full_path):
                return []
            return os.listdir(full_path)
        except Exception as e:
            logger.error(f"�г��ļ�ʧ��: {e}")
            return []

    def delete_file(self, path: str) -> bool:
        """ɾ���ļ�"""
        try:
            full_path = os.path.join(self.root_path, path)
            if os.path.isfile(full_path):
                os.remove(full_path)
                logger.info(f"�ļ�ɾ���ɹ�: {full_path}")
                return True
            logger.warning(f"�ļ�������: {full_path}")
            return False
        except Exception as e:
            logger.error(f"ɾ���ļ�ʧ�� {path}: {e}")
            return False