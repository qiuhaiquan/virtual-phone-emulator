# tests/test_hardware.py
import unittest
from src.core.hardware.detector import HardwareDetector


class TestHardwareDetector(unittest.TestCase):

    def setUp(self):
        self.detector = HardwareDetector()

    def test_detect_cpu(self):
        self.detector.detect_cpu()
        self.assertIn("cpu", self.detector.detected_hardware)
        self.assertIsNotNone(self.detector.detected_hardware["cpu"])

    def test_detect_memory(self):
        self.detector.detect_memory()
        self.assertIn("memory", self.detector.detected_hardware)
        self.assertIsNotNone(self.detector.detected_hardware["memory"])

    def test_detect_storage(self):
        self.detector.detect_storage()
        self.assertIn("storage", self.detector.detected_hardware)
        self.assertIsNotNone(self.detector.detected_hardware["storage"])

    def test_detect_network(self):
        self.detector.detect_network()
        self.assertIn("network", self.detector.detected_hardware)
        self.assertIsNotNone(self.detector.detected_hardware["network"])

    def test_detect_display(self):
        self.detector.detect_display()
        self.assertIn("display", self.detector.detected_hardware)
        self.assertIsNotNone(self.detector.detected_hardware["display"])

    def test_detect_camera(self):
        self.detector.detect_camera()
        self.assertIn("camera", self.detector.detected_hardware)
        self.assertIsNotNone(self.detector.detected_hardware["camera"])

    def test_detect_audio(self):
        self.detector.detect_audio()
        self.assertIn("audio", self.detector.detected_hardware)
        self.assertIsNotNone(self.detector.detected_hardware["audio"])


if __name__ == '__main__':
    unittest.main()