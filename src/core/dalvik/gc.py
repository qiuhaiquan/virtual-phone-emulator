# src/core/dalvik/gc.py
import logging
import time
from typing import Dict, Any, Set

logger = logging.getLogger(__name__)


class GarbageCollector:
    """标记-清除垃圾回收器"""

    def __init__(self, vm):
        self.vm = vm
        self.heap_size = 1024 * 1024  # 1MB堆大小
        self.used_heap = 0
        self.gc_threshold = 0.7  # 堆使用率达到70%时触发GC
        self.gc_count = 0
        self.last_gc_time = 0

    def collect_if_needed(self) -> None:
        """根据需要执行垃圾回收"""
        if self.used_heap / self.heap_size >= self.gc_threshold:
            logger.info(f"触发垃圾回收: 堆使用率 {self.used_heap / self.heap_size:.2%}")
            self.collect()

    def collect(self) -> None:
        """执行垃圾回收"""
        start_time = time.time()
        self.gc_count += 1

        # 标记阶段
        marked_objects = self._mark()

        # 清除阶段
        self._sweep(marked_objects)

        end_time = time.time()
        logger.info(
            f"垃圾回收完成: 回收了 {len(self.vm.heap) - len(marked_objects)} 个对象, 耗时 {end_time - start_time:.4f}s")
        logger.info(f"堆状态: {self.used_heap}/{self.heap_size} ({self.used_heap / self.heap_size:.2%})")
        self.last_gc_time = end_time

    def _mark(self) -> Set[int]:
        """标记可达对象"""
        marked = set()

        # 从根集合开始标记
        # 1. 寄存器中的对象引用
        for value in self.vm.interpreter.registers:
            if isinstance(value, int) and value in self.vm.heap:
                self._mark_object(value, marked)

        # 2. 调用栈中的对象引用
        for frame in self.vm.interpreter.call_stack:
            for value in frame.get('registers', []):
                if isinstance(value, int) and value in self.vm.heap:
                    self._mark_object(value, marked)

        return marked

    def _mark_object(self, object_id: int, marked: Set[int]) -> None:
        """递归标记对象及其引用的对象"""
        if object_id in marked:
            return

        marked.add(object_id)
        obj = self.vm.heap[object_id]

        # 遍历对象的字段，标记引用的对象
        for field_value in obj['fields'].values():
            if isinstance(field_value, int) and field_value in self.vm.heap:
                self._mark_object(field_value, marked)

    def _sweep(self, marked_objects: Set[int]) -> None:
        """清除未标记的对象"""
        objects_to_delete = []

        # 找出未标记的对象
        for object_id in self.vm.heap:
            if object_id not in marked_objects:
                objects_to_delete.append(object_id)

        # 删除未标记的对象
        for object_id in objects_to_delete:
            obj_size = self._get_object_size(self.vm.heap[object_id])
            del self.vm.heap[object_id]
            self.used_heap -= obj_size

        logger.info(f"删除了 {len(objects_to_delete)} 个不可达对象")

    def _get_object_size(self, obj: Dict[str, Any]) -> int:
        """估算对象大小"""
        # 简化实现，实际需要根据对象类型和字段计算
        return 1024  # 假设每个对象1KB