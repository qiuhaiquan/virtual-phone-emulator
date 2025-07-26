# src/core/dalvik/vm.py
import time
import logging
from typing import Dict, Any, Optional
from .dex_parser import DEXParser
from .interpreter import BytecodeInterpreter  # 新增导入
from .jit import JITCompiler  # 新增导入
from .gc import GarbageCollector  # 新增导入

logger = logging.getLogger(__name__)


class DalvikVM:
    """增强版Dalvik/ART虚拟机，支持字节码解释、JIT编译和垃圾回收"""

    def __init__(self):
        self.loaded_classes = {}
        self.registered_natives = {}
        self.heap = {}  # 对象堆
        self.next_object_id = 1

        # 新增组件
        self.interpreter = BytecodeInterpreter(self)  # 字节码解释器
        self.jit = JITCompiler(self)  # JIT编译器
        self.gc = GarbageCollector(self)  # 垃圾回收器

    def load_dex(self, dex_data: bytes) -> bool:
        """加载DEX文件"""
        parser = DEXParser(dex_data)
        if not parser.parse():
            return False

        # 加载类
        for class_def in parser.class_defs:
            class_name = class_def['class_name']
            self.loaded_classes[class_name] = class_def
            logger.debug(f"加载类: {class_name}")

        return True

    def execute_main(self, dex_data: bytes) -> None:
        """执行DEX文件中的main方法"""
        parser = DEXParser(dex_data)
        if not parser.parse():
            logger.error("无法解析DEX文件")
            return

        main_method = parser.get_main_method()
        if not main_method:
            logger.warning("未找到main方法")
            return

        logger.info(f"准备执行main方法: {main_method['class_name']}.{main_method['name']}")

        # 找到主类定义
        main_class = None
        for class_def in parser.class_defs:
            if class_def['class_name'] == main_method['class_name']:
                main_class = class_def
                break

        if not main_class:
            logger.error(f"找不到主类定义: {main_method['class_name']}")
            return

        # 执行主方法
        self._execute_method(main_method, main_class, parser)

    def _execute_method(self, method: Dict[str, Any], class_def: Dict[str, Any], dex_parser) -> None:
        """执行方法"""
        # 检查是否应该JIT编译
        if self.jit.should_compile(method):
            compiled_function = self.jit.compile_method(method, class_def, dex_parser)
            if compiled_function:
                self.jit.execute_compiled(method, class_def, dex_parser)
                return

        # 否则使用解释器执行
        self.interpreter.interpret(method, class_def, dex_parser)

    def _create_object(self, class_name: str) -> int:
        """创建对象实例"""
        object_id = self.next_object_id
        self.next_object_id += 1

        # 估算对象大小
        obj_size = 1024  # 简化为1KB
        self.gc.used_heap += obj_size

        self.heap[object_id] = {
            'class_name': class_name,
            'fields': {},
            'marked': False
        }

        logger.debug(f"创建对象: {class_name} (ID: {object_id}, 大小: {obj_size}B)")

        # 检查是否需要垃圾回收
        self.gc.collect_if_needed()

        return object_id

    def register_native_method(self, method_name: str, handler) -> None:
        """注册本地方法"""
        self.registered_natives[method_name] = handler
        logger.info(f"注册本地方法: {method_name}")