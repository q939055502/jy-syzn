# 检测数据处理工具
# 用于处理检测参数数据，包括数据转换、重复单元格清洗和行高计算等

import sys
import os

# 添加项目根目录到Python路径，确保可以直接运行该脚本
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

import logging
from typing import List, Dict, Optional

# 创建日志记录器
logger = logging.getLogger(__name__)


class DetectionDataProcessor:
    """
    检测数据处理器类，用于处理检测参数数据
    """
    
    def __init__(self):
        """
        初始化检测数据处理器
        """
        # 不同设备对应的列宽度配置
        # 格式：[参数/单价, 组批规则, 取样频率, 取样要求, 送检要求, 所需信息, 检评规范, 备注]
        self.pc_col_widths = [120, 130, 130, 130, 130, 150, 150, 130]
        self.tablet_col_widths = [80, 90, 90, 90, 90, 100, 100, 98]
        self.phone_col_widths = [40, 45, 45, 45, 45, 50, 50, 55]
        
        # 表格基础配置
        self.line_spacing = 1.2
        self.text_margin = 1  # 文字与边框距离尽可能最小、紧凑
    
    def transform_detection_data(self, params: List[dict]) -> List[dict]:
        """
        转换检测数据，按规则提取和转换字段
        
        :param params: 检测参数列表
        :return: 转换后的新列表
        """
        transformed_data = []
        
        for param in params:
            # 转换param_name，拼接价格
            param_name = param.get('param_name', '')
            price = param.get('price', '')
            transformed_param_name = f"{param_name}({price})"
            
            # 构建备注字段
            report_time = param.get('report_time', '')
            template_code = param.get('template_code', '')
            remark = f"{report_time}\n委托单{template_code}"
            
            # 提取并转换字段，处理空值
            transformed_item = {
                'is_regular_param': param.get('is_regular_param', 0),
                'param_name': transformed_param_name,
                'sampling_batch': param.get('sampling_batch', ''),
                'sampling_frequency': param.get('sampling_frequency', ''),
                'sampling_require': param.get('sampling_require', ''),
                'inspection_require': param.get('inspection_require', ''),
                'required_info': param.get('required_info', ''),
                'standards': param.get('standards', ''),
                'remark': remark
            }
            
            # 处理所有字段的空值，将None、'null'等转换为空字符串
            for key, value in transformed_item.items():
                if value is None or value == 'null' or value == 'None':
                    transformed_item[key] = ''
            
            transformed_data.append(transformed_item)
        
        return transformed_data
    
    def _estimate_text_width(self, text: str, font_size: int) -> int:
        """
        估算文本宽度
        
        :param text: 文本内容
        :param font_size: 当前字体大小
        :return: 估算的宽度（像素）
        """
        width = 0
        for char in text:
            # 更准确的字符宽度估算
            if '\u4e00' <= char <= '\u9fff':
                # 中文字符，完整宽度
                width += font_size
            elif char.isdigit():
                # 数字，稍宽一点
                width += font_size * 0.6
            elif char.isalpha():
                # 英文字母
                width += font_size * 0.5
            else:
                # 其他字符
                width += font_size * 0.4
        return width
    
    def _split_text_to_lines(self, text: str, max_width: int, font_size: int) -> int:
        """
        将文本按最大宽度分割成多行，返回需要的行数
        
        :param text: 文本内容
        :param max_width: 最大宽度（像素）
        :param font_size: 当前字体大小
        :return: 需要的行数
        """
        if not text:
            return 1
        
        lines = str(text).split('\n')
        total_lines = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                total_lines += 1
                continue
            
            # 估算当前行的宽度
            line_width = self._estimate_text_width(line, font_size)
            
            if line_width <= max_width:
                total_lines += 1
            else:
                # 需要自动换行，计算需要的行数
                # 简化处理：按字符数比例计算
                estimated_lines = int(line_width / max_width) + 1
                total_lines += estimated_lines
        
        return total_lines
    
    def wrap_text(self, text: str, device_type: str = 'pc', col_idx: int = 0) -> str:
        """
        对文本进行自动换行处理，在需要换行的地方添加换行符
        
        :param text: 要处理的文本
        :param device_type: 设备类型，可选值：'pc'、'tablet'、'phone'
        :param col_idx: 列索引（0-7）
        :return: 处理后的文本，包含适当的换行符
        """
        # 确保text是字符串类型
        text = str(text) if text is not None else ''
        if not text:
            return text
        
        # 获取设备对应的列宽
        if device_type == 'tablet':
            col_width = self.tablet_col_widths[col_idx]
        elif device_type == 'phone':
            col_width = self.phone_col_widths[col_idx]
        else:
            col_width = self.pc_col_widths[col_idx]
        
        # 获取设备对应的字体大小
        device_font_sizes = {
            'pc': 12,
            'tablet': 10,
            'phone': 8
        }
        font_size = device_font_sizes.get(device_type, 12)
        
        # 计算可用宽度：列宽 - 4 * 边距，增加一些安全边距
        available_width = col_width - self.text_margin * 4
        
        # 添加一个缩放因子，确保估算宽度有安全余量
        available_width *= 0.95
        
        # 处理文本中的手动换行符
        paragraphs = text.split('\n')
        wrapped_paragraphs = []
        
        for paragraph in paragraphs:
            # 保留原始文本的换行结构，不使用strip()移除空格
            if not paragraph:
                # 保留空行
                wrapped_paragraphs.append('')
                continue
            
            # 开始自动换行
            wrapped_line = ''
            current_line = ''
            
            # 逐字符处理
            for char in paragraph:
                test_line = current_line + char
                test_width = self._estimate_text_width(test_line, font_size)
                
                if test_width <= available_width:
                    current_line = test_line
                else:
                    # 当前行已满，添加到结果中
                    wrapped_line += current_line + '\n'
                    current_line = char
            
            # 添加最后一行
            if current_line:
                wrapped_line += current_line
            
            wrapped_paragraphs.append(wrapped_line)
        
        # 重新组合段落
        wrapped_text = '\n'.join(wrapped_paragraphs)
        
        return wrapped_text
    
    def clean_duplicate_adjacent_cells(self, data: List[dict]) -> List[dict]:
        """
        二次清洗数据，移除相邻行中同一字段的重复值
        
        :param data: 经过transform_detection_data处理后的列表
        :return: 二次清洗后的新列表
        """
        if not data:
            return []
        
        # 需要处理的字段列表
        fields_to_process = [
            'sampling_batch', 'sampling_frequency', 'sampling_require',
            'inspection_require', 'required_info', 'standards', 'remark'
        ]
        
        # 创建结果列表，深拷贝第一行数据
        result = [dict(data[0])]
        
        # 处理第一行的空值
        for field in fields_to_process:
            if result[0].get(field) is None or result[0].get(field) == 'null' or result[0].get(field) == 'None':
                result[0][field] = ''
        
        # 记录每个字段的最近非空值
        last_non_empty_values = {}
        for field in fields_to_process:
            last_non_empty_values[field] = result[0].get(field)
        
        # 从第二行开始处理
        for i in range(1, len(data)):
            # 深拷贝当前行
            current_row = dict(data[i])
            
            # 遍历需要处理的字段
            for field in fields_to_process:
                current_value = current_row.get(field)
                # 处理当前值的空值
                if current_value is None or current_value == 'null' or current_value == 'None':
                    current_value = ''
                    current_row[field] = ''
                
                # 如果当前字段值与最近非空值相同，则置空
                if current_value == last_non_empty_values.get(field):
                    current_row[field] = ''
                else:
                    # 更新最近非空值
                    last_non_empty_values[field] = current_value
            
            # 添加处理后的行到结果列表
            result.append(current_row)
        
        return result
    
    def calculate_row_heights(self, data: List[dict], device_type: str = 'pc') -> tuple:
        """
        计算每行的高度，考虑内容换行和合并单元格情况
        
        :param data: 经过二次清洗后的数据列表
        :param device_type: 设备类型，可选值：'pc'、'tablet'、'phone'
        :return: (行高列表, 合并单元格列表)
                 合并单元格列表格式：[(start_row, end_row, col_idx), ...]
                 表示从第start_row行到第end_row行的第col_idx列需要合并
        """
        if not data:
            return [], []
        
        # 不同设备对应的字体大小配置
        device_font_sizes = {
            'pc': 12,
            'tablet': 10,
            'phone': 8
        }
        
        font_size = device_font_sizes.get(device_type, 12)
        num_rows = len(data)
        num_cols = 8  # 固定8列
        
        # 1. 计算每个单元格的基础高度（考虑换行符和自动换行）
        base_cell_heights = []
        for row_idx in range(num_rows):
            row = data[row_idx]
            row_heights = []
            for col_idx, field in enumerate(['param_name', 'sampling_batch', 'sampling_frequency', 
                                           'sampling_require', 'inspection_require', 'required_info', 
                                           'standards', 'remark']):
                value = row.get(field, '')
                # 处理空值，确保所有空值都转换为空字符串
                if value is None or value == 'null' or value == 'None':
                    value = ''
                
                # 对文本进行自动换行处理
                wrapped_text = self.wrap_text(value, device_type, col_idx)
                
                # 计算需要的行数
                lines = wrapped_text.split('\n')
                # 过滤空行
                non_empty_lines = [line for line in lines if line.strip()]
                num_lines = len(non_empty_lines) if non_empty_lines else 1
                
                # 计算单元格高度：行高 * 行数 + 上下边距
                cell_height = int(font_size * self.line_spacing * num_lines + self.text_margin * 2)
                row_heights.append(cell_height)
            base_cell_heights.append(row_heights)
        
        # 2. 识别合并单元格范围
        merged_cells = []
        
        for col_idx in range(num_cols):
            current_merge_start = None
            for row_idx in range(num_rows):
                # 正确获取字段名
                field_names = ['param_name', 'sampling_batch', 'sampling_frequency', 
                              'sampling_require', 'inspection_require', 'required_info', 
                              'standards', 'remark']
                field = field_names[col_idx]
                # 获取当前单元格值并处理空值
                value = data[row_idx].get(field, '')
                if value is None or value == 'null' or value == 'None':
                    value = ''
                
                if value == '' and row_idx > 0:
                    # 当前单元格为空，需要合并
                    if current_merge_start is None:
                        current_merge_start = row_idx - 1
                else:
                    # 当前单元格有值，结束之前的合并
                    if current_merge_start is not None:
                        # 记录合并单元格信息
                        merged_cells.append((current_merge_start, row_idx - 1, col_idx))
                        current_merge_start = None
            
            # 处理列末尾的合并
            if current_merge_start is not None:
                merged_cells.append((current_merge_start, num_rows - 1, col_idx))
        
        # 3. 初始化每行高度为该行非合并单元格的最大高度
        row_heights = []
        for row_idx in range(num_rows):
            # 初始化max_height为0
            max_height = 0
            for col_idx in range(num_cols):
                # 检查当前单元格是否需要合并
                is_merged = any(start <= row_idx <= end and col == col_idx for start, end, col in merged_cells)
                if not is_merged or any(start == row_idx and col == col_idx for start, end, col in merged_cells):
                    # 非合并单元格或合并起始单元格，计算高度
                    max_height = max(max_height, base_cell_heights[row_idx][col_idx])
            # 确保至少有一个默认高度
            if max_height == 0:
                max_height = int(font_size * 1.2 + 2)
            row_heights.append(max_height)
        
        # 4. 迭代调整行高，直到所有合并单元格都满足高度要求
        max_iterations = 10  # 最大迭代次数，防止无限循环
        for _ in range(max_iterations):
            adjusted = False
            
            for start_row, end_row, col_idx in merged_cells:
                # 计算合并单元格需要的总高度
                required_height = base_cell_heights[start_row][col_idx]
                # 计算当前合并区域的总高度
                current_total_height = sum(row_heights[start_row:end_row+1])
                
                if required_height > current_total_height:
                    # 需要增加的高度
                    extra_height = required_height - current_total_height
                    # 计算合并行数
                    merge_rows = end_row - start_row + 1
                    # 平均分配额外高度
                    extra_per_row = extra_height // merge_rows
                    remainder = extra_height % merge_rows
                    
                    # 调整合并区域内的行高
                    for i in range(start_row, end_row+1):
                        row_heights[i] += extra_per_row
                        if remainder > 0:
                            row_heights[i] += 1
                            remainder -= 1
                    
                    adjusted = True
            
            if not adjusted:
                # 没有调整，说明已经达到稳定状态
                break
        
        # 5. 确保每行高度至少为最小行高，根据设备类型设置不同的最低行高
        if device_type == 'pc':
            min_row_height = 20
        elif device_type == 'tablet':
            min_row_height = 30
        else:  # phone
            min_row_height = 25
        row_heights = [max(height, min_row_height) for height in row_heights]
        
        return row_heights, merged_cells


# 导出实例化的数据处理器，便于直接调用
detection_data_processor = DetectionDataProcessor()