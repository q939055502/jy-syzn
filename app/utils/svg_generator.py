# SVG生成工具
# 用于生成检测参数的SVG表格，不依赖数据库

import sys
import os

# 添加项目根目录到Python路径，确保可以直接运行该脚本
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

import logging
from typing import List, Dict, Optional
from app.utils.detection_data_processor import DetectionDataProcessor

# 创建日志记录器
logger = logging.getLogger(__name__)


class SVGGenerator:
    """
    SVG生成器类，用于生成检测参数的SVG表格
    """
    
    def __init__(self):
        """
        初始化SVG生成器
        """
        # 使用数据处理器处理数据
        self.data_processor = DetectionDataProcessor()
        
        # 表头配置
        self.headers = [
            '参数/单价',
            '组批规则',
            '取样频率',
            '取样要求',
            '送检要求',
            '所需信息',
            '检评规范',
            '备注'
        ]
        
        # 不同设备的表格宽度配置
        self.pc_width = 1200
        self.tablet_width = 768
        self.phone_width = 375
        
        # 默认使用电脑端宽度
        self.width = self.pc_width
        
        # 边距设置
        self.margin = 2
        
        # 不同设备对应的列宽度配置
        # 格式：[参数/单价, 组批规则, 取样频率, 取样要求, 送检要求, 所需信息, 检评规范, 备注]
        # PC端：1200px宽度，分配8列
        self.pc_col_widths = [120, 130, 130, 130, 130, 150, 150, 130]
        # 平板端：768px宽度，分配8列
        self.tablet_col_widths = [80, 90, 90, 90, 90, 100, 100, 98]
        # 手机端：375px宽度，分配8列
        self.phone_col_widths = [40, 45, 45, 45, 45, 50, 50, 55]
        
        # 默认使用PC端列宽
        self.col_widths = self.pc_col_widths
        
        # 不同设备的字体大小配置
        self.pc_font_size = 12
        self.tablet_font_size = 10
        self.phone_font_size = 8
        
        # 不同设备的表头字体大小配置
        self.pc_header_font_size = 16
        self.tablet_header_font_size = 14
        self.phone_header_font_size = 8
        
        # 默认使用PC端字体大小
        self.font_size = self.pc_font_size
        self.header_font_size = self.pc_header_font_size
        
        # 表格基础配置
        self.header_height = 40
        self.line_spacing = 1.2
        self.text_margin = 1  # 文字与边框距离尽可能最小、紧凑
        
        # 水印配置
        self.watermark_text = "我是水印"
        self.watermark_color = "#888888"
        self.watermark_opacity = 0.3
        self.watermark_rotation = 30
        self.watermark_size = 14
        self.watermark_horizontal_spacing = 100
        self.watermark_vertical_spacing = 80
        self.watermark_font = "Arial"
    
    def transform_detection_data(self, params: List[dict]) -> List[dict]:
        """
        转换检测数据，按规则提取和转换字段
        :param params: 检测参数列表
        :return: 转换后的新列表
        """
        return self.data_processor.transform_detection_data(params)
    
    def clean_duplicate_adjacent_cells(self, data: List[dict]) -> List[dict]:
        """
        二次清洗数据，移除相邻行中同一字段的重复值
        :param data: 经过transform_detection_data处理后的列表
        :return: 二次清洗后的新列表
        """
        return self.data_processor.clean_duplicate_adjacent_cells(data)
    
    def generate_svg(self, data: List[dict], device_type: str = 'pc') -> str:
        """
        生成SVG表格
        :param data: 经过二次清洗后的数据列表
        :param device_type: 设备类型，可选值：'pc'、'tablet'、'phone'
        :return: SVG字符串
        """
        # 根据设备类型设置宽度、列宽和字体大小
        if device_type == 'tablet':
            self.width = self.tablet_width
            col_widths = self.tablet_col_widths
            font_size = self.tablet_font_size
            header_font_size = self.tablet_header_font_size
        elif device_type == 'phone':
            self.width = self.phone_width
            col_widths = self.phone_col_widths
            font_size = self.phone_font_size
            header_font_size = self.phone_header_font_size
        else:
            self.width = self.pc_width
            col_widths = self.pc_col_widths
            font_size = self.pc_font_size
            header_font_size = self.pc_header_font_size
        
        # 使用类的基础配置
        header_height = self.header_height
        line_spacing = self.line_spacing
        text_margin = self.text_margin
        
        # 可用宽度（减去边距）
        available_width = self.width - 2 * self.margin
        
        # 调整列宽，确保总和等于可用宽度
        col_width_sum = sum(col_widths)
        if col_width_sum < available_width:
            # 调整最后一列宽度，填补空白
            col_widths[-1] += (available_width - col_width_sum)
        
        # 计算每行的高度和合并单元格信息
        row_heights, merged_cells = self.calculate_row_heights(data, device_type)
        
        # 计算表格总高度
        total_height = self.margin + header_height + sum(row_heights) + self.margin
        
        # 创建SVG模板
        svg_template = f'<?xml version="1.0" encoding="UTF-8"?>' + '\n'
        svg_template += f'<svg width="{self.width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">' + '\n'
        # 透明背景：移除白色背景矩形
        svg_template += f'    <!-- 表格外边框 -->' + '\n'
        svg_template += f'    <rect x="{self.margin}" y="{self.margin}" width="{available_width}" height="{total_height - 2 * self.margin}" fill="none" stroke="black" stroke-width="1"/>' + '\n'
        
        # 绘制表头
        header_y = self.margin
        current_x = self.margin
        for header, col_width in zip(self.headers, col_widths):
            # 表头单元格背景 - 透明
            svg_template += f'    <rect x="{current_x}" y="{header_y}" width="{col_width}" height="{header_height}" fill="none" stroke="black" stroke-width="1"/>' + '\n'
            # 表头文本（居中，加粗，使用动态字体大小）
            text_x = current_x + col_width // 2
            # 表头文本垂直居中，考虑字体基线
            text_y = header_y + header_height // 2 + header_font_size * 0.3
            svg_template += f'    <text x="{text_x}" y="{text_y}" font-family="Arial" font-size="{header_font_size}" font-weight="bold" fill="black" text-anchor="middle">{header}</text>' + '\n'
            current_x += col_width
        
        # 绘制数据行
        data_y = header_y + header_height
        
        for row_idx, row in enumerate(data):
            current_x = self.margin
            current_row_height = row_heights[row_idx]
            
            # 绘制数据行单元格
            for col_idx, col_width in enumerate(col_widths):
                # 检查当前单元格是否是合并单元格的一部分
                is_merged = any(start <= row_idx <= end and col == col_idx for start, end, col in merged_cells)
                
                # 只绘制非合并单元格或合并单元格的第一个单元格
                if not is_merged or any(start == row_idx and col == col_idx for start, end, col in merged_cells):
                    # 检查是否需要跨行绘制
                    merge_info = None
                    for start, end, col in merged_cells:
                        if start == row_idx and col == col_idx:
                            merge_info = (start, end, col)
                            break
                    
                    # 计算单元格高度
                    cell_height = current_row_height
                    if merge_info:
                        # 合并单元格，计算跨行高度
                        merge_start, merge_end, _ = merge_info
                        cell_height = sum(row_heights[merge_start:merge_end+1])
                    
                    # 绘制单元格
                    svg_template += f'    <rect x="{current_x}" y="{data_y}" width="{col_width}" height="{cell_height}" fill="none" stroke="black" stroke-width="1"/>' + '\n'
                
                current_x += col_width
            
            # 绘制数据行文本
            current_x = self.margin
            
            # 获取所有字段值
            all_fields = [
                row.get('param_name', ''),
                row.get('sampling_batch', ''),
                row.get('sampling_frequency', ''),
                row.get('sampling_require', ''),
                row.get('inspection_require', ''),
                row.get('required_info', ''),
                row.get('standards', ''),
                row.get('remark', '')
            ]
            
            for col_idx, (value, col_width) in enumerate(zip(all_fields, col_widths)):
                # 检查当前单元格是否是合并单元格的一部分
                is_merged = any(start <= row_idx <= end and col == col_idx for start, end, col in merged_cells)
                
                # 只绘制非合并单元格或合并单元格的第一个单元格的文本
                if not is_merged or any(start == row_idx and col == col_idx for start, end, col in merged_cells):
                    # 计算文本起始Y坐标（垂直居中）
                    # 检查是否是合并单元格
                    merge_info = None
                    for start, end, col in merged_cells:
                        if start == row_idx and col == col_idx:
                            merge_info = (start, end, col)
                            break
                    
                    # 计算合并单元格的总高度
                    if merge_info:
                        merge_start, merge_end, _ = merge_info
                        cell_height = sum(row_heights[merge_start:merge_end+1])
                    else:
                        cell_height = current_row_height
                    
                    # 对文本进行自动换行处理
                    wrapped_text = self.wrap_text(value, device_type, col_idx)
                    
                    # 计算文本的行数
                    lines = wrapped_text.split('\n')
                    non_empty_lines = [line for line in lines if line.strip()]
                    num_lines = len(non_empty_lines) if non_empty_lines else 1
                    
                    # SVG文本垂直居中计算
                    # 1. 计算单行高度（包括行间距）
                    line_height = font_size * self.line_spacing
                    # 2. 计算所有文本的总高度
                    total_text_height = num_lines * line_height
                    # 3. 计算垂直居中位置
                    # 文本块顶部位置 = 单元格顶部 + (单元格高度 - 文本总高度) / 2
                    text_block_top = data_y + (cell_height - total_text_height) / 2
                    
                    # 处理文本颜色（第一列根据is_regular_param设置）
                    if col_idx == 0:
                        is_regular_param = row.get('is_regular_param', 0)
                        # 确保is_regular_param是整数
                        try:
                            is_regular_param = int(is_regular_param)
                        except (ValueError, TypeError):
                            is_regular_param = 0
                        is_regular = is_regular_param == 1
                        text_color = 'red' if is_regular else 'black'
                    else:
                        text_color = 'black'
                    
                    # 绘制每一行文本
                    for i, line in enumerate(non_empty_lines):
                        if not line.strip():
                            continue
                        
                        # 计算当前行的Y坐标
                        # 每行的基线位置 = 文本块顶部 + 行高 * (i + 0.7)
                        # 0.7是一个经验值，表示行内文本基线相对于行高的位置
                        text_x = current_x + col_width // 2
                        text_y = text_block_top + line_height * (i + 0.7)
                        svg_template += f'    <text x="{text_x}" y="{text_y}" font-family="Arial" font-size="{font_size}" fill="{text_color}" text-anchor="middle">{line}</text>' + '\n'
                
                current_x += col_width
            
            # 移动到下一行
            data_y += current_row_height
        
        svg_template += '</svg>'
        
        return svg_template
    
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
        
        # 获取设备对应的列宽和字体大小
        if device_type == 'tablet':
            col_width = self.tablet_col_widths[col_idx]
            font_size = self.tablet_font_size
        elif device_type == 'phone':
            col_width = self.phone_col_widths[col_idx]
            font_size = self.phone_font_size
        else:
            col_width = self.pc_col_widths[col_idx]
            font_size = self.pc_font_size
        
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
    
    def calculate_row_heights(self, data: List[dict], device_type: str = 'pc') -> tuple:
        """
        计算每行的高度，考虑内容换行和合并单元格情况
        :param data: 经过二次清洗后的数据列表
        :param device_type: 设备类型，可选值：'pc'、'tablet'、'phone'
        :return: (行高列表, 合并单元格列表)
                 合并单元格列表格式：[(start_row, end_row, col_idx), ...]
                 表示从第start_row行到第end_row行的第col_idx列需要合并
        """
        return self.data_processor.calculate_row_heights(data, device_type)
    
    def save_svg(self, svg_content: str, filename: str = 'test_table.svg') -> None:
        """
        保存SVG内容到文件
        :param svg_content: SVG字符串内容
        :param filename: 文件名，默认为test_table.svg
        :return: None
        """
        import os
        # 保存到项目根目录
        file_path = os.path.join(os.getcwd(), filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        logger.info(f'SVG文件已保存到：{file_path}')
    
    def add_text_watermark_to_svg(self, svg_str: str) -> str:
        """
        向SVG字符串添加文字水印
        :param svg_str: 原始SVG字符串
        :return: 添加水印后的SVG字符串
        """
        import re
        
        # 1. 解析SVG尺寸
        # 优先从width和height属性获取尺寸
        width_match = re.search(r'width="(\d+)"', svg_str)
        height_match = re.search(r'height="(\d+)"', svg_str)
        
        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
        else:
            # 从viewBox获取尺寸
            viewBox_match = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_str)
            if viewBox_match:
                width = int(viewBox_match.group(1))
                height = int(viewBox_match.group(2))
            else:
                # 默认尺寸
                width = self.width
                height = 1000
        
        # 2. 生成水印文本标签
        watermark_tags = []
        
        # 从负的间距开始，确保整个区域都被水印覆盖
        start_x = -self.watermark_horizontal_spacing
        start_y = -self.watermark_vertical_spacing
        
        # 计算需要生成多少行和列水印
        # 增加额外的一行一列，确保边缘区域也被覆盖
        cols = int(width / self.watermark_horizontal_spacing) + 2
        rows = int(height / self.watermark_vertical_spacing) + 2
        
        for i in range(rows):
            for j in range(cols):
                # 计算当前水印的坐标
                x = start_x + j * self.watermark_horizontal_spacing
                y = start_y + i * self.watermark_vertical_spacing
                
                # 构建水印标签
                watermark_tag = f'    <text x="{x}" y="{y}" font-family="{self.watermark_font}" font-size="{self.watermark_size}" '
                watermark_tag += f'fill="{self.watermark_color}" opacity="{self.watermark_opacity}" '
                watermark_tag += f'transform="rotate({self.watermark_rotation}, {x}, {y})" text-anchor="middle">'
                watermark_tag += f'{self.watermark_text}</text>'
                
                watermark_tags.append(watermark_tag)
        
        # 3. 将水印标签插入到SVG的</svg>标签之前
        watermark_svg = svg_str.replace('</svg>', '\n'.join(watermark_tags) + '\n</svg>')
        
        return watermark_svg
    
    def add_anti_crawl_watermark(self, svg_str: str, **kwargs) -> str:
        """
        向SVG添加防爬水印和噪点，采用多层防御策略
        :param svg_str: 原始SVG字符串
        :param kwargs: 可选配置参数
        :return: 添加防爬水印后的SVG字符串
        """
        import re
        import random
        import math
        
        # 1. 解析SVG尺寸
        width_match = re.search(r'width="(\d+)"', svg_str)
        height_match = re.search(r'height="(\d+)"', svg_str)
        
        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
        else:
            viewBox_match = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_str)
            if viewBox_match:
                width = int(viewBox_match.group(1))
                height = int(viewBox_match.group(2))
            else:
                width = self.width
                height = 1000
        
        # 配置参数
        config = {
            'noise_density': kwargs.get('noise_density', 0.01),  # 噪点密度
            'noise_opacity': kwargs.get('noise_opacity', 0.1),  # 噪点透明度
            'add_grid': kwargs.get('add_grid', True),  # 是否添加网格
            'grid_opacity': kwargs.get('grid_opacity', 0.05),  # 网格透明度
            'add_fake_elements': kwargs.get('add_fake_elements', True),  # 是否添加虚假元素
            'fake_elements_count': kwargs.get('fake_elements_count', 5),  # 虚假元素数量
            'add_signature': kwargs.get('add_signature', True),  # 是否添加签名
            'signature_text': kwargs.get('signature_text', 'anti-crawl-protected'),  # 签名文本
            **kwargs
        }
        
        # 生成防爬水印标签
        anti_crawl_tags = []
        
        # 2. 添加随机噪点
        noise_count = int(width * height * config['noise_density'])
        for _ in range(noise_count):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.uniform(0.5, 2)
            opacity = random.uniform(config['noise_opacity'] * 0.5, config['noise_opacity'] * 1.5)
            # 随机选择噪点类型
            if random.random() < 0.5:
                # 小圆点
                noise_tag = f'    <circle cx="{x}" cy="{y}" r="{size}" fill="#000000" fill-opacity="{opacity}" />'
            else:
                # 短线条
                angle = random.uniform(0, 360)
                length = random.uniform(1, 3)
                x2 = x + length * math.cos(math.radians(angle))
                y2 = y + length * math.sin(math.radians(angle))
                noise_tag = f'    <line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-opacity="{opacity}" stroke-width="{size}" />'
            anti_crawl_tags.append(noise_tag)
        
        # 3. 添加透明网格
        if config['add_grid']:
            grid_spacing = 50
            for x in range(0, width + grid_spacing, grid_spacing):
                anti_crawl_tags.append(f'    <line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#000000" stroke-opacity="{config["grid_opacity"]}" stroke-width="0.5" />')
            for y in range(0, height + grid_spacing, grid_spacing):
                anti_crawl_tags.append(f'    <line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#000000" stroke-opacity="{config["grid_opacity"]}" stroke-width="0.5" />')
        
        # 4. 添加虚假元素（增加SVG复杂度）
        if config['add_fake_elements']:
            for _ in range(config['fake_elements_count']):
                x = random.randint(0, width)
                y = random.randint(0, height)
                # 随机选择虚假元素类型
                element_type = random.choice(['rect', 'path', 'ellipse', 'polygon'])
                if element_type == 'rect':
                    w = random.uniform(10, 50)
                    h = random.uniform(10, 50)
                    fake_tag = f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#000000" stroke-opacity="0.05" stroke-width="0.5" />'
                elif element_type == 'ellipse':
                    rx = random.uniform(5, 25)
                    ry = random.uniform(5, 25)
                    fake_tag = f'    <ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="none" stroke="#000000" stroke-opacity="0.05" stroke-width="0.5" />'
                elif element_type == 'polygon':
                    points = []
                    for _ in range(3, 7):
                        px = x + random.uniform(-20, 20)
                        py = y + random.uniform(-20, 20)
                        points.append(f'{px},{py}')
                    points_str = ' '.join(points)
                    fake_tag = f'    <polygon points="{points_str}" fill="none" stroke="#000000" stroke-opacity="0.05" stroke-width="0.5" />'
                else:  # path
                    path_data = f'M{x},{y} C{x+10},{y-10} {x+20},{y+10} {x+30},{y}'
                    fake_tag = f'    <path d="{path_data}" fill="none" stroke="#000000" stroke-opacity="0.05" stroke-width="0.5" />'
                anti_crawl_tags.append(fake_tag)
        
        # 5. 添加隐藏签名
        if config['add_signature']:
            # 隐藏在边缘位置，透明度极低
            signature_tag = f'    <text x="{width - 50}" y="{height - 5}" font-family="Arial" font-size="3" fill="#000000" fill-opacity="0.01" text-anchor="end">'
            signature_tag += f'{config["signature_text"]}</text>'
            anti_crawl_tags.append(signature_tag)
        
        # 6. 添加混淆代码（SVG注释中的混淆文本）
        confusion_text = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=100))
        confusion_tag = f'    <!-- {confusion_text} -->'
        anti_crawl_tags.append(confusion_tag)
        
        # 7. 将防爬水印标签插入到SVG的</svg>标签之前
        anti_crawl_svg = svg_str.replace('</svg>', '\n'.join(anti_crawl_tags) + '\n</svg>')
        
        return anti_crawl_svg


