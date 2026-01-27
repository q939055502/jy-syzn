# 检测资源管理员服务类
# 包含检测相关资源的批量操作，如批量创建、更新、删除、导入导出等

import csv
import io
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

from app.models.detection import (
    DetectionStandard, DetectionItem,
    DelegationFormTemplate
)
from app.services.detection import (
    DetectionStandardService, DetectionItemService,
    DelegationFormTemplateService
)



class DetectionAdminService:
    """检测资源管理员服务类，处理检测相关资源的批量操作"""
    
    @staticmethod
    def batch_create_standards(standards_data: List[Dict[str, Any]]) -> Tuple[List[DetectionStandard], List[Dict[str, Any]]]:
        """
        批量创建检测规范
        :param standards_data: 检测规范数据列表
        :return: (成功创建的规范列表, 失败的记录及原因)
        """
        success_list = []
        error_list = []
        
        # 使用 DetectionStandardService 创建单个规范
        for index, data in enumerate(standards_data):
            try:
                # 使用现有的服务类方法创建规范
                standard, error = DetectionStandardService.create(data)
                if error:
                    error_list.append({
                        'index': index + 1,
                        'data': data,
                        'error': f'创建失败: {error}'
                    })
                    continue
                
                success_list.append(standard)
            except Exception as e:
                error_list.append({
                    'index': index + 1,
                    'data': data,
                    'error': f'创建失败: {str(e)}'
                })
        
        return success_list, error_list
    
    @staticmethod
    def batch_update_standards(standards_data: List[Dict[str, Any]]) -> Tuple[List[DetectionStandard], List[Dict[str, Any]]]:
        """
        批量更新检测规范
        :param standards_data: 检测规范数据列表，每个字典必须包含standard_id
        :return: (成功更新的规范列表, 失败的记录及原因)
        """
        success_list = []
        error_list = []
        
        try:
            for index, data in enumerate(standards_data):
                try:
                    # 验证标准ID
                    standard_id = data.get('standard_id')
                    if not standard_id:
                        error_list.append({
                            'index': index + 1,
                            'data': data,
                            'error': '标准ID不能为空'
                        })
                        continue
                    
                    # 使用服务类更新规范
                    standard, error = DetectionStandardService.update(standard_id, data)
                    if error:
                        error_list.append({
                            'index': index + 1,
                            'data': data,
                            'error': f'更新失败: {error}'
                        })
                        continue
                    
                    success_list.append(standard)
                except Exception as e:
                    error_list.append({
                        'index': index + 1,
                        'data': data,
                        'error': f'更新失败: {str(e)}'
                    })
            
        except Exception as e:
            raise Exception(f'批量更新检测规范失败: {str(e)}')
        
        return success_list, error_list
    
    @staticmethod
    def batch_delete_standards(standard_ids: List[int]) -> Tuple[int, List[Dict[str, Any]]]:
        """
        批量删除检测规范
        :param standard_ids: 要删除的规范ID列表
        :return: (成功删除的数量, 失败的记录及原因)
        """
        success_count = 0
        error_list = []
        
        try:
            for standard_id in standard_ids:
                try:
                    # 使用服务类删除规范
                    success, error = DetectionStandardService.delete(standard_id)
                    if success:
                        success_count += 1
                    else:
                        error_list.append({
                            'standard_id': standard_id,
                            'error': error
                        })
                except Exception as e:
                    error_list.append({
                        'standard_id': standard_id,
                        'error': f'删除失败: {str(e)}'
                    })
            
        except Exception as e:
            raise Exception(f'批量删除检测规范失败: {str(e)}')
        
        return success_count, error_list
    
    @staticmethod
    def export_standards(standard_ids: Optional[List[int]] = None) -> Tuple[str, bytes]:
        """
        导出检测规范到CSV文件
        :param standard_ids: 要导出的规范ID列表，None表示导出所有
        :return: (文件名, CSV字节数据)
        """
        try:
            # 获取要导出的规范
            if standard_ids:
                standards, error = DetectionStandardService.get_by_ids(standard_ids)
                if error:
                    raise Exception(f'获取检测规范失败: {error}')
            else:
                standards, error = DetectionStandardService.get_all()
                if error:
                    raise Exception(f'获取检测规范失败: {error}')
            
            # 创建CSV文件
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow([
                '规范ID', '规范编号', '规范名称', '规范类型',
                '生效日期', '失效日期', '状态', '替代规范ID',
                '备注', '创建时间', '更新时间'
            ])
            
            # 写入数据
            for standard in standards:
                writer.writerow([
                    standard.standard_id,
                    standard.standard_code,
                    standard.standard_name,
                    standard.standard_type or '',
                    standard.effective_time.isoformat() if standard.effective_time else '',
                    standard.invalid_time.isoformat() if standard.invalid_time else '',
                    standard.status,
                    standard.replace_id or '',
                    standard.remark or '',
                    standard.create_time.isoformat() if standard.create_time else '',
                    standard.update_time.isoformat() if standard.update_time else ''
                ])
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'detection_standards_{timestamp}.csv'
            
            return filename, output.getvalue().encode('utf-8')
        
        except Exception as e:
            raise Exception(f'导出检测规范失败: {str(e)}')
    
    @staticmethod
    def import_standards(csv_data: bytes) -> Tuple[int, List[Dict[str, Any]]]:
        """
        从CSV数据导入检测规范
        :param csv_data: CSV字节数据
        :return: (成功导入的数量, 失败的记录及原因)
        """
        success_count = 0
        error_list = []
        
        try:
            # 解析CSV数据
            csv_text = csv_data.decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_text))
            
            # 验证表头
            required_fields = ['规范编号', '规范名称']
            for field in required_fields:
                if field not in reader.fieldnames:
                    raise Exception(f'CSV文件缺少必要字段: {field}')
            
            # 准备导入数据
            import_data = []
            for row in reader:
                # 转换字段名称和数据类型
                standard_data = {
                    'standard_code': row['规范编号'].strip(),
                    'standard_name': row['规范名称'].strip(),
                    'standard_type': row.get('规范类型', '').strip() or None,
                    'status': int(row.get('状态', '1').strip()) if row.get('状态') else 1
                }
                
                # 处理日期字段
                effective_time = row.get('生效日期', '').strip()
                if effective_time:
                    try:
                        standard_data['effective_time'] = datetime.strptime(effective_time, '%Y-%m-%d').date()
                    except ValueError:
                        standard_data['effective_time'] = None
                
                invalid_time = row.get('失效日期', '').strip()
                if invalid_time:
                    try:
                        standard_data['invalid_time'] = datetime.strptime(invalid_time, '%Y-%m-%d').date()
                    except ValueError:
                        standard_data['invalid_time'] = None
                
                # 处理替代规范ID
                replace_id = row.get('替代规范ID', '').strip()
                if replace_id:
                    try:
                        standard_data['replace_id'] = int(replace_id)
                    except ValueError:
                        standard_data['replace_id'] = None
                
                standard_data['remark'] = row.get('备注', '').strip() or None
                import_data.append(standard_data)
            
            # 批量创建
            success_list, error_list = DetectionAdminService.batch_create_standards(import_data)
            success_count = len(success_list)
            
            return success_count, error_list
        
        except Exception as e:
            raise Exception(f'导入检测规范失败: {str(e)}')
    
    @staticmethod
    def batch_create_items(items_data: List[Dict[str, Any]]) -> Tuple[List[DetectionItem], List[Dict[str, Any]]]:
        """
        批量创建检测项目
        :param items_data: 检测项目数据列表
        :return: (成功创建的项目列表, 失败的记录及原因)
        """
        success_list = []
        error_list = []
        
        try:
            for index, data in enumerate(items_data):
                try:
                    # 验证必填字段
                    if not data.get('group_id') or not data.get('item_name'):
                        error_list.append({
                            'index': index + 1,
                            'data': data,
                            'error': '项目组ID和检测项目名称不能为空'
                        })
                        continue
                    
                    # 使用服务类创建项目
                    item, error = DetectionItemService.create(data)
                    if error:
                        error_list.append({
                            'index': index + 1,
                            'data': data,
                            'error': f'创建失败: {error}'
                        })
                        continue
                    
                    success_list.append(item)
                except Exception as e:
                    error_list.append({
                        'index': index + 1,
                        'data': data,
                        'error': f'创建失败: {str(e)}'
                    })
            
        except Exception as e:
            raise Exception(f'批量创建检测项目失败: {str(e)}')
        
        return success_list, error_list
    
    @staticmethod
    def batch_delete_items(item_ids: List[int]) -> Tuple[int, List[Dict[str, Any]]]:
        """
        批量删除检测项目
        :param item_ids: 要删除的项目ID列表
        :return: (成功删除的数量, 失败的记录及原因)
        """
        success_count = 0
        error_list = []
        
        try:
            for item_id in item_ids:
                try:
                    # 使用服务类删除项目
                    success, error = DetectionItemService.delete(item_id)
                    if success:
                        success_count += 1
                    else:
                        error_list.append({
                            'item_id': item_id,
                            'error': error
                        })
                except Exception as e:
                    error_list.append({
                        'item_id': item_id,
                        'error': f'删除失败: {str(e)}'
                    })
            
        except Exception as e:
            raise Exception(f'批量删除检测项目失败: {str(e)}')
        
        return success_count, error_list
    

    
    @staticmethod
    def batch_create_templates(templates_data: List[Dict[str, Any]]) -> Tuple[List[DelegationFormTemplate], List[Dict[str, Any]]]:
        """
        批量创建委托单模板
        :param templates_data: 委托单模板数据列表
        :return: (成功创建的模板列表, 失败的记录及原因)
        """
        success_list = []
        error_list = []
        
        try:
            for index, data in enumerate(templates_data):
                try:
                    # 验证必填字段
                    if not data.get('group_id') or not data.get('template_name') or not data.get('template_version') or not data.get('file_path'):
                        error_list.append({
                            'index': index + 1,
                            'data': data,
                            'error': '项目组ID、模板名称、模板版本和文件路径不能为空'
                        })
                        continue
                    
                    # 使用服务类创建模板
                    template, error = DelegationFormTemplateService.create(data)
                    if error:
                        error_list.append({
                            'index': index + 1,
                            'data': data,
                            'error': f'创建失败: {error}'
                        })
                        continue
                    
                    success_list.append(template)
                except Exception as e:
                    error_list.append({
                        'index': index + 1,
                        'data': data,
                        'error': f'创建失败: {str(e)}'
                    })
            
        except Exception as e:
            raise Exception(f'批量创建委托单模板失败: {str(e)}')
        
        return success_list, error_list
    
    @staticmethod
    def batch_delete_templates(template_ids: List[int]) -> Tuple[int, List[Dict[str, Any]]]:
        """
        批量删除委托单模板
        :param template_ids: 要删除的模板ID列表
        :return: (成功删除的数量, 失败的记录及原因)
        """
        success_count = 0
        error_list = []
        
        try:
            for template_id in template_ids:
                success, error = DelegationFormTemplateService.delete(template_id)
                if success:
                    success_count += 1
                else:
                    error_list.append({
                        'template_id': template_id,
                        'error': error
                    })
            
        except Exception as e:
            raise Exception(f'批量删除委托单模板失败: {str(e)}')
        
        return success_count, error_list
