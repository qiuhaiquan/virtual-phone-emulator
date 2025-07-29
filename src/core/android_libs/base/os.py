# android_libs/base/os.py
class Build:
    """ģ�� android.os.Build ��"""

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
    """ģ�� android.os.BatteryManager ��"""

    def __init__(self, hardware_abstraction):
        self.hardware_abstraction = hardware_abstraction

    def isCharging(self) -> bool:
        # ��Ӳ��������ȡʵ�ʳ��״̬
        return self.hardware_abstraction.get_battery_status().is_charging