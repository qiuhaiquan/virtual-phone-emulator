# src/core/dalvik/android_runtime.py
import logging
from typing import Any

from .vm import DalvikVM
from ..android_lib_loader import AndroidLibLoader
from ..graphic.opengl import OpenGLRenderer
from ..graphic.surface_flinger import SurfaceFlinger

logger = logging.getLogger(__name__)


class AndroidRuntime:
    """Android运行时环境"""

    def __init__(self, hardware_abstraction, lib_zip_path: str):
        self.vm = DalvikVM()
        self.hardware_abstraction = hardware_abstraction
        self.lib_loader = AndroidLibLoader(lib_zip_path)
        self.surface_flinger = SurfaceFlinger(hardware_abstraction)
        self.opengl_renderer = OpenGLRenderer()
        self._register_native_methods()

    def _register_native_methods(self) -> None:
        """注册本地方法"""
        # 注册方法代理，将调用转发到库加载器
        self.vm.register_native_method_proxy(self._handle_native_method_call)
        self.vm.register_native_method("android/view/SurfaceHolder.createSurface", self._create_surface)
        self.vm.register_native_method("android/opengl/GLSurfaceView.eglCreateContext", self._create_opengl_context)

    def _handle_native_method_call(self, class_name: str, method_name: str, args: list) -> Any:
        """处理本地方法调用"""
        logger.info(f"调用本地方法: {class_name}.{method_name}")

        # 加载类
        clazz = self.lib_loader.load_class(class_name)
        if not clazz:
            logger.error(f"找不到类: {class_name}")
            return None

        # 获取方法
        method = getattr(clazz, method_name, None)
        if not method or not callable(method):
            logger.error(f"找不到方法: {class_name}.{method_name}")
            return None

        # 调用方法
        try:
            # 创建类实例（如果方法不是静态的）
            instance = clazz(self.hardware_abstraction) if not hasattr(method, "__isstatic__") else None

            # 调用方法
            if instance:
                return method(instance, *args)
            else:
                return method(*args)

        except Exception as e:
            logger.error(f"调用方法失败: {e}")
            return None

    def _create_surface(self, vm, method, parser) -> None:
        """创建Surface的本地方法实现"""
        # 解析参数
        width = parser.get_int()
        height = parser.get_int()
        name = parser.get_string()

        # 创建surface
        surface = self.surface_flinger.create_surface(name, width, height)

        # 返回surface句柄给虚拟机
        vm.set_return_value(surface)

    def _create_opengl_context(self, vm, method, parser) -> None:
        """创建OpenGL上下文的本地方法实现"""
        context = self.opengl_renderer.create_context()
        vm.set_return_value(context)