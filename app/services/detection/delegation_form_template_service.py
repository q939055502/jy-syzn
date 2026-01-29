# 委托单模板服务类
# 包含委托单模板相关的业务逻辑，如获取模板信息、创建模板、更新模板等

import shutil
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from app.models.detection import DelegationFormTemplate, DetectionItem
from app.extensions import get_db_and_redis, get_db_redis_direct
from app.dal.detection_dal import DelegationFormTemplateDAL, DetectionItemDAL
from app.services.detection.utils.file_utils import (
    ensure_dir, generate_file_path, get_absolute_file_path, delete_file, move_file,
    is_allowed_file, get_file_extension
)
from app.services.utils.link_generator import LinkGeneratorService


class DelegationFormTemplateService:
    """委托单模板服务类，处理委托单模板相关的业务逻辑"""
    
    @staticmethod
    def _generate_download_url(template):
        """
        生成委托单模板的下载链接
        :param template: 委托单模板对象
        :return: 下载链接
        """
        # 生成文件路径
        file_extension = template.file_type[1:] if template.file_type.startswith('.') else template.file_type
        file_path = generate_file_path(
            "delegation_form_templates",
            template.template_name,
            template.template_code,
            file_extension
        )
        
        # 使用新的链接生成服务生成带签名的下载链接
        return LinkGeneratorService.generate_signed_url(file_path.as_posix())
    
    @staticmethod
    def get_by_id(template_id):
        """
        根据ID获取委托单模板信息
        :param template_id: 模板ID
        :return: 成功返回 (模板对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            template_dal = DelegationFormTemplateDAL(db, redis)
            template = template_dal.get_by_id(template_id)
            if template:
                # 模板已包含template_code字段，无需额外添加
                # 为模板添加下载链接属性
                template.download_url = DelegationFormTemplateService._generate_download_url(template)
                return (template, None)
            else:
                return (None, f"委托单模板ID {template_id} 不存在")
        except Exception as e:
            return (None, f"获取委托单模板失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_all():
        """
        获取所有委托单模板列表
        :return: 成功返回 (模板列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            template_dal = DelegationFormTemplateDAL(db, redis)
            templates = template_dal.get_all()
            
            # 为每个模板添加下载链接
            for template in templates:
                template.download_url = DelegationFormTemplateService._generate_download_url(template)
            
            return (templates, None)
        except Exception as e:
            return (None, f"获取委托单模板列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    

    
    @staticmethod
    def get_by_status(status):
        """
        根据状态获取委托单模板列表
        :param status: 状态：1=启用，0=禁用
        :return: 成功返回 (模板列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            template_dal = DelegationFormTemplateDAL(db, redis)
            templates = template_dal.get_by_status(status)
            
            # 为每个模板添加下载链接
            for template in templates:
                template.download_url = DelegationFormTemplateService._generate_download_url(template)
            
            return (templates, None)
        except Exception as e:
            return (None, f"获取委托单模板列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    

    
    @staticmethod
    def create(template_data, file):
        """
        创建新委托单模板
        :param template_data: 模板数据字典
        :param file: 上传的文件对象
        :return: 成功返回 (模板对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        temp_file_path = None
        try:
            # 验证必填字段
            if 'template_name' not in template_data or not template_data['template_name']:
                return (None, "模板名称不能为空")
            if 'template_code' not in template_data or not template_data['template_code']:
                return (None, "模板编号不能为空")
            if 'file_type' not in template_data or not template_data['file_type']:
                return (None, "文件类型不能为空")
            
            # 验证文件格式
            if not is_allowed_file(file.filename):
                return (None, "不支持的文件格式，仅允许.doc、.docx、.xls、.xlsx格式")
            
            # 保存上传的文件到临时位置
            with NamedTemporaryFile(delete=False, suffix=f".{template_data['file_type']}") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_file_path = temp_file.name
            
            # 创建模板
            db, redis, close_db_func = get_db_redis_direct()
            template_dal = DelegationFormTemplateDAL(db, redis)
            template = template_dal.create(template_data)
            
            # 确保upload_user字段被正确设置
            if 'upload_user' in template_data:
                template.upload_user = template_data['upload_user']
                db.commit()
                db.refresh(template)
            
            # 移除file_type中的点，因为generate_file_path会添加
            file_extension = template.file_type[1:] if template.file_type.startswith('.') else template.file_type
            
            # 生成文件路径并保存文件
            file_path = generate_file_path(
                "delegation_form_templates",
                template.template_name,
                template.template_code,
                file_extension
            )
            
            # 获取绝对路径
            absolute_file_path = get_absolute_file_path(file_path)
            
            # 确保目录存在
            ensure_dir(absolute_file_path.parent)
            
            # 保存文件到最终位置
            shutil.copy2(temp_file_path, absolute_file_path)
            
            return (template, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return (None, f"创建委托单模板失败: {str(e)}")
        finally:
            # 清理临时文件
            if temp_file_path and Path(temp_file_path).exists():
                Path(temp_file_path).unlink()
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def update(template_id, template_data, file=None):
        """
        更新委托单模板信息
        :param template_id: 模板ID
        :param template_data: 要更新的模板数据
        :param file: 上传的文件对象（可选）
        :return: 成功返回 (模板对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        temp_file_path = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            template_dal = DelegationFormTemplateDAL(db, redis)
            
            # 检查模板是否存在
            template = template_dal.get_by_id(template_id)
            if not template:
                return (None, f"委托单模板ID {template_id} 不存在")
            
            # 保存模板的旧信息，用于后续文件处理
            old_template_name = template.template_name
            old_file_type = template.file_type
            
            # 保存上传的文件到临时位置（如果有）
            if file:
                # 验证文件格式
                if not is_allowed_file(file.filename):
                    return (None, "不支持的文件格式，仅允许.doc、.docx、.xls、.xlsx格式")
                
                # 确保file_type在template_data中
                if 'file_type' not in template_data:
                    # 从上传文件中获取扩展名
                    file_extension = get_file_extension(file.filename)
                    template_data['file_type'] = file_extension
                
                with NamedTemporaryFile(delete=False, suffix=f".{template_data['file_type']}") as temp_file:
                    shutil.copyfileobj(file.file, temp_file)
                    temp_file_path = temp_file.name
            
            # 更新模板
            updated_template = template_dal.update(template_id, template_data)
            
            # 移除旧file_type中的点
            old_file_extension = old_file_type[1:] if old_file_type.startswith('.') else old_file_type
            
            # 生成旧文件路径
            old_file_path = generate_file_path(
                "delegation_form_templates",
                old_template_name,
                template.template_code,  # 使用template_code替代template_version
                old_file_extension
            )
            
            # 获取旧文件的绝对路径
            old_absolute_file_path = get_absolute_file_path(old_file_path)
            
            # 移除旧file_type中的点
            new_file_extension = updated_template.file_type[1:] if updated_template.file_type.startswith('.') else updated_template.file_type
            
            # 生成新文件路径
            new_file_path = generate_file_path(
                "delegation_form_templates",
                updated_template.template_name,
                updated_template.template_code,  # 使用template_code替代template_version
                new_file_extension
            )
            
            # 获取新文件的绝对路径
            new_absolute_file_path = get_absolute_file_path(new_file_path)
            
            # 处理文件
            if file:
                # 如果上传了新文件，先删除旧文件，然后保存新文件
                if old_absolute_file_path.exists():
                    delete_file(old_absolute_file_path)
                
                # 保存新文件到最终位置
                ensure_dir(new_absolute_file_path.parent)
                shutil.copy2(temp_file_path, new_absolute_file_path)
            else:
                # 如果没有上传新文件，但元数据发生了变化，移动旧文件到新位置
                if old_absolute_file_path != new_absolute_file_path:
                    if old_absolute_file_path.exists():
                        move_file(old_absolute_file_path, new_absolute_file_path)
            
            return (updated_template, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return (None, f"更新委托单模板失败: {str(e)}")
        finally:
            # 清理临时文件
            if temp_file_path and Path(temp_file_path).exists():
                Path(temp_file_path).unlink()
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def delete(template_id):
        """
        删除委托单模板
        :param template_id: 模板ID
        :return: 成功返回 (True, None)，失败返回 (False, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            template_dal = DelegationFormTemplateDAL(db, redis)
            
            # 检查模板是否存在
            template = template_dal.get_by_id(template_id)
            if not template:
                return (False, f"委托单模板ID {template_id} 不存在")
            
            # 移除file_type中的点
            file_extension = template.file_type[1:] if template.file_type.startswith('.') else template.file_type
            
            # 生成文件路径并删除文件
            file_path = generate_file_path(
                "delegation_form_templates",
                template.template_name,
                template.template_code,
                file_extension
            )
            absolute_file_path = get_absolute_file_path(file_path)
            delete_file(absolute_file_path)
            
            # 删除模板
            success = template_dal.delete(template_id)
            return (success, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return (False, f"删除委托单模板失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    

    
    @staticmethod
    def search(search_keyword, status=None):
        """
        搜索委托单模板
        :param search_keyword: 搜索关键词，支持按模板名称搜索
        :param status: 状态筛选，1=启用，0=禁用，None=不筛选
        :return: 成功返回 (模板列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            template_dal = DelegationFormTemplateDAL(db, redis)
            
            # 调用DAL层搜索方法，传递status参数
            templates = template_dal.search(search_keyword, status)
            
            # 为每个模板添加下载链接
            for template in templates:
                template.download_url = DelegationFormTemplateService._generate_download_url(template)
            
            return (templates, None)
        except Exception as e:
            return (None, f"搜索委托单模板失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_usage_info(template_id):
        """
        获取委托单模板的使用情况
        :param template_id: 模板ID
        :return: 成功返回 (使用情况列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            
            # 检查模板是否存在
            template_dal = DelegationFormTemplateDAL(db, redis)
            template = template_dal.get_by_id(template_id)
            if not template:
                return (None, f"委托单模板ID {template_id} 不存在")
            
            # 获取所有关联的检测参数
            from app.dal.detection_dal import DetectionParamDAL
            param_dal = DetectionParamDAL(db, redis)
            params = param_dal.get_by_template_id(template_id)
            
            # 构建使用情况列表
            usage_list = []
            for param in params:
                # 获取检测对象、检测项目和检测参数信息
                obj = param.item.detection_object
                item = param.item
                
                # 获取状态文本
                obj_status = "启用" if obj.status == 1 else "禁用"
                item_status = "启用" if item.status == 1 else "禁用"
                param_status = "启用" if param.status == 1 else "禁用"
                
                # 拼接字符串
                usage_str = f"{obj.object_name}（{obj_status}）--{item.item_name}（{item_status}）--{param.param_name}（{param_status}）"
                usage_list.append(usage_str)
            
            return (usage_list, None)
        except Exception as e:
            return (None, f"获取委托单模板使用情况失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
