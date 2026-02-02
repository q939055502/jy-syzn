# 数据直接生成PNG图片工具
# 用于将检测参数数据直接转换为PNG图片，不经过SVG中间步骤

import logging
import os
import sys
from typing import List, Dict, Optional
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到Python路径，确保直接运行时能正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
# 项目根目录是d:\Projects\jy_syzn，需要向上两级目录
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from app.utils.detection_data_processor import DetectionDataProcessor

# 创建日志记录器
logger = logging.getLogger(__name__)


class DataToPNGDirectConverter:
    """
    数据直接转PNG转换器类，用于将检测参数数据直接转换为PNG图片
    """
    
    def __init__(self):
        """
        初始化数据直接转PNG转换器
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
        
        # 不同设备对应的列宽度配置
        # 格式：[参数/单价, 组批规则, 取样频率, 取样要求, 送检要求, 所需信息, 检评规范, 备注]
        self.device_col_widths = {
            'pc': [120, 130, 130, 130, 130, 150, 150, 130],
            'tablet': [80, 90, 90, 90, 90, 100, 100, 98],
            'phone': [40, 45, 45, 45, 45, 50, 50, 55]
        }
        
        # 不同设备的字体大小配置
        self.device_font_sizes = {
            'pc': 12,
            'tablet': 10,
            'phone': 8
        }
        
        # 不同设备的表头字体大小配置
        self.device_header_font_sizes = {
            'pc': 16,
            'tablet': 14,
            'phone': 8
        }
        
        # 表格基础配置
        self.header_height = 40
        self.line_spacing = 1.2
        self.text_margin = 5  # 文字与边框距离
        self.margin = 2  # 表格外边框边距
    
    def convert_data_to_png(self, params: List[dict], device_type: str = 'pc') -> bytes:
        """
        将检测参数数据直接转换为PNG图片
        
        :param params: 检测参数列表
        :param device_type: 设备类型，可选值：'pc'、'tablet'、'phone'
        :return: PNG二进制数据
        """
        # 1. 转换检测数据
        transformed_data = self.data_processor.transform_detection_data(params)
        
        # 2. 清洗重复相邻单元格
        cleaned_data = self.data_processor.clean_duplicate_adjacent_cells(transformed_data)
        
        # 3. 计算行高和合并单元格信息
        row_heights, merged_cells = self.data_processor.calculate_row_heights(cleaned_data, device_type)
        
        # 4. 获取设备相关配置
        width = getattr(self, f'{device_type}_width', self.pc_width)
        col_widths = self.device_col_widths.get(device_type, self.device_col_widths['pc'])
        font_size = self.device_font_sizes.get(device_type, 12)
        header_font_size = self.device_header_font_sizes.get(device_type, 16)
        
        # 调整列宽，确保总和等于可用宽度
        available_width = width - 2 * self.margin
        col_width_sum = sum(col_widths)
        if col_width_sum < available_width:
            # 调整最后一列宽度，填补空白
            col_widths[-1] += (available_width - col_width_sum)
        
        # 5. 计算表格总高度
        total_height = self.margin + self.header_height + sum(row_heights) + self.margin
        
        # 6. 创建空白图片
        image = Image.new('RGB', (width, total_height), color='white')
        draw = ImageDraw.Draw(image)
        
        # 7. 获取字体 - 优先使用支持中文的字体
        font = None
        header_font = None
        bold_header_font = None
        
        # 尝试使用Windows系统中文字体，指定完整路径
        windows_font_dir = 'C:/Windows/Fonts'
        chinese_fonts = {
            'hei': 'simhei.ttf',
            'song': 'simsun.ttc',
            'kai': 'simkai.ttf',
            'fangsong': 'simfang.ttf'
        }
        
        try:
            # 尝试加载黑体
            hei_font_path = os.path.join(windows_font_dir, chinese_fonts['hei'])
            if os.path.exists(hei_font_path):
                font = ImageFont.truetype(hei_font_path, font_size)
                header_font = ImageFont.truetype(hei_font_path, header_font_size)
                bold_header_font = ImageFont.truetype(hei_font_path, header_font_size)  # 黑体本身就是粗体
        except Exception as e:
            logger.warning(f'加载黑体失败: {e}')
        
        # 如果黑体加载失败，尝试宋体
        if font is None:
            try:
                song_font_path = os.path.join(windows_font_dir, chinese_fonts['song'])
                if os.path.exists(song_font_path):
                    font = ImageFont.truetype(song_font_path, font_size)
                    header_font = ImageFont.truetype(song_font_path, header_font_size)
                    bold_header_font = ImageFont.truetype(song_font_path, header_font_size)
            except Exception as e:
                logger.warning(f'加载宋体失败: {e}')
        
        # 如果中文字体都加载失败，尝试Arial
        if font is None:
            try:
                # 尝试使用Arial字体
                font = ImageFont.truetype('arial.ttf', font_size)
                header_font = ImageFont.truetype('arial.ttf', header_font_size)
                bold_header_font = ImageFont.truetype('arialbd.ttf', header_font_size)
            except Exception as e:
                logger.warning(f'加载Arial失败: {e}')
                # 使用默认字体作为最后备选
                font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                bold_header_font = ImageFont.load_default()
        
        # 8. 绘制表格外边框
        available_width = width - 2 * self.margin
        draw.rectangle(
            [self.margin, self.margin, self.margin + available_width, total_height - self.margin],
            outline='black',
            width=1,
            fill=None
        )
        
        # 9. 绘制表头
        header_y = self.margin
        current_x = self.margin
        for header, col_width in zip(self.headers, col_widths):
            # 绘制表头单元格
            draw.rectangle(
                [current_x, header_y, current_x + col_width, header_y + self.header_height],
                outline='black',
                width=1,
                fill=None
            )
            
            # 绘制表头文本
            text_bbox = draw.textbbox((0, 0), header, font=bold_header_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = current_x + col_width // 2 - text_width // 2
            text_y = header_y + self.header_height // 2 - text_height // 2
            draw.text(
                (text_x, text_y),
                header,
                font=bold_header_font,
                fill='black'
            )
            
            current_x += col_width
        
        # 10. 绘制数据行
        data_y = header_y + self.header_height
        
        for row_idx, row in enumerate(cleaned_data):
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
                    draw.rectangle(
                        [current_x, data_y, current_x + col_width, data_y + cell_height],
                        outline='black',
                        width=1,
                        fill=None
                    )
                
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
                    # 检查是否是合并单元格
                    merge_info = None
                    for start, end, col in merged_cells:
                        if start == row_idx and col == col_idx:
                            merge_info = (start, end, col)
                            break
                    
                    # 计算合并单元格的总高度
                    cell_height = current_row_height
                    if merge_info:
                        merge_start, merge_end, _ = merge_info
                        cell_height = sum(row_heights[merge_start:merge_end+1])
                    
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
                    
                    # 绘制文本，支持自动换行
                    self._draw_wrapped_text(
                        draw,
                        value,
                        (current_x, data_y, current_x + col_width, data_y + cell_height),
                        font,
                        text_color,
                        font_size,
                        self.line_spacing,
                        self.text_margin
                    )
                
                current_x += col_width
            
            # 移动到下一行
            data_y += current_row_height
        
        # 11. 添加水印
        logger.info(f"添加水印，图片尺寸: {width}x{total_height}")
        self._add_watermark(draw, width, total_height, font)
        logger.info("水印添加完成")
        
        # 12. 保存为PNG二进制数据
        png_data = BytesIO()
        image.save(png_data, format='PNG', dpi=(300, 300))
        png_data.seek(0)
        
        return png_data.getvalue()
    
    def _draw_wrapped_text(self, draw, text, box, font, color, font_size, line_spacing, margin):
        """
        在指定区域内绘制自动换行文本，支持中英文混合
        
        :param draw: ImageDraw对象
        :param text: 要绘制的文本
        :param box: 文本区域坐标 (x1, y1, x2, y2)
        :param font: 字体对象
        :param color: 文本颜色
        :param font_size: 字体大小
        :param line_spacing: 行间距
        :param margin: 边距
        """
        x1, y1, x2, y2 = box
        available_width = x2 - x1 - 2 * margin
        available_height = y2 - y1 - 2 * margin
        
        text = str(text) if text is not None else ''
        if not text:
            return
        
        # 处理手动换行符
        paragraphs = text.split('\n')
        all_lines = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                all_lines.append('')
                continue
            
            lines = []
            current_line = ''
            
            # 检查是否包含中文
            contains_chinese = any('\u4e00' <= char <= '\u9fff' for char in paragraph)
            
            if contains_chinese:
                # 中文文本：按字符处理
                for char in paragraph:
                    if char == ' ':
                        # 处理空格
                        test_line = current_line + char
                    else:
                        # 中文和其他字符
                        test_line = current_line + char
                    
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    test_width = bbox[2] - bbox[0]
                    
                    if test_width <= available_width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = char
                if current_line:
                    lines.append(current_line)
            else:
                # 英文文本：按单词处理
                words = paragraph.split()
                if words:
                    current_line = words[0]
                    
                    for word in words[1:]:
                        test_line = current_line + ' ' + word
                        bbox = draw.textbbox((0, 0), test_line, font=font)
                        test_width = bbox[2] - bbox[0]
                        
                        if test_width <= available_width:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word
                    lines.append(current_line)
            
            all_lines.extend(lines)
        
        # 过滤空行
        all_lines = [line for line in all_lines if line.strip()]
        if not all_lines:
            return
        
        # 计算文本高度
        line_height = int(font_size * line_spacing)
        total_text_height = len(all_lines) * line_height
        
        # 垂直居中
        text_y = y1 + margin + (available_height - total_text_height) // 2
        
        # 绘制每行文本
        for line in all_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x1 + margin + (available_width - text_width) // 2
            draw.text((text_x, text_y), line, font=font, fill=color)
            text_y += line_height
    
    def _add_watermark(self, draw, width, height, font):
        """
        添加水印到图片
        
        :param draw: ImageDraw对象
        :param width: 图片宽度
        :param height: 图片高度
        :param font: 字体对象
        """
        logger.info(f"开始添加水印，图片尺寸: {width}x{height}")
        
        watermark_text = "我是水印"
        
        # 使用合适的字体大小
        font_size = 16  # 使用12号字体，确保清晰可见
        logger.info(f"使用字体大小: {font_size}")
        
        # 尝试加载中文字体，适配不同操作系统
        watermark_font = None
        
        # 定义不同操作系统下的字体搜索路径
        font_paths = []
        
        # 根据操作系统添加字体路径
        if os.name == 'nt':  # Windows
            windows_font_dir = 'C:/Windows/Fonts'
            font_paths.extend([
                os.path.join(windows_font_dir, 'simhei.ttf'),   # 黑体
                os.path.join(windows_font_dir, 'simsun.ttc'),   # 宋体
                os.path.join(windows_font_dir, 'arial.ttf'),     # Arial
                os.path.join(windows_font_dir, 'calibri.ttf')    # Calibri
            ])
        else:  # Linux/macOS
            # Linux常见字体路径
            linux_font_dirs = ['/usr/share/fonts', '/usr/local/share/fonts', '~/.local/share/fonts']
            # 常见中文字体文件名
            chinese_fonts = ['simhei.ttf', 'simsun.ttc', 'wenquanyi.ttc', 'msyh.ttc', 'NotoSansSC-Regular.ttf']
            
            for font_dir in linux_font_dirs:
                for font_name in chinese_fonts:
                    font_paths.append(os.path.join(font_dir, font_name))
            
            # 添加一些通用字体
            font_paths.extend([
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
            ])
        
        # 尝试加载字体
        loaded = False
        for font_path in font_paths:
            try:
                # 处理~路径
                expanded_path = os.path.expanduser(font_path)
                if os.path.exists(expanded_path):
                    watermark_font = ImageFont.truetype(expanded_path, font_size)
                    logger.info(f"成功加载字体: {expanded_path}")
                    loaded = True
                    break
            except Exception as e:
                logger.warning(f"加载字体失败: {font_path}, {e}")
        
        # 如果所有字体都加载失败，使用默认字体
        if not loaded:
            watermark_font = ImageFont.load_default()
            logger.info("使用默认字体")
        
        # 加深水印颜色，同时保持适当透明度
        watermark_fill = (96, 96, 96, 80)  # 深灰色，透明度约31%，颜色更深更清晰
        
        # 计算水印文本大小
        text_bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 使用更简单可靠的方式实现斜向水印
        # 创建一个与水印文本大小匹配的临时图像
        import math
        angle = -30  # 向左倾斜30度
        
        # 计算旋转后所需的画布大小
        # 确保旋转后的水印能完整显示
        rotated_width = int(math.sqrt(text_width**2 + text_height**2))
        rotated_height = rotated_width
        
        # 计算水印间距
        spacing = 150
        
        # 直接在原始图像上绘制多个斜向水印
        # 不使用复杂的图层，确保稳定显示
        for y in range(0, height + spacing, spacing):
            for x in range(0, width + spacing, spacing):
                # 创建单个水印的临时图像
                single_watermark = Image.new('RGBA', (rotated_width, rotated_height), (255, 255, 255, 0))
                single_draw = ImageDraw.Draw(single_watermark)
                
                # 在临时图像中心绘制水印文本
                single_draw.text(
                    (rotated_width // 2, rotated_height // 2),
                    watermark_text,
                    font=watermark_font,
                    fill=watermark_fill,
                    anchor='mm'  # 中心对齐
                )
                
                # 旋转单个水印
                rotated = single_watermark.rotate(angle, expand=False, fillcolor=(255, 255, 255, 0))
                
                # 计算水印位置，确保均匀分布
                pos_x = x - rotated_width // 2
                pos_y = y - rotated_height // 2
                
                # 直接粘贴到原始图像上
                draw._image.paste(rotated, (pos_x, pos_y), rotated)
        
        logger.info("水印添加完成")
    
    def save_png_to_file(self, png_data: bytes, filename: str = 'test_table_direct.png') -> None:
        """
        将PNG二进制数据保存到文件
        
        :param png_data: PNG二进制数据
        :param filename: 文件名，默认为test_table_direct.png
        :return: None
        """
        import os
        # 保存到项目根目录
        file_path = os.path.join(os.getcwd(), filename)
        with open(file_path, 'wb') as f:
            f.write(png_data)
        logger.info(f"PNG文件已保存到：{file_path}")


# 导出实例化的转换器，便于直接调用
data_to_png_direct_converter = DataToPNGDirectConverter()


# 测试代码，仅在直接运行时执行
if __name__ == "__main__":
    # 测试数据
    test_params = [
        {
            "is_regular_param": 0,
            "param_name": "凝结时间",
            "price": "30.00元/组",
            "sampling_batch": "每批次≤500吨取1组",
            "sampling_frequency": None,
            "sampling_require": "需使用无菌采样袋，采样量≥500g",
            "inspection_require": None,
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
            "sampling_frequency": None,
            "sampling_require": "需使用无菌采样袋，采样量≥500g",
            "inspection_require": None,
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
    
    # 测试转换为PC端PNG
    print("生成PC端PNG...")
    pc_png = data_to_png_direct_converter.convert_data_to_png(test_params, device_type='pc')
    data_to_png_direct_converter.save_png_to_file(pc_png, "test_pc_direct.png")
    print("PC端PNG已生成并保存到项目根目录下的test_pc_direct.png")
    
    # 测试转换为平板端PNG
    print("\n生成平板端PNG...")
    tablet_png = data_to_png_direct_converter.convert_data_to_png(test_params, device_type='tablet')
    data_to_png_direct_converter.save_png_to_file(tablet_png, "test_tablet_direct.png")
    print("平板端PNG已生成并保存到项目根目录下的test_tablet_direct.png")
    
    # 测试转换为手机端PNG
    print("\n生成手机端PNG...")
    phone_png = data_to_png_direct_converter.convert_data_to_png(test_params, device_type='phone')
    data_to_png_direct_converter.save_png_to_file(phone_png, "test_phone_direct.png")
    print("手机端PNG已生成并保存到项目根目录下的test_phone_direct.png")
    
    print("\n所有测试完成！")