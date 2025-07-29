# android_libs/graphics/drawable.py
# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)
class Drawable:
    """模拟 android.graphics.drawable.Drawable 类"""

    def __init__(self, hardware_abstraction):
        self.hardware_abstraction = hardware_abstraction

    def draw(self, canvas):
        """在Canvas上绘制"""
        logger.info("Drawable.draw 方法被调用，但具体绘制逻辑由子类实现")


class ColorDrawable(Drawable):
    """模拟 android.graphics.drawable.ColorDrawable 类"""

    def __init__(self, hardware_abstraction, color):
        super().__init__(hardware_abstraction)
        self.color = color

    def draw(self, canvas):
        # 获取边界
        bounds = self.get_bounds()
        if bounds:
            left, top, right, bottom = bounds
            # 调用 canvas 的 draw_rect 方法绘制矩形
            canvas.draw_rect(left, top, right, bottom, self.color)
        else:
            logger.warning("未获取到有效的边界信息，无法绘制 ColorDrawable")

    def get_bounds(self):
        # 简单模拟边界信息
        return (0, 0, 100, 100)