# 导出实例化的生成器，便于直接调用
svg_generator = SVGGenerator()


# 测试代码，仅在直接运行时执行
if __name__ == "__main__":
    # 测试数据
    test_params = [
        {
            "is_regular_param": 0,
            "param_name": "凝结时间",
            "price": "30.00元/组",
            "sampling_batch": "每批次≤500吨取1组99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999",
            "sampling_frequency": "123456",
            "sampling_require": "需使用无菌采样袋，采样量≥500g",
            "inspection_require": "abcd",
            "required_info": "产品名称、批次号、生产日期、规格",
            "report_time": "常规5个工作日，加急3个工作日",
            "standards": "通用硅酸盐水泥\nGB 175-2023",
            "template_code": "SN-2024-001"
        },
        {
            "is_regular_param": 1,
            "param_name": "安定性",
            "price": "25.00元/组",
            "sampling_batch": "每批次≤5000吨取1组",
            "sampling_frequency": "123456",
            "sampling_require": "需使用无菌采样袋，采样量≥500g",
            "inspection_require": "abcd",
            "required_info": "产品名称、批次号、生产日期、规格",
            "report_time": "常规5个工作日，加急3个工作日",
            "standards": "通用硅酸盐水泥\nGB 175-2023",
            "template_code": "SN-2024-001"
        },
        {
            "is_regular_param": 1,
            "param_name": "抗压强度",
            "price": "50.00元/组",
            "sampling_batch": "每批次≤5000吨取1组",
            "sampling_frequency": "每月1次",
            "sampling_require": "需使用无菌采样袋，采样量≥1000g",
            "inspection_require": "需低温保存",
            "required_info": "产品名称、批次号、生产日期、规格",
            "report_time": "常规7个工作日，加急3个工作日",
            "standards": "通用硅酸盐水泥\nGB 175-2023\nGB 175-2023",
            "template_code": "SN-2024-002"
        }
    ]
    
    # 转换数据
    transformed_data = svg_generator.transform_detection_data(test_params)
    
    # 二次清洗数据
    cleaned_data = svg_generator.clean_duplicate_adjacent_cells(transformed_data)
    
    # 计算不同设备类型的行高
    device_types = ['pc', 'tablet', 'phone']
    for device in device_types:
        row_heights, merged_cells = svg_generator.calculate_row_heights(cleaned_data, device)
        print(f"{device.upper()}端计算得到的行高：")
        for i, height in enumerate(row_heights):
            print(f"第{i+1}行：{height}px")
        print(f"合并单元格信息：{merged_cells}")
        print()
    print("="*50 + "\n")
    
    # 生成SVG并保存
    svg_content = svg_generator.generate_svg(cleaned_data)
    # 在保存之前添加水印
    svg_content_with_watermark = svg_generator.add_text_watermark_to_svg(svg_content)
    # 添加防爬水印和噪点
    svg_content_with_anti_crawl = svg_generator.add_anti_crawl_watermark(svg_content_with_watermark)
    svg_generator.save_svg(svg_content_with_anti_crawl)
    print("SVG文件已生成并保存到项目根目录下的test_table.svg")
    
    # 生成平板端SVG
    tablet_svg = svg_generator.generate_svg(cleaned_data, device_type='tablet')
    # 在保存之前添加水印
    tablet_svg_with_watermark = svg_generator.add_text_watermark_to_svg(tablet_svg)
    # 添加防爬水印和噪点
    tablet_svg_with_anti_crawl = svg_generator.add_anti_crawl_watermark(tablet_svg_with_watermark)
    svg_generator.save_svg(tablet_svg_with_anti_crawl, "test_table_tablet.svg")
    print("平板端SVG文件已生成并保存到项目根目录下的test_table_tablet.svg")
    
    # 生成手机端SVG
    phone_svg = svg_generator.generate_svg(cleaned_data, device_type='phone')
    # 在保存之前添加水印
    phone_svg_with_watermark = svg_generator.add_text_watermark_to_svg(phone_svg)
    # 添加防爬水印和噪点
    phone_svg_with_anti_crawl = svg_generator.add_anti_crawl_watermark(phone_svg_with_watermark)
    svg_generator.save_svg(phone_svg_with_anti_crawl, "test_table_phone.svg")
    print("手机端SVG文件已生成并保存到项目根目录下的test_table_phone.svg")
