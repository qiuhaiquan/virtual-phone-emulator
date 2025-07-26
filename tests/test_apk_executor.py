# tests/test_apk_executor.py
import unittest
import os
from unittest.mock import Mock
from src.core.apk.python_apk_loader import PythonAPKLoader


class TestAPKExecutor(unittest.TestCase):

    def setUp(self):
        # 创建模拟的硬件抽象层
        self.hardware_abstraction = Mock()

        # 创建一个临时APK文件用于测试
        self.temp_apk = "temp_test.apk"
        with open(self.temp_apk, 'w') as f:
            f.write("This is a test APK file")

    def tearDown(self):
        # 删除临时文件
        if os.path.exists(self.temp_apk):
            os.remove(self.temp_apk)

    def test_load_apk(self):
        loader = PythonAPKLoader(self.temp_apk, self.hardware_abstraction)
        result = loader.load()
        self.assertTrue(result)

    def test_run_apk(self):
        loader = PythonAPKLoader(self.temp_apk, self.hardware_abstraction)
        loader.load()

        # 测试运行（模拟）
        try:
            loader.run()
            self.assertTrue(True)  # 如果没有异常，测试通过
        except Exception as e:
            self.fail(f"运行APK时发生异常: {e}")


if __name__ == '__main__':
    unittest.main()