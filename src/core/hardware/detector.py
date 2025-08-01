"""负责检测和识别计算机硬件"""
import platform
import subprocess
import logging
import os

logger = logging.getLogger(__name__)

class HardwareDetector:
    """负责检测和识别计算机硬件"""

    def __init__(self):
        self.os = platform.system()
        self.detected_hardware = {}

    def detect_all_hardware(self) -> dict:
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
                # 使用 PowerShell 命令获取 CPU 信息
                output = subprocess.check_output(["powershell", "Get-WmiObject -Class Win32_Processor | Select-Object -ExpandProperty Name"], shell=False).decode()
                self.detected_hardware["cpu"] = output.strip()
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
                # 使用 PowerShell 命令获取内存信息
                output = subprocess.check_output(["powershell", "Get-WmiObject -Class Win32_OperatingSystem | Select-Object -ExpandProperty TotalVisibleMemorySize"], shell=False).decode()
                mem_kb = int(output.strip())
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
                # 使用 PowerShell 命令获取存储设备信息
                output = subprocess.check_output(["powershell", "Get-WmiObject -Class Win32_LogicalDisk -Filter \"DriveType=3\" | Select-Object DeviceID, FreeSpace, Size | Format-Table -HideTableHeaders"], shell=False).decode()
                lines = output.strip().split("\n")
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

    def detect_display(self) -> None:
        """检测显示设备信息"""
        try:
            if self.os == "Windows":
                # 使用 PowerShell 命令获取显示设备信息
                output = subprocess.check_output(["powershell", "Get-WmiObject -Class Win32_VideoController | Select-Object -ExpandProperty Name"], shell=False).decode()
                self.detected_hardware["display"] = output.strip()
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
                # Windows 下 wmic 输出为 GBK 编码
                try:
                    # 使用 PowerShell 获取音频设备信息
                    output = subprocess.check_output(
                        [
                            "powershell",
                            "-Command",
                            "(Get-CimInstance -ClassName Win32_SoundDevice).Name"
                        ],
                        shell=False,  # 使用 shell=False 更安全
                        stderr=subprocess.STDOUT  # 捕获错误输出
                    ).decode('gbk', errors='ignore')

                    # 提取有效行（忽略空行）
                    lines = [line.strip() for line in output.splitlines() if line.strip()]
                    self.detected_hardware["audio"] = lines[0] if lines else "未知"

                except subprocess.CalledProcessError as e:
                    # 处理命令执行失败的情况
                    logger.error(f"检测音频设备失败: {e.output.decode('gbk', errors='ignore')}")
                    self.detected_hardware["audio"] = "未知"
                except Exception as e:
                    # 处理其他异常
                    logger.error(f"检测音频设备时发生未知错误: {e}")
                    self.detected_hardware["audio"] = "未知"
            elif self.os == "Linux":
                output = subprocess.check_output("aplay -l", shell=True).decode('utf-8', errors='ignore')
                self.detected_hardware["audio"] = "存在" if output.strip() else "未知"
            elif self.os == "Darwin":
                output = subprocess.check_output("system_profiler SPAudioDataType", shell=True).decode('utf-8', errors='ignore')
                self.detected_hardware["audio"] = output.strip()
        except Exception as e:
            logger.error(f"检测音频设备失败: {e}")
            self.detected_hardware["audio"] = "未知"

    def detect_network(self) -> None:
        """检测网络设备信息"""
        try:
            if self.os == "Windows":
                output = subprocess.check_output("ipconfig /all", shell=True)
                output = output.decode('gbk', errors='ignore')  # Windows默认编码
            elif self.os == "Linux":
                output = subprocess.check_output("ip addr show", shell=True)
                output = output.decode('utf-8', errors='ignore')
            else:  # macOS
                output = subprocess.check_output("ifconfig", shell=True)
                output = output.decode('utf-8', errors='ignore')

            self.detected_hardware["network"] = output.strip()
        except Exception as e:
            logger.error(f"检测网络失败: {e}")
            self.detected_hardware["network"] = "未知"
