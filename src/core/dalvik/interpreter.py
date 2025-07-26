import struct
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BytecodeInterpreter:
    def __init__(self, vm):
        self.vm = vm
        self.instructions = {
            0x70: self._invoke_direct,
            0x71: self._invoke_static,
            0x72: self._invoke_interface,
            0x74: self._invoke_virtual_range,
            0x75: self._invoke_super_range,
            0x76: self._invoke_direct_range,
            0x77: self._invoke_static_range,
            0x78: self._invoke_interface_range,

            # 返回指令
            0x79: self._return_void,
            0x7A: self._return,
            0x7B: self._return_wide,
            0x7C: self._return_object,

            # 实例操作
            0x22: self._new_instance,
            0x23: self._new_array,
            0x24: self._filled_new_array,
            0x25: self._filled_new_array_range,
            0x26: self._fill_array_data,
            0x27: self._throw,

            # 数组操作
            0x44: self._aget,
            0x45: self._aget_wide,
            0x46: self._aget_object,
            0x47: self._aget_boolean,
            0x48: self._aget_byte,
            0x49: self._aget_char,
            0x4A: self._aget_short,
            0x4B: self._aput,
            0x4C: self._aput_wide,
            0x4D: self._aput_object,
            0x4E: self._aput_boolean,
            0x4F: self._aput_byte,
            0x50: self._aput_char,
            0x51: self._aput_short,

            # 类型转换
            0x28: self._check_cast,
            0x29: self._instance_of,

            # 比较指令
            0x2A: self._cmpl_float,
            0x2B: self._cmpg_float,
            0x2C: self._cmpl_double,
            0x2D: self._cmpg_double,
            0x2E: self._cmp_long,

            # 条件分支
            0x2F: self._if_eq,
            0x30: self._if_ne,
            0x31: self._if_lt,
            0x32: self._if_ge,
            0x33: self._if_gt,
            0x34: self._if_le,
            0x35: self._if_eqz,
            0x36: self._if_nez,
            0x37: self._if_ltz,
            0x38: self._if_gez,
            0x39: self._if_gtz,
            0x3A: self._if_lez,

            # 无条件分支
            0x3B: self._goto,
            0x3C: self._goto_16,
            0x3D: self._goto_32,
            0x3E: self._packed_switch,
            0x3F: self._sparse_switch,

            # 算术运算
            0x90: self._add_int,
            0x91: self._sub_int,
            0x92: self._mul_int,
            0x93: self._div_int,
            0x94: self._rem_int,
            0x95: self._and_int,
            0x96: self._or_int,
            0x97: self._xor_int,
            0x98: self._shl_int,
            0x99: self._shr_int,
            0x9A: self._ushr_int,
            0x9B: self._add_long,
            0x9C: self._sub_long,
            0x9D: self._mul_long,
            0x9E: self._div_long,
            0x9F: self._rem_long,
            0xA0: self._and_long,
            0xA1: self._or_long,
            0xA2: self._xor_long,
            0xA3: self._shl_long,
            0xA4: self._shr_long,
            0xA5: self._ushr_long,
            0xA6: self._add_float,
            0xA7: self._sub_float,
            0xA8: self._mul_float,
            0xA9: self._div_float,
            0xAA: self._rem_float,
            0xAB: self._add_double,
            0xAC: self._sub_double,
            0xAD: self._mul_double,
            0xAE: self._div_double,
            0xAF: self._rem_double,

            # 自增运算
            0xB0: self._neg_int,
            0xB1: self._not_int,
            0xB2: self._neg_long,
            0xB3: self._not_long,
            0xB4: self._neg_float,
            0xB5: self._neg_double,
            0xB6: self._int_to_long,
            0xB7: self._int_to_float,
            0xB8: self._int_to_double,
            0xB9: self._long_to_int,
            0xBA: self._long_to_float,
            0xBB: self._long_to_double,
            0xBC: self._float_to_int,
            0xBD: self._float_to_long,
            0xBE: self._float_to_double,
            0xBF: self._double_to_int,
            0xC0: self._double_to_long,
            0xC1: self._double_to_float,
            0xC2: self._int_to_byte,
            0xC3: self._int_to_char,
            0xC4: self._int_to_short,

            # 特殊指令
            0xF0: self._nop,  # 扩展指令，这里简化处理
        }

    def interpret(self, method: Dict[str, Any], class_def: Dict[str, Any], dex_parser) -> None:
        """解释执行方法"""
        self.current_method = method
        self.current_class = class_def

        # 获取方法代码
        code_off = method.get('code_off', 0)
        if code_off == 0:
            logger.warning(f"方法 {method['name']} 没有代码")
            return

        # 获取代码项
        code = dex_parser.code_items.get(code_off)
        if not code:
            logger.warning(f"无法获取方法 {method['name']} 的代码")
            return

        # 初始化寄存器和程序计数器
        self.register_size = code['registers_size']
        self.registers = [None] * self.register_size
        self.pc = 0
        self.exception = None

        # 执行方法
        logger.info(f"开始解释执行方法: {method['class_name']}.{method['name']}")
        self._execute_code(code, dex_parser)

    def _execute_code(self, code: Dict[str, Any], dex_parser) -> None:
        """执行代码"""
        insns = code['insns']
        tries = code['tries']

        while self.pc < len(insns):
            # 检查异常
            if self.exception is not None:
                # 查找匹配的异常处理器
                handler = self._find_exception_handler(self.pc, self.exception, tries, dex_parser)
                if handler:
                    # 跳转到异常处理代码
                    self.pc = handler['handler_pc']
                    self.exception = None
                    logger.info(f"捕获异常，跳转到处理代码: {self.pc}")
                    continue
                else:
                    # 没有找到异常处理器，终止方法执行
                    logger.error(f"未处理的异常: {self.exception}")
                    return

            # 获取当前指令
            insn = insns[self.pc]
            opcode = insn['opcode']

            if opcode in self.instructions:
                # 执行指令
                logger.debug(f"执行指令: 0x{opcode:02x} at offset {insn['offset']}")
                self.instructions[opcode](insn, insns, dex_parser)
            else:
                logger.warning(f"未知指令: 0x{opcode:02x} at offset {insn['offset']}")
                self.pc += 1

            # 检查垃圾回收条件
            if self.pc % 100 == 0:  # 每执行100条指令检查一次
                self.vm.gc.collect_if_needed()

    def _find_exception_handler(self, pc: int, exception_type: str, tries: List[Dict[str, Any]], dex_parser) -> \
            Optional[Dict[str, Any]]:
        """查找匹配的异常处理器"""
        # 简化实现，实际需要解析handlers表
        for try_block in tries:
            if pc >= try_block['start_addr'] and pc < try_block['start_addr'] + try_block['insn_count']:
                # 找到匹配的try块，现在需要查找匹配的catch处理器
                # 这里简化处理，假设只有一个catch-all处理器
                return {
                    'handler_pc': try_block['handler_off']
                }

        return None

    # 指令实现（仅展示部分关键指令，完整实现需要所有指令）
    def _nop(self, insn, insns, dex_parser):
        """nop指令"""
        self.pc += 1

    def _move(self, insn, insns, dex_parser):
        """move指令"""
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        self.registers[vA] = self.registers[vB]
        self.pc += 1

    def _const_4(self, insn, insns, dex_parser):
        """const/4指令"""
        vA = (insn['opcode'] >> 4) & 0x0F
        value = insn['opcode'] & 0x0F
        self.registers[vA] = value
        self.pc += 1

    def _new_instance(self, insn, insns, dex_parser):
        """new-instance指令"""
        vA = (insn['opcode'] >> 4) & 0x0F
        type_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 2: insn['offset'] + 4])[0]
        class_name = dex_parser.type_ids[type_idx]

        # 创建对象实例
        object_id = self.vm._create_object(class_name)
        self.registers[vA] = object_id

        logger.debug(f"创建实例: {class_name} (ID: {object_id})")
        self.pc += 2

    def _invoke_virtual(self, insn, insns, dex_parser):
        """invoke-virtual指令"""
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用方法
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _move_result(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        # 假设结果在栈顶
        result = self.vm.stack.pop()
        self.registers[vA] = result
        self.pc += 1

    def _move_from16(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        self.registers[vA] = self.registers[vB]
        self.pc += 2

    def _move_16(self, insn, insns, dex_parser):
        vA = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        vB = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 3: insn['offset'] + 5])[0]
        self.registers[vA] = self.registers[vB]
        self.pc += 4

    def _move_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        self.registers[vA] = self.registers[vB]
        self.registers[vA + 1] = self.registers[vB + 1]
        self.pc += 1

    def _move_wide_from16(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        self.registers[vA] = self.registers[vB]
        self.registers[vA + 1] = self.registers[vB + 1]
        self.pc += 2

    def _move_wide_16(self, insn, insns, dex_parser):
        vA = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        vB = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 3: insn['offset'] + 5])[0]
        self.registers[vA] = self.registers[vB]
        self.registers[vA + 1] = self.registers[vB + 1]
        self.pc += 4

    def _move_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        self.registers[vA] = self.registers[vB]
        self.pc += 1

    def _move_object_from16(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        self.registers[vA] = self.registers[vB]
        self.pc += 2

    def _move_object_16(self, insn, insns, dex_parser):
        vA = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        vB = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 3: insn['offset'] + 5])[0]
        self.registers[vA] = self.registers[vB]
        self.pc += 4

    def _move_result_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        result_low = self.vm.stack.pop()
        result_high = self.vm.stack.pop()
        self.registers[vA] = result_low
        self.registers[vA + 1] = result_high
        self.pc += 1

    def _move_result_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        result = self.vm.stack.pop()
        self.registers[vA] = result
        self.pc += 1

    def _move_exception(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        exception = self.vm.stack.pop()
        self.registers[vA] = exception
        self.pc += 1

    def _const_16(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        value = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        self.registers[vA] = value
        self.pc += 2

    def _const(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        value = struct.unpack('<I', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 5])[0]
        self.registers[vA] = value
        self.pc += 4

    def _const_high16(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        value = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0] << 16
        self.registers[vA] = value
        self.pc += 2

    def _const_wide_16(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        value = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        self.registers[vA] = value
        self.registers[vA + 1] = 0
        self.pc += 2

    def _const_wide_32(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        value = struct.unpack('<I', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 5])[0]
        self.registers[vA] = value
        self.registers[vA + 1] = 0
        self.pc += 4

    def _const_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        value = struct.unpack('<Q', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 9])[0]
        self.registers[vA] = value & 0xFFFFFFFF
        self.registers[vA + 1] = value >> 32
        self.pc += 8

    def _const_wide_high16(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        value = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0] << 48
        self.registers[vA] = value & 0xFFFFFFFF
        self.registers[vA + 1] = value >> 32
        self.pc += 2

    def _const_string(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        string_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        string_value = dex_parser.string_data[string_idx]
        self.registers[vA] = string_value
        self.pc += 2

    def _const_string_jumbo(self, insn, insns, dex_parser):
        vA = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        string_idx = struct.unpack('<I', self.vm.dex_data[insn['offset'] + 3: insn['offset'] + 7])[0]
        string_value = dex_parser.string_data[string_idx]
        self.registers[vA] = string_value
        self.pc += 6

    def _const_class(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        type_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        class_name = dex_parser.type_ids[type_idx]
        # 简单示例，将类名作为类对象
        self.registers[vA] = class_name
        self.pc += 2

    def _monitor_enter(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        object_id = self.registers[vA]
        # 简单示例，假设锁操作成功
        self.vm.lock_object(object_id)
        self.pc += 1

    def _monitor_exit(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        object_id = self.registers[vA]
        # 简单示例，假设解锁操作成功
        self.vm.unlock_object(object_id)
        self.pc += 1

    def _iget(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.vm.get_object_field(object_id, field_idx)
        self.registers[vA] = field_value
        self.pc += 2

    def _iget_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.vm.get_object_field(object_id, field_idx)
        self.registers[vA] = field_value & 0xFFFFFFFF
        self.registers[vA + 1] = field_value >> 32
        self.pc += 2

    def _iget_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.vm.get_object_field(object_id, field_idx)
        self.registers[vA] = field_value
        self.pc += 2

    def _iget_boolean(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.vm.get_object_field(object_id, field_idx)
        self.registers[vA] = bool(field_value)
        self.pc += 2

    def _iget_byte(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.vm.get_object_field(object_id, field_idx)
        self.registers[vA] = field_value & 0xFF
        self.pc += 2

    def _iget_char(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.vm.get_object_field(object_id, field_idx)
        self.registers[vA] = field_value & 0xFFFF
        self.pc += 2

    def _iget_short(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.vm.get_object_field(object_id, field_idx)
        self.registers[vA] = field_value & 0xFFFF
        self.pc += 2

    def _sget(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.vm.get_static_field(field_idx)
        self.registers[vA] = field_value
        self.pc += 2

    def _sget_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.vm.get_static_field(field_idx)
        self.registers[vA] = field_value & 0xFFFFFFFF
        self.registers[vA + 1] = field_value >> 32
        self.pc += 2

    def _sget_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.vm.get_static_field(field_idx)
        self.registers[vA] = field_value
        self.pc += 2

    def _sget_boolean(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.vm.get_static_field(field_idx)
        self.registers[vA] = bool(field_value)
        self.pc += 2

    def _sget_byte(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.vm.get_static_field(field_idx)
        self.registers[vA] = field_value & 0xFF
        self.pc += 2

    def _sget_char(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.vm.get_static_field(field_idx)
        self.registers[vA] = field_value & 0xFFFF
        self.pc += 2

    def _sget_short(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.vm.get_static_field(field_idx)
        self.registers[vA] = field_value & 0xFFFF
        self.pc += 2

    def _iput(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.registers[vA]
        self.vm.set_object_field(object_id, field_idx, field_value)
        self.pc += 2

    def _iput_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.registers[vA]
        self.vm.set_object_field(object_id, field_idx, field_value)
        self.pc += 2

    def _iput_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = (self.registers[vA + 1] << 32) | self.registers[vA]
        self.vm.set_object_field(object_id, field_idx, field_value)
        self.pc += 2

    def _iput_boolean(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = int(self.registers[vA])
        self.vm.set_object_field(object_id, field_idx, field_value)
        self.pc += 2

    def _iput_byte(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.registers[vA] & 0xFF
        self.vm.set_object_field(object_id, field_idx, field_value)
        self.pc += 2

    def _iput_char(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.registers[vA] & 0xFFFF
        self.vm.set_object_field(object_id, field_idx, field_value)
        self.pc += 2

    def _iput_short(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        object_id = self.registers[vB]
        field_value = self.registers[vA] & 0xFFFF
        self.vm.set_object_field(object_id, field_idx, field_value)
        self.pc += 2

    def _sput(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.registers[vA]
        self.vm.set_static_field(field_idx, field_value)
        self.pc += 2

    def _sput_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = (self.registers[vA + 1] << 32) | self.registers[vA]
        self.vm.set_static_field(field_idx, field_value)
        self.pc += 2

    def _sput_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.registers[vA]
        self.vm.set_static_field(field_idx, field_value)
        self.pc += 2

    def _sput_boolean(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = int(self.registers[vA])
        self.vm.set_static_field(field_idx, field_value)
        self.pc += 2

    def _sput_byte(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.registers[vA] & 0xFF
        self.vm.set_static_field(field_idx, field_value)
        self.pc += 2

    def _sput_char(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.registers[vA] & 0xFFFF
        self.vm.set_static_field(field_idx, field_value)
        self.pc += 2

    def _sput_short(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        field_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        field_value = self.registers[vA] & 0xFFFF
        self.vm.set_static_field(field_idx, field_value)
        self.pc += 2

    def _invoke_super(self, insn, insns, dex_parser):
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用父类方法
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _invoke_direct(self, insn, insns, dex_parser):
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用直接方法
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _invoke_static(self, insn, insns, dex_parser):
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用静态方法
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _invoke_interface(self, insn, insns, dex_parser):
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用接口方法
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _invoke_virtual_range(self, insn, insns, dex_parser):
        vRegCount = (insn['opcode'] >> 4) & 0x0F
        vRegStart = insn['opcode'] & 0x0F
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用虚拟方法范围
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _invoke_super_range(self, insn, insns, dex_parser):
        vRegCount = (insn['opcode'] >> 4) & 0x0F
        vRegStart = insn['opcode'] & 0x0F
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用父类方法范围
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _invoke_direct_range(self, insn, insns, dex_parser):
        vRegCount = (insn['opcode'] >> 4) & 0x0F
        vRegStart = insn['opcode'] & 0x0F
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用直接方法范围
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _invoke_static_range(self, insn, insns, dex_parser):
        vRegCount = (insn['opcode'] >> 4) & 0x0F
        vRegStart = insn['opcode'] & 0x0F
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用静态方法范围
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _invoke_interface_range(self, insn, insns, dex_parser):
        vRegCount = (insn['opcode'] >> 4) & 0x0F
        vRegStart = insn['opcode'] & 0x0F
        method_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        # 简单示例，调用接口方法范围
        # 这里需要根据实际情况实现方法调用逻辑
        self.pc += 2

    def _return_void(self, insn, insns, dex_parser):
        # 简单示例，返回空
        self.vm.stack.pop_frame()
        return

    def _return_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        result = (self.registers[vA + 1] << 32) | self.registers[vA]
        self.vm.stack.pop_frame()
        self.vm.stack.push(result)
        return

    def _return_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        result = self.registers[vA]
        self.vm.stack.pop_frame()
        self.vm.stack.push(result)
        return

    def _return(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        result = self.registers[vA]
        self.vm.stack.pop_frame()
        self.vm.stack.push(result)
        return

    def _new_array(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        type_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        array_length = self.registers[vB]
        array_type = dex_parser.type_ids[type_idx]
        array_id = self.vm._create_array(array_type, array_length)
        self.registers[vA] = array_id
        self.pc += 2

    def _filled_new_array(self, insn, insns, dex_parser):
        vRegCount = (insn['opcode'] >> 4) & 0x0F
        vRegStart = insn['opcode'] & 0x0F
        type_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        array_type = dex_parser.type_ids[type_idx]
        array_length = vRegCount
        array_id = self.vm._create_array(array_type, array_length)
        for i in range(array_length):
            self.vm.set_array_element(array_id, i, self.registers[vRegStart + i])
        self.vm.stack.push(array_id)
        self.pc += 2

    def _filled_new_array_range(self, insn, insns, dex_parser):
        vRegCount = (insn['opcode'] >> 4) & 0x0F
        vRegStart = insn['opcode'] & 0x0F
        type_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        array_type = dex_parser.type_ids[type_idx]
        array_length = vRegCount
        array_id = self.vm._create_array(array_type, array_length)
        for i in range(array_length):
            self.vm.set_array_element(array_id, i, self.registers[vRegStart + i])
        self.vm.stack.push(array_id)
        self.pc += 2

    def _fill_array_data(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        array_id = self.registers[vA]
        data_offset = struct.unpack('<I', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 5])[0]
        # 简单示例，填充数组数据
        # 这里需要根据实际情况实现数组数据填充逻辑
        self.pc += 4

    def _throw(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        exception = self.registers[vA]
        self.exception = exception
        self.pc += 1

    def _aget(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        element = self.vm.get_array_element(array_id, index)
        self.registers[vA] = element
        self.pc += 1

    def _aget_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        element = self.vm.get_array_element(array_id, index)
        self.registers[vA] = element & 0xFFFFFFFF
        self.registers[vA + 1] = element >> 32
        self.pc += 1

    def _aget_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        element = self.vm.get_array_element(array_id, index)
        self.registers[vA] = element
        self.pc += 1

    def _aget_boolean(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        element = self.vm.get_array_element(array_id, index)
        self.registers[vA] = bool(element)
        self.pc += 1

    def _aget_byte(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        element = self.vm.get_array_element(array_id, index)
        self.registers[vA] = element & 0xFF
        self.pc += 1

    def _aget_char(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        element = self.vm.get_array_element(array_id, index)
        self.registers[vA] = element & 0xFFFF
        self.pc += 1

    def _aget_short(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        element = self.vm.get_array_element(array_id, index)
        self.registers[vA] = element & 0xFFFF
        self.pc += 1

    def _aput(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        value = self.registers[vA]
        self.vm.set_array_element(array_id, index, value)
        self.pc += 1

    def _aput_wide(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        value = (self.registers[vA + 1] << 32) | self.registers[vA]
        self.vm.set_array_element(array_id, index, value)
        self.pc += 1

    def _aput_object(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        value = self.registers[vA]
        self.vm.set_array_element(array_id, index, value)
        self.pc += 1

    def _aput_boolean(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        value = int(self.registers[vA])
        self.vm.set_array_element(array_id, index, value)
        self.pc += 1

    def _aput_byte(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        value = self.registers[vA] & 0xFF
        self.vm.set_array_element(array_id, index, value)
        self.pc += 1

    def _aput_char(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        value = self.registers[vA] & 0xFFFF
        self.vm.set_array_element(array_id, index, value)
        self.pc += 1

    def _aput_short(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        array_id = self.registers[vB]
        index = self.registers[vC]
        value = self.registers[vA] & 0xFFFF
        self.vm.set_array_element(array_id, index, value)
        self.pc += 1

    def _check_cast(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        type_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        target_type = dex_parser.type_ids[type_idx]
        object_id = self.registers[vA]
        object_type = self.vm.get_object_type(object_id)
        if object_type != target_type:
            self.exception = f"ClassCastException: {object_type} cannot be cast to {target_type}"
            self.pc += 1
            return
        self.pc += 2

    def _instance_of(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        type_idx = struct.unpack('<H', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        target_type = dex_parser.type_ids[type_idx]
        object_id = self.registers[vB]
        object_type = self.vm.get_object_type(object_id)
        result = int(object_type == target_type)
        self.registers[vA] = result
        self.pc += 2

    def _cmpl_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        if value1 < value2:
            result = 1
        elif value1 > value2:
            result = -1
        else:
            result = 0
        self.registers[vA] = result
        self.pc += 1

    def _cmpg_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        if value1 > value2:
            result = 1
        elif value1 < value2:
            result = -1
        else:
            result = 0
        self.registers[vA] = result
        self.pc += 1

    def _cmpl_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        if value1 < value2:
            result = 1
        elif value1 > value2:
            result = -1
        else:
            result = 0
        self.registers[vA] = result
        self.pc += 1

    def _cmpg_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        if value1 > value2:
            result = 1
        elif value1 < value2:
            result = -1
        else:
            result = 0
        self.registers[vA] = result
        self.pc += 1

    def _cmp_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        if value1 > value2:
            result = 1
        elif value1 < value2:
            result = -1
        else:
            result = 0
        self.registers[vA] = result
        self.pc += 1

    def _if_eg(self, insn, insns, dex_parser):
        # 可能是拼写错误，应该是 _if_eq
        self._if_eq(insn, insns, dex_parser)

    def _if_ne(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value1 = self.registers[vA]
        value2 = self.registers[vB]
        if value1 != value2:
            self.pc += offset
        else:
            self.pc += 2

    def _if_eq(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value1 = self.registers[vA]
        value2 = self.registers[vB]
        if value1 == value2:
            self.pc += offset
        else:
            self.pc += 2

    def _if_lt(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value1 = self.registers[vA]
        value2 = self.registers[vB]
        if value1 < value2:
            self.pc += offset
        else:
            self.pc += 2

    def _if_le(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value1 = self.registers[vA]
        value2 = self.registers[vB]
        if value1 <= value2:
            self.pc += offset
        else:
            self.pc += 2

    def _if_gt(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value1 = self.registers[vA]
        value2 = self.registers[vB]
        if value1 > value2:
            self.pc += offset
        else:
            self.pc += 2

    def _if_ge(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value1 = self.registers[vA]
        value2 = self.registers[vB]
        if value1 >= value2:
            self.pc += offset
        else:
            self.pc += 2

    def _if_eqz(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value = self.registers[vA]
        if value == 0:
            self.pc += offset
        else:
            self.pc += 2

    def _if_ltz(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value = self.registers[vA]
        if value < 0:
            self.pc += offset
        else:
            self.pc += 2

    def _if_nez(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value = self.registers[vA]
        if value != 0:
            self.pc += offset
        else:
            self.pc += 2

    def _if_gez(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value = self.registers[vA]
        if value >= 0:
            self.pc += offset
        else:
            self.pc += 2

    def _if_gtz(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value = self.registers[vA]
        if value > 0:
            self.pc += offset
        else:
            self.pc += 2

    def _if_lez(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        value = self.registers[vA]
        if value <= 0:
            self.pc += offset
        else:
            self.pc += 2

    def _goto(self, insn, insns, dex_parser):
        offset = struct.unpack('<b', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 2])[0]
        self.pc += offset

    def _goto_16(self, insn, insns, dex_parser):
        offset = struct.unpack('<h', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 3])[0]
        self.pc += offset

    def _goto_32(self, insn, insns, dex_parser):
        offset = struct.unpack('<i', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 5])[0]
        self.pc += offset

    def _packed_switch(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        key = self.registers[vA]
        table_offset = struct.unpack('<I', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 5])[0]
        first_key = struct.unpack('<I', self.vm.dex_data[table_offset: table_offset + 4])[0]
        size = struct.unpack('<I', self.vm.dex_data[table_offset + 4: table_offset + 8])[0]
        for i in range(size):
            target_offset = struct.unpack('<i', self.vm.dex_data[table_offset + 8 + i * 4: table_offset + 12 + i * 4])[0]
            if key == first_key + i:
                self.pc += target_offset
                return
        self.pc += 4

    def _sparse_switch(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        key = self.registers[vA]
        table_offset = struct.unpack('<I', self.vm.dex_data[insn['offset'] + 1: insn['offset'] + 5])[0]
        size = struct.unpack('<I', self.vm.dex_data[table_offset: table_offset + 4])[0]
        for i in range(size):
            case_key = struct.unpack('<I', self.vm.dex_data[table_offset + 4 + i * 8: table_offset + 8 + i * 8])[0]
            target_offset = struct.unpack('<i', self.vm.dex_data[table_offset + 8 + i * 8: table_offset + 12 + i * 8])[0]
            if key == case_key:
                self.pc += target_offset
                return
        self.pc += 4

    def _add_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 + value2
        self.registers[vA] = result
        self.pc += 1

    def _sub_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 - value2
        self.registers[vA] = result
        self.pc += 1

    def _mul_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 * value2
        self.registers[vA] = result
        self.pc += 1

    def _div_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        if value2 == 0:
            self.exception = "ArithmeticException: division by zero"
            self.pc += 1
            return
        result = value1 // value2
        self.registers[vA] = result
        self.pc += 1

    def _rem_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        if value2 == 0:
            self.exception = "ArithmeticException: division by zero"
            self.pc += 1
            return
        result = value1 % value2
        self.registers[vA] = result
        self.pc += 1

    def _and_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 & value2
        self.registers[vA] = result
        self.pc += 1

    def _or_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 | value2
        self.registers[vA] = result
        self.pc += 1

    def _xor_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 ^ value2
        self.registers[vA] = result
        self.pc += 1

    def _shl_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 << value2
        self.registers[vA] = result
        self.pc += 1

    def _shr_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 >> value2
        self.registers[vA] = result
        self.pc += 1

    def _ushr_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = (value1 % 0x100000000) >> value2
        self.registers[vA] = result
        self.pc += 1

    def _add_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 + value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _sub_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 - value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _mul_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 * value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _div_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        if value2 == 0:
            self.exception = "ArithmeticException: division by zero"
            self.pc += 1
            return
        result = value1 // value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _rem_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        if value2 == 0:
            self.exception = "ArithmeticException: division by zero"
            self.pc += 1
            return
        result = value1 % value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _and_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 & value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _or_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 | value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _xor_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 ^ value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _shl_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = self.registers[vC]
        result = value1 << value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _shr_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = self.registers[vC]
        result = value1 >> value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _ushr_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = self.registers[vC]
        result = (value1 % 0x10000000000000000) >> value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _add_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 + value2
        self.registers[vA] = result
        self.pc += 1

    def _sub_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 - value2
        self.registers[vA] = result
        self.pc += 1

    def _mul_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        result = value1 * value2
        self.registers[vA] = result
        self.pc += 1

    def _div_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        if value2 == 0:
            self.exception = "ArithmeticException: division by zero"
            self.pc += 1
            return
        result = value1 / value2
        self.registers[vA] = result
        self.pc += 1

    def _rem_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = self.registers[vB]
        value2 = self.registers[vC]
        if value2 == 0:
            self.exception = "ArithmeticException: division by zero"
            self.pc += 1
            return
        result = value1 % value2
        self.registers[vA] = result
        self.pc += 1

    def _add_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 + value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _sub_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 - value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _mul_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        result = value1 * value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _div_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        if value2 == 0:
            self.exception = "ArithmeticException: division by zero"
            self.pc += 1
            return
        result = value1 / value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _rem_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        vC = (insn['opcode'] >> 8) & 0x0F
        value1 = (self.registers[vB + 1] << 32) | self.registers[vB]
        value2 = (self.registers[vC + 1] << 32) | self.registers[vC]
        if value2 == 0:
            self.exception = "ArithmeticException: division by zero"
            self.pc += 1
            return
        result = value1 % value2
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _neg_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = -value
        self.registers[vA] = result
        self.pc += 1

    def _not_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = ~value
        self.registers[vA] = result
        self.pc += 1

    def _neg_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = -value
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _not_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = ~value
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _neg_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = -value
        self.registers[vA] = result
        self.pc += 1

    def _neg_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = -value
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _int_to_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        self.registers[vA] = value
        self.registers[vA + 1] = 0
        self.pc += 1

    def _int_to_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = float(value)
        self.registers[vA] = result
        self.pc += 1

    def _int_to_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = float(value)
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _long_to_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = int(value)
        self.registers[vA] = result
        self.pc += 1

    def _long_to_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = float(value)
        self.registers[vA] = result
        self.pc += 1

    def _long_to_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = float(value)
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _float_to_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = int(value)
        self.registers[vA] = result
        self.pc += 1

    def _float_to_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = int(value)
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _float_to_double(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = float(value)
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _double_to_int(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = int(value)
        self.registers[vA] = result
        self.pc += 1

    def _double_to_long(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = int(value)
        self.registers[vA] = result & 0xFFFFFFFF
        self.registers[vA + 1] = result >> 32
        self.pc += 1

    def _double_to_float(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = (self.registers[vB + 1] << 32) | self.registers[vB]
        result = float(value)
        self.registers[vA] = result
        self.pc += 1

    def _int_to_byte(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = value & 0xFF
        self.registers[vA] = result
        self.pc += 1

    def _int_to_short(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = value & 0xFFFF
        self.registers[vA] = result
        self.pc += 1

    def _int_to_char(self, insn, insns, dex_parser):
        vA = (insn['opcode'] >> 4) & 0x0F
        vB = insn['opcode'] & 0x0F
        value = self.registers[vB]
        result = value & 0xFFFF
        self.registers[vA] = result
        self.pc += 1
