# src/core/dalvik/dex_parser.py
import struct
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DEXParser:
    """完整的DEX文件解析器"""

    def __init__(self, dex_data: bytes):
        self.dex_data = dex_data
        self.header = {}
        self.string_ids = []
        self.type_ids = []
        self.proto_ids = []
        self.field_ids = []
        self.method_ids = []
        self.class_defs = []
        self.code_items = {}
        self.string_data = []

    def parse(self) -> bool:
        """解析整个DEX文件"""
        try:
            self._parse_header()
            self._parse_string_ids()
            self._parse_type_ids()
            self._parse_proto_ids()
            self._parse_field_ids()
            self._parse_method_ids()
            self._parse_class_defs()
            self._parse_code_items()

            logger.info(f"DEX文件解析完成: {len(self.class_defs)}个类, {len(self.method_ids)}个方法")
            return True
        except Exception as e:
            logger.error(f"解析DEX文件失败: {e}")
            return False

    def _parse_header(self) -> None:
        """解析DEX文件头部"""
        # 读取魔数和版本
        magic = self.dex_data[0:8].decode('ascii')
        if magic[:3] != 'dex' or len(magic) < 8:
            raise ValueError("无效的DEX文件格式")

        self.header['magic'] = magic
        self.header['checksum'] = struct.unpack('<I', self.dex_data[8:12])[0]
        self.header['signature'] = self.dex_data[12:32]
        self.header['file_size'] = struct.unpack('<I', self.dex_data[32:36])[0]
        self.header['header_size'] = struct.unpack('<I', self.dex_data[36:40])[0]
        self.header['endian_tag'] = struct.unpack('<I', self.dex_data[40:44])[0]

        # 读取各部分偏移量
        self.header['string_ids_off'] = struct.unpack('<I', self.dex_data[44:48])[0]
        self.header['type_ids_off'] = struct.unpack('<I', self.dex_data[48:52])[0]
        self.header['proto_ids_off'] = struct.unpack('<I', self.dex_data[52:56])[0]
        self.header['field_ids_off'] = struct.unpack('<I', self.dex_data[56:60])[0]
        self.header['method_ids_off'] = struct.unpack('<I', self.dex_data[60:64])[0]
        self.header['class_defs_off'] = struct.unpack('<I', self.dex_data[64:68])[0]
        self.header['data_off'] = struct.unpack('<I', self.dex_data[68:72])[0]

        # 读取各部分数量
        self.header['string_ids_size'] = struct.unpack('<I', self.dex_data[72:76])[0]
        self.header['type_ids_size'] = struct.unpack('<I', self.dex_data[76:80])[0]
        self.header['proto_ids_size'] = struct.unpack('<I', self.dex_data[80:84])[0]
        self.header['field_ids_size'] = struct.unpack('<I', self.dex_data[84:88])[0]
        self.header['method_ids_size'] = struct.unpack('<I', self.dex_data[88:92])[0]
        self.header['class_defs_size'] = struct.unpack('<I', self.dex_data[92:96])[0]

    def _parse_string_ids(self) -> None:
        """解析字符串ID表"""
        count = self.header['string_ids_size']
        offset = self.header['string_ids_off']

        for i in range(count):
            data_offset = struct.unpack('<I', self.dex_data[offset + i * 4: offset + (i + 1) * 4])[0]
            string_data = self._read_utf8_string(data_offset)
            self.string_ids.append(string_data)

    def _read_utf8_string(self, offset: int) -> str:
        """从指定偏移量读取UTF-8字符串"""
        # 读取uleb128格式的字符串长度
        length, size = self._read_uleb128(offset)

        # 读取字符串数据
        string_data = self.dex_data[offset + size: offset + size + length]
        return string_data.decode('utf-8', errors='replace')

    def _read_uleb128(self, offset: int) -> (int, int):
        """读取uleb128格式的整数，返回值和占用的字节数"""
        result = 0
        shift = 0
        bytes_read = 0

        while True:
            byte = self.dex_data[offset + bytes_read]
            result |= (byte & 0x7F) << shift
            bytes_read += 1

            if (byte & 0x80) == 0:
                break

            shift += 7

        return result, bytes_read

    def _parse_type_ids(self) -> None:
        """解析类型ID表"""
        count = self.header['type_ids_size']
        offset = self.header['type_ids_off']

        for i in range(count):
            string_idx = struct.unpack('<I', self.dex_data[offset + i * 4: offset + (i + 1) * 4])[0]
            self.type_ids.append(self.string_ids[string_idx])

    def _parse_proto_ids(self) -> None:
        """解析方法原型ID表"""
        count = self.header['proto_ids_size']
        offset = self.header['proto_ids_off']

        for i in range(count):
            shorty_idx = struct.unpack('<I', self.dex_data[offset + i * 12: offset + i * 12 + 4])[0]
            return_type_idx = struct.unpack('<I', self.dex_data[offset + i * 12 + 4: offset + i * 12 + 8])[0]
            parameters_off = struct.unpack('<I', self.dex_data[offset + i * 12 + 8: offset + i * 12 + 12])[0]

            # 解析参数类型列表
            parameters = []
            if parameters_off != 0:
                size = struct.unpack('<I', self.dex_data[parameters_off: parameters_off + 4])[0]
                for j in range(size):
                    type_idx = \
                    struct.unpack('<I', self.dex_data[parameters_off + 4 + j * 4: parameters_off + 4 + (j + 1) * 4])[0]
                    parameters.append(self.type_ids[type_idx])

            self.proto_ids.append({
                'shorty': self.string_ids[shorty_idx],
                'return_type': self.type_ids[return_type_idx],
                'parameters': parameters
            })

    def _parse_field_ids(self) -> None:
        """解析字段ID表"""
        count = self.header['field_ids_size']
        offset = self.header['field_ids_off']

        for i in range(count):
            class_idx = struct.unpack('<H', self.dex_data[offset + i * 8: offset + i * 8 + 2])[0]
            type_idx = struct.unpack('<H', self.dex_data[offset + i * 8 + 2: offset + i * 8 + 4])[0]
            name_idx = struct.unpack('<I', self.dex_data[offset + i * 8 + 4: offset + i * 8 + 8])[0]

            self.field_ids.append({
                'class_idx': class_idx,
                'class_name': self.type_ids[class_idx],
                'type_idx': type_idx,
                'type_name': self.type_ids[type_idx],
                'name_idx': name_idx,
                'name': self.string_ids[name_idx]
            })

    def _parse_method_ids(self) -> None:
        """解析方法ID表"""
        count = self.header['method_ids_size']
        offset = self.header['method_ids_off']

        for i in range(count):
            class_idx = struct.unpack('<H', self.dex_data[offset + i * 8: offset + i * 8 + 2])[0]
            proto_idx = struct.unpack('<H', self.dex_data[offset + i * 8 + 2: offset + i * 8 + 4])[0]
            name_idx = struct.unpack('<I', self.dex_data[offset + i * 8 + 4: offset + i * 8 + 8])[0]

            self.method_ids.append({
                'class_idx': class_idx,
                'class_name': self.type_ids[class_idx],
                'proto_idx': proto_idx,
                'name_idx': name_idx,
                'name': self.string_ids[name_idx],
                'proto': self.proto_ids[proto_idx],
                'code_off': 0  # 稍后在解析类定义时填充
            })

    def _parse_class_defs(self) -> None:
        """解析类定义"""
        count = self.header['class_defs_size']
        offset = self.header['class_defs_off']

        for i in range(count):
            class_idx = struct.unpack('<I', self.dex_data[offset + i * 32: offset + i * 32 + 4])[0]
            access_flags = struct.unpack('<I', self.dex_data[offset + i * 32 + 4: offset + i * 32 + 8])[0]
            superclass_idx = struct.unpack('<I', self.dex_data[offset + i * 32 + 8: offset + i * 32 + 12])[0]
            interfaces_off = struct.unpack('<I', self.dex_data[offset + i * 32 + 12: offset + i * 32 + 16])[0]
            source_file_idx = struct.unpack('<I', self.dex_data[offset + i * 32 + 16: offset + i * 32 + 20])[0]
            annotations_off = struct.unpack('<I', self.dex_data[offset + i * 32 + 20: offset + i * 32 + 24])[0]
            class_data_off = struct.unpack('<I', self.dex_data[offset + i * 32 + 24: offset + i * 32 + 28])[0]
            static_values_off = struct.unpack('<I', self.dex_data[offset + i * 32 + 28: offset + i * 32 + 32])[0]

            # 解析接口列表
            interfaces = []
            if interfaces_off != 0:
                size = struct.unpack('<I', self.dex_data[interfaces_off: interfaces_off + 4])[0]
                for j in range(size):
                    type_idx = \
                    struct.unpack('<I', self.dex_data[interfaces_off + 4 + j * 4: interfaces_off + 4 + (j + 1) * 4])[0]
                    interfaces.append(self.type_ids[type_idx])

            # 解析源文件名
            source_file = None
            if source_file_idx != 0xFFFFFFFF:
                source_file = self.string_ids[source_file_idx]

            # 解析超类名
            superclass_name = 'java/lang/Object'
            if superclass_idx != 0xFFFFFFFF:
                superclass_name = self.type_ids[superclass_idx]

            # 解析类数据
            direct_methods = []
            virtual_methods = []
            if class_data_off != 0:
                # 解析类数据结构
                # 格式: [uleb128] static_fields_size, instance_fields_size, direct_methods_size, virtual_methods_size
                # 然后依次是静态字段、实例字段、直接方法、虚方法
                pos = class_data_off

                # 读取各部分大小
                static_fields_size, bytes_read = self._read_uleb128(pos)
                pos += bytes_read
                instance_fields_size, bytes_read = self._read_uleb128(pos)
                pos += bytes_read
                direct_methods_size, bytes_read = self._read_uleb128(pos)
                pos += bytes_read
                virtual_methods_size, bytes_read = self._read_uleb128(pos)
                pos += bytes_read

                # 解析字段
                # 格式: [uleb128] field_idx_diff, access_flags
                fields = []
                last_field_idx = 0
                for _ in range(static_fields_size + instance_fields_size):
                    field_idx_diff, bytes_read = self._read_uleb128(pos)
                    pos += bytes_read
                    access_flags, bytes_read = self._read_uleb128(pos)
                    pos += bytes_read

                    field_idx = last_field_idx + field_idx_diff
                    last_field_idx = field_idx

                    fields.append({
                        'field_idx': field_idx,
                        'access_flags': access_flags
                    })

                # 解析方法
                # 格式: [uleb128] method_idx_diff, access_flags, code_off
                last_method_idx = 0
                for _ in range(direct_methods_size):
                    method_idx_diff, bytes_read = self._read_uleb128(pos)
                    pos += bytes_read
                    access_flags, bytes_read = self._read_uleb128(pos)
                    pos += bytes_read
                    code_off, bytes_read = self._read_uleb128(pos)
                    pos += bytes_read

                    method_idx = last_method_idx + method_idx_diff
                    last_method_idx = method_idx

                    if method_idx < len(self.method_ids):
                        self.method_ids[method_idx]['code_off'] = code_off
                        direct_methods.append({
                            'method_idx': method_idx,
                            'access_flags': access_flags,
                            'code_off': code_off
                        })

                for _ in range(virtual_methods_size):
                    method_idx_diff, bytes_read = self._read_uleb128(pos)
                    pos += bytes_read
                    access_flags, bytes_read = self._read_uleb128(pos)
                    pos += bytes_read
                    code_off, bytes_read = self._read_uleb128(pos)
                    pos += bytes_read

                    method_idx = last_method_idx + method_idx_diff
                    last_method_idx = method_idx

                    if method_idx < len(self.method_ids):
                        self.method_ids[method_idx]['code_off'] = code_off
                        virtual_methods.append({
                            'method_idx': method_idx,
                            'access_flags': access_flags,
                            'code_off': code_off
                        })

            self.class_defs.append({
                'class_idx': class_idx,
                'class_name': self.type_ids[class_idx],
                'access_flags': access_flags,
                'superclass_name': superclass_name,
                'interfaces': interfaces,
                'source_file': source_file,
                'class_data_off': class_data_off,
                'direct_methods': direct_methods,
                'virtual_methods': virtual_methods
            })

    def _parse_code_items(self) -> None:
        """解析方法代码项"""
        for method in self.method_ids:
            code_off = method.get('code_off', 0)
            if code_off == 0:
                continue

            # 解析CodeItem结构
            registers_size = struct.unpack('<H', self.dex_data[code_off: code_off + 2])[0]
            ins_size = struct.unpack('<H', self.dex_data[code_off + 2: code_off + 4])[0]
            outs_size = struct.unpack('<H', self.dex_data[code_off + 4: code_off + 6])[0]
            tries_size = struct.unpack('<H', self.dex_data[code_off + 6: code_off + 8])[0]
            debug_info_off = struct.unpack('<I', self.dex_data[code_off + 8: code_off + 12])[0]
            insns_size = struct.unpack('<I', self.dex_data[code_off + 12: code_off + 16])[0]

            # 读取指令
            insns = []
            pos = code_off + 16
            for i in range(insns_size):
                # 指令格式: [ushort] opcode | (registers << 8)
                insn = struct.unpack('<H', self.dex_data[pos: pos + 2])[0]
                opcode = insn & 0xFF
                registers = (insn >> 8) & 0xFF

                # 不同类型的指令有不同的长度和格式
                # 这里只做简单处理，实际需要根据opcode解析完整指令
                insns.append({
                    'opcode': opcode,
                    'registers': registers,
                    'offset': pos
                })

                # 大多数指令是2字节，但有些是4字节或更长
                # 这里简化处理，假设所有指令都是2字节
                pos += 2

            # 解析异常处理表
            tries = []
            if tries_size > 0:
                # 异常处理表在指令之后
                tries_pos = pos
                for i in range(tries_size):
                    start_addr = struct.unpack('<I', self.dex_data[tries_pos: tries_pos + 4])[0]
                    insn_count = struct.unpack('<H', self.dex_data[tries_pos + 4: tries_pos + 6])[0]
                    handler_off = struct.unpack('<H', self.dex_data[tries_pos + 6: tries_pos + 8])[0]

                    tries.append({
                        'start_addr': start_addr,
                        'insn_count': insn_count,
                        'handler_off': handler_off
                    })

                    tries_pos += 8

                # 解析handlers表
                handlers = {}
                handlers_pos = tries_pos

                # 每个handler列表以uleb128格式的size开始
                # 如果size为负数，表示最后一个entry是catch-all
                # 否则，最后一个entry是catch-all

                # 这里简化处理，不详细解析handlers表

            self.code_items[code_off] = {
                'registers_size': registers_size,
                'ins_size': ins_size,
                'outs_size': outs_size,
                'tries_size': tries_size,
                'insns': insns,
                'tries': tries
            }

    def get_main_method(self) -> Optional[Dict[str, Any]]:
        """查找main方法"""
        for method in self.method_ids:
            if method['name'] == 'main' and method['proto']['return_type'] == 'V':
                # 检查参数是否为[String[]]
                if (len(method['proto']['parameters']) == 1 and
                        method['proto']['parameters'][0] == '[Ljava/lang/String;'):
                    return method
        return None