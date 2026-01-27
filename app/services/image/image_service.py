# 图片服务类
# 包含SVG生成、转位图、缓存管理等功能

import os
import random
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from app.extensions import get_db_redis_direct
from app.dal.data_image_dal import DataImageDAL
from app.utils.redis_utils import RedisUtils
from app.utils.svg_generator import svg_generator
from app.utils.data_to_png_direct_converter import data_to_png_direct_converter

# 创建日志记录器
logger = logging.getLogger(__name__)

class ImageService:
    """图片服务类，处理SVG生成、转位图、缓存管理等功能"""
    
    # 缓存过期时间（秒）
    CACHE_EXPIRE = 15 * 24 * 3600  # 15天
    
    # 设备类型对应的宽度和DPI配置
    DEVICE_CONFIG = {
        'pc': {'width': 1200, 'dpi': 300},
        'phone': {'width': 375, 'dpi': 300},
        'tablet': {'width': 768, 'dpi': 300}
    }
    

    
    @staticmethod
    def get_image(data_unique_id: str, device_type: str, image_type: str = "png") -> bytes:
        """
        获取图片数据，优先从Redis缓存获取
        :param data_unique_id: 数据唯一标识
        :param device_type: 设备类型（pc/phone/tablet）
        :param image_type: 图片类型（png或svg）
        :return: 图片二进制数据（PNG或SVG）
        """
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            data_image_dal = DataImageDAL(db, redis)
            
            # 生成缓存键
            cache_key = f"data_img:{data_unique_id}:{device_type}"
            
            # 先从Redis获取
            cached_data = RedisUtils.get_cache(redis, cache_key)
            if cached_data:
                if image_type == "svg":
                    return cached_data['svg_content'].encode('utf-8')
                else:
                    return cached_data['png_data']
            
            # 缓存未命中，从数据库获取
            image = data_image_dal.get_by_data_and_device(data_unique_id, device_type)
            if image:
                # 将数据存入缓存
                RedisUtils.set_cache(redis, cache_key, image.__dict__, expire=ImageService.CACHE_EXPIRE)
                if image_type == "svg":
                    return image.svg_content.encode('utf-8')
                else:
                    return image.png_data
            
            # 图片不存在，返回一个简单的图片
            if image_type == "svg":
                # 返回简单的SVG图片
                width = ImageService.DEVICE_CONFIG.get(device_type, ImageService.DEVICE_CONFIG['pc'])['width']
                svg_content = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='200' viewBox='0 0 {width} 200'>
                    <rect width='100%' height='100%' fill='white' />
                    <text x='50%' y='50%' font-size='20' text-anchor='middle' dominant-baseline='middle' fill='red'>图片不存在</text>
                </svg>"""
                return svg_content.encode('utf-8')
            else:
                # 返回简单的PNG图片
                width = ImageService.DEVICE_CONFIG.get(device_type, ImageService.DEVICE_CONFIG['pc'])['width']
                height = 200
                img = Image.new('RGB', (width, height), color='white')
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                text = "图片不存在"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                draw.text((x, y), text, font=font, fill='red')
                
                output = BytesIO()
                img.save(output, format='PNG')
                return output.getvalue()
        except Exception as e:
            logger.error(f"获取图片失败: {e}")
            # 返回错误图片
            if image_type == "svg":
                # 返回简单的SVG错误图片
                width = ImageService.DEVICE_CONFIG.get(device_type, ImageService.DEVICE_CONFIG['pc'])['width']
                svg_content = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='200' viewBox='0 0 {width} 200'>
                    <rect width='100%' height='100%' fill='white' />
                    <text x='50%' y='50%' font-size='20' text-anchor='middle' dominant-baseline='middle' fill='red'>图片生成错误: {str(e)[:50]}</text>
                </svg>"""
                return svg_content.encode('utf-8')
            else:
                # 返回错误PNG图片
                width = ImageService.DEVICE_CONFIG.get(device_type, ImageService.DEVICE_CONFIG['pc'])['width']
                height = 200
                img = Image.new('RGB', (width, height), color='white')
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                text = f"图片生成错误: {str(e)[:50]}"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                draw.text((x, y), text, font=font, fill='red')
                
                output = BytesIO()
                img.save(output, format='PNG')
                return output.getvalue()
        finally:
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def _clean_detection_params(params: list) -> list:
        """
        清洗检测参数数据，只保留指定字段
        
        :param params: 原始检测参数列表
        :return: 清洗后的检测参数列表，按is_regular_param降序和sort_order升序排序
        """
        cleaned_params = []
        
        # 定义需要保留的字段映射
        field_mapping = {
            'is_regular_param': 'is_regular_param',  # 是否为常规参数
            'param_name': 'param_name',  # 参数名称
            'price': 'price',  # 价格
            'sampling_batch': 'sampling_batch',  # 组批规则
            'sampling_frequency': 'sampling_frequency',  # 取样频率
            'sampling_require': 'sampling_require',  # 取样要求
            'inspection_require': 'inspection_require',  # 送检要求
            'required_info': 'required_info',  # 所需信息
            'report_time': 'report_time',  # 报告时间
            'standards': 'standards',  # 规范信息
            'template': 'template',  # 模板信息
            'sort_order': 'sort_order'  # 排序序号
        }
        
        for param in params:
            cleaned_param = {}
            
            # 保留指定字段
            for source_field, target_field in field_mapping.items():
                if source_field in param:
                    # 特殊处理standards字段，转换为带换行符的文本格式
                    if source_field == 'standards':
                        standards = param['standards']
                        # 处理两种情况：如果是列表，需要转换为文本；如果已经是文本，直接使用
                        if isinstance(standards, list):
                            # 将standards转换为文本格式：每个标准的名称和代码之间用换行符分隔，不同标准之间也用换行符分隔
                            standards_text = []
                            for standard in standards:
                                standard_name = standard.get('standard_name', '')
                                standard_code = standard.get('standard_code', '')
                                # 格式：标准名称\n标准代码
                                if standard_name and standard_code:
                                    standards_text.append(f"{standard_name}\n{standard_code}")
                                elif standard_name:
                                    standards_text.append(standard_name)
                                elif standard_code:
                                    standards_text.append(standard_code)
                            # 合并所有标准，用换行符分隔，生成最终的standards文本
                            cleaned_param[target_field] = '\n'.join(standards_text)
                        else:
                            # 已经是字符串格式，直接使用
                            cleaned_param[target_field] = str(standards)
                    # 特殊处理template字段，只保留template_code
                    elif source_field == 'template':
                        template = param['template']
                        cleaned_param['template_code'] = template.get('template_code', '')
                    else:
                        cleaned_param[target_field] = param[source_field]
            
            # 确保standards始终为字符串类型，即使没有任何标准
            if 'standards' not in cleaned_param:
                cleaned_param['standards'] = ''
            
            cleaned_params.append(cleaned_param)
        
        # 排序：先按is_regular_param降序（常规参数在前），再按sort_order升序（按排序号排列）
        cleaned_params.sort(key=lambda x: (-x.get('is_regular_param', 0), x.get('sort_order', 0)))
        
        print(cleaned_params)
        return cleaned_params
    
    @staticmethod
    def generate_detection_image(item_id: int, item_name: str) -> dict:
        """
        生成检测参数图片并保存到数据库
        :param item_id: 检测项目ID
        :param item_name: 检测项目名称
        :return: 包含生成结果的数据字典
        """
        from app.services.detection.detection_param_service import DetectionParamService
        
        # 获取启用的检测参数
        params, error_msg = DetectionParamService.get_enabled_by_item_id(item_id)
        if error_msg:
            raise Exception(f"获取检测参数失败: {error_msg}")
        
        if not params:
            raise Exception(f"检测项目 {item_id} 下没有启用的检测参数")
        
        # 生成数据唯一标识
        data_unique_id = f"detection:{item_id}"
        
        # 数据清洗：只保留指定字段
        cleaned_params = ImageService._clean_detection_params(params)
        
        # 使用svg_generator处理数据并生成SVG
        # 1. 转换检测数据
        transformed_data = svg_generator.transform_detection_data(cleaned_params)
        # 2. 清洗重复相邻单元格
        cleaned_data = svg_generator.clean_duplicate_adjacent_cells(transformed_data)
        # 3. 生成原始SVG
        svg_content = svg_generator.generate_svg(cleaned_data)
        # 4. 添加文本水印
        svg_content_with_watermark = svg_generator.add_text_watermark_to_svg(svg_content)
        # 5. 添加防爬水印和噪点
        svg_content = svg_generator.add_anti_crawl_watermark(svg_content_with_watermark)
        
        # 保存图片到数据库
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            data_image_dal = DataImageDAL(db, redis)
            
            # 为所有设备类型生成并保存图片
            for device_type in ImageService.DEVICE_CONFIG.keys():
                # 使用数据直接生成PNG，不经过SVG转换
                # 注意：使用cleaned_params而不是cleaned_data，避免数据被转换两次
                png_data = data_to_png_direct_converter.convert_data_to_png(cleaned_params, device_type)
                
                # 保存到数据库
                image_data = {
                    'data_unique_id': data_unique_id,
                    'device_type': device_type,
                    'svg_content': svg_content,
                    'png_data': png_data
                }
                
                # 先尝试更新，不存在则创建
                existing_image = data_image_dal.get_by_data_and_device(data_unique_id, device_type)
                if existing_image:
                    # 更新现有记录，版本号+1
                    image_data['version'] = existing_image.version + 1
                    data_image_dal.update(existing_image.image_id, image_data)
                else:
                    # 创建新记录
                    data_image_dal.create(image_data)
        except Exception as e:
            logger.error(f"保存图片到数据库失败: {e}")
            raise Exception(f"保存图片到数据库失败: {e}")
        finally:
            if close_db_func:
                close_db_func()
        
        return {
            "data_unique_id": data_unique_id,
            "item_id": item_id,
            "item_name": item_name
        }
    

