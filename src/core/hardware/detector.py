# src/core/hardware/detector.py
import os
import platform
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HardwareDetector:
    """负责检测和识别计算机硬件"""

    def __init__(self):
        self.os = platform.system()
        self.detected_hardware = {}

    def detect_all_hardware(self) -> Dict[str, Any]:
        """检测并返回所有可用硬件信息"""
        self.detect_cpu()
        self.detect_memory()
        self.detect_storage()
        self.detect_network()
        self.detect_display()
        self.detect_camera()
        self.detect_audio()

        return self.detected_hardware

    def detect_cpu(self) -> None:
        """检测CPU信息"""
        try:
            if self.os == "Windows":
                output = subprocess.check_output("wmic cpu get Name", shell=True).decode()
                self.detected_hardware["cpu"] = output.strip().split("\n")[-1].strip()
            elif self.os == "Linux":
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            self.detected_hardware["cpu"] = line.split(":")[1].strip()
                            break
            elif self.os == "Darwin":  # macOS
                output = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode()
                self.detected_hardware["cpu"] = output.strip()
        except Exception as e:
            logger.error(f"检测CPU失败: {e}")
            self.detected_hardware["cpu"] = "未知"

    def detect_memory(self) -> None:
        """检测内存信息"""
        try:
            if self.os == "Windows":
                output = subprocess.check_output("wmic OS get TotalVisibleMemorySize", shell=True).decode()
                mem_kb = int(output.strip().split("\n")[-1].strip())
                self.detected_hardware["memory"] = f"{mem_kb / (1024 * 1024):.2f} GB"
            elif self.os == "Linux":
                with open("/proc/meminfo") as f:
                    for line in f:
                        if "MemTotal" in line:
                            mem_kb = int(line.split()[1])
                            self.detected_hardware["memory"] = f"{mem_kb / (1024 * 1024):.2f} GB"
                            break
            elif self.os == "Darwin":
                output = subprocess.check_output("sysctl -n hw.memsize", shell=True).decode()
                mem_bytes = int(output.strip())
                self.detected_hardware["memory"] = f"{mem_bytes / (1024 ** 3):.2f} GB"
        except Exception as e:
            logger.error(f"检测内存失败: {e}")
            self.detected_hardware["memory"] = "未知"

    def detect_storage(self) -> None:
        """检测存储设备信息"""
        try:
            if self.os == "Windows":
                output = subprocess.check_output("wmic logicaldisk where drivetype=3 get deviceid, freespace, size",
                                                 shell=True).decode()
                lines = output.strip().split("\n")[1:]  # 跳过标题行
                drives = []
                for line in lines:
                    if line.strip():
                        parts = line.strip().split()
                        drive = {
                            "device": parts[0],
                            "size": f"{int(parts[-1]) / (1024 ** 3):.2f} GB",
                            "free": f"{int(parts[-2]) / (1024 ** 3):.2f} GB"
                        }
                        drives.append(drive)
                self.detected_hardware["storage"] = drives
            elif self.os == "Linux":
                output = subprocess.check_output("df -h /", shell=True).decode()
                lines = output.strip().split("\n")[1:]  # 跳过标题行
                if lines:
                    parts = lines[0].split()
                    self.detected_hardware["storage"] = {
                        "device": parts[0],
                        "size": parts[1],
                        "used": parts[2],
                        "free": parts[3]
                    }
            elif self.os == "Darwin":
                output = subprocess.check_output("df -h /", shell=True).decode()
                lines = output.strip().split("\n")[1:]  # 跳过标题行
                if lines:
                    parts = lines[0].split()
                    self.detected_hardware["storage"] = {
                        "device": parts[0],
                        "size": parts[1],
                        "used": parts[2],
                        "free": parts[3]
                    }
        except Exception as e:
            logger.error(f"检测存储失败: {e}")
            self.detected_hardware["storage"] = "未知"

    def detect_network(self) -> None:
        """检测网络设备信息"""
        try:
            if self.os == "Windows":
                output = subprocess.check_output("ipconfig /all", shell=True).decode()
                self.detected_hardware["network"] = output.strip()
            elif self.os == "Linux":
                output = subprocess.check_output("ifconfig", shell=True).decode()
                self.detected_hardware["network"] = output.strip()
            elif self.os == "Darwin":
                output = subprocess.check_output("ifconfig", shell=True).decode()
                self.detected_hardware["network"] = output.strip()
        except Exception as e:
            logger.error(f"检测网络失败: {e}")
            self.detected_hardware["network"] = "未知"

    def detect_display(self) -> None:
        """检测显示设备信息"""
        try:
            if self.os == "Windows":
                output = subprocess.check_output("wmic path win32_VideoController get Name", shell=True).decode()
                self.detected_hardware["display"] = output.strip().split("\n")[-1].strip()
            elif self.os == "Linux":
                output = subprocess.check_output("lspci | grep VGA", shell=True).decode()
                self.detected_hardware["display"] = output.strip()
            elif self.os == "Darwin":
                output = subprocess.check_output("system_profiler SPDisplaysDataType", shell=True).decode()
                self.detected_hardware["display"] = output.strip()
        except Exception as e:
            logger.error(f"检测显示设备失败: {e}")
            self.detected_hardware["display"] = "未知"

    def detect_camera(self) -> None:
        """检测摄像头设备"""
        try:
            if self.os == "Windows":
                # 简单检测，实际可能需要更复杂的方法
                output = subprocess.check_output("devcon find *camera*", shell=True).decode()
                self.detected_hardware["camera"] = bool(output.strip())
            elif self.os == "Linux":
                camera_count = len(os.listdir("/dev/") if os.path.exists("/dev/") else [])
                self.detected_hardware["camera"] = camera_count > 0
            elif self.os == "Darwin":
                # macOS上检测摄像头更复杂，这里简化处理
                self.detected_hardware["camera"] = True  # 假设macOS设备通常有摄像头
        except Exception as e:
            logger.error(f"检测摄像头失败: {e}")
            self.detected_hardware["camera"] = False

    def detect_audio(self) -> None:
        """检测音频设备"""
        try:
            if self.os == "Windows":
                output = subprocess.check_output("wmic path win32_SoundDevice get Name", shell=True).decode()
                self.detected_hardware["audio"] = output.strip().split("\n")[-1].strip()
            elif self.os == "Linux":
                output = subprocess.check_output("aplay -l", shell=True).decode()
                self.detected_hardware["audio"] = bool(output.strip())
            elif self.os == "Darwin":
                output = subprocess.check_output("system_profiler SPAudioDataType", shell=True).decode()
                self.detected_hardware["audio"] = output.strip()
        except Exception as e:
            logger.error(f"检测音频设备失败: {e}")
            self.detected_hardware["audio"] = "未知"