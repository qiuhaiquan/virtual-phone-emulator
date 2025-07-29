# android_libs/base/os.py
class Build:
    """模拟 android.os.Build 类"""

    def __init__(self, hardware_abstraction):
        self.hardware_abstraction = hardware_abstraction

    @staticmethod
    def getDevice() -> str:
        return "DoubaoVirtualDevice"

    @staticmethod
    def getModel() -> str:
        return "Doubao Virtual Phone"


# android_libs/hardware/battery.py
class BatteryManager:
    """模拟 android.os.BatteryManager 类"""

    def __init__(self, hardware_abstraction):
        self.hardware_abstraction = hardware_abstraction

    def isCharging(self) -> bool:
        # 从硬件抽象层获取实际充电状态
        return self.hardware_abstraction.get_battery_status().is_charging