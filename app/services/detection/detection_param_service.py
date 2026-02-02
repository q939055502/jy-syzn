# 检测参数服务类
# 包含检测参数相关的业务逻辑，如获取参数信息、创建参数、更新参数等

import logging
from typing import Optional, Dict, Any, List
from app.models.detection import DetectionParam, DetectionItem
from app.extensions import get_db_and_redis, get_db_redis_direct
from app.dal.detection_dal import DetectionParamDAL, DetectionItemDAL, DetectionStandardDAL
from app.services.detection.status_manager import StatusManager

# 创建日志记录器
logger = logging.getLogger(__name__)


class DetectionParamService:
    """检测参数服务类，处理检测参数相关的业务逻辑"""
    
    @staticmethod
    def get_by_id(param_id, db=None, redis=None):
        """
        根据ID获取检测参数信息
        :param param_id: 检测参数ID
        :param db: 数据库会话，可选
        :param redis: Redis客户端，可选
        :return: 成功返回 (检测参数对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"根据ID获取检测参数: {param_id}")
            # 如果没有传入会话，创建新会话
            if not db or not redis:
                db, redis, close_db_func = get_db_redis_direct()
            
            param_dal = DetectionParamDAL(db, redis)
            param = param_dal.get_by_id(param_id, with_relations=True)
            if param:
                logger.info(f"成功获取检测参数: {param_id}")
                return (param, None)
            else:
                error_msg = f"检测参数ID {param_id} 不存在"
                logger.warning(error_msg)
                return (None, error_msg)
        except Exception as e:
            error_msg = f"获取检测参数失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_all(page: int = 1, limit: int = 100, db=None, redis=None):
        """
        获取所有检测参数信息，支持分页
        :param page: 当前页码，默认1
        :param limit: 每页数量，默认100
        :param db: 数据库会话，可选
        :param redis: Redis客户端，可选
        :return: 成功返回 (检测参数列表, 总记录数, None)，失败返回 (None, 0, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"获取检测参数列表，页码: {page}，每页数量: {limit}")
            # 如果没有传入会话，创建新会话
            if not db or not redis:
                db, redis, close_db_func = get_db_redis_direct()
            
            param_dal = DetectionParamDAL(db, redis)
            params, total = param_dal.get_paginated(page=page, limit=limit)
            
            # 按sort_order升序排序，sort_order相同时按param_id升序排序，不考虑常规状态
            params.sort(key=lambda x: (x.sort_order if x.sort_order is not None else 0, x.param_id))
            
            logger.info(f"成功获取检测参数列表，共 {total} 条记录")
            return (params, total, None)
        except Exception as e:
            error_msg = f"获取检测参数列表失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, 0, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_item_id(item_id, page: int = 1, limit: int = 100, db=None, redis=None):
        """
        根据项目ID获取检测参数列表，支持分页
        :param item_id: 项目ID
        :param page: 当前页码，默认1
        :param limit: 每页数量，默认100
        :param db: 数据库会话，可选
        :param redis: Redis客户端，可选
        :return: 成功返回 (检测参数列表, 总记录数, None)，失败返回 (None, 0, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"根据项目ID获取检测参数列表: {item_id}，页码: {page}，每页数量: {limit}")
            db, redis, close_db_func = get_db_redis_direct()
            # 检查项目是否存在
            item_dal = DetectionItemDAL(db, redis)
            item = item_dal.get_by_id(item_id)
            if not item:
                error_msg = f"项目ID {item_id} 不存在"
                logger.warning(error_msg)
                return (None, 0, error_msg)
            
            param_dal = DetectionParamDAL(db, redis)
            params, total = param_dal.get_paginated(page=page, limit=limit, condition={"item_id": item_id})
            
            # 按sort_order升序排序，sort_order相同时按param_id升序排序，不考虑常规状态
            params.sort(key=lambda x: (x.sort_order if x.sort_order is not None else 0, x.param_id))
            
            logger.info(f"成功获取项目 {item_id} 的检测参数列表，共 {total} 条记录")
            return (params, total, None)
        except Exception as e:
            error_msg = f"获取检测参数列表失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, 0, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_status(status, page: int = 1, limit: int = 100, db=None, redis=None):
        """
        根据状态获取检测参数列表，支持分页
        :param status: 状态：1=启用，0=禁用
        :param page: 当前页码，默认1
        :param limit: 每页数量，默认100
        :param db: 数据库会话，可选
        :param redis: Redis客户端，可选
        :return: 成功返回 (检测参数列表, 总记录数, None)，失败返回 (None, 0, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"根据状态获取检测参数列表: {status}，页码: {page}，每页数量: {limit}")
            db, redis, close_db_func = get_db_redis_direct()
            
            param_dal = DetectionParamDAL(db, redis)
            params, total = param_dal.get_paginated(page=page, limit=limit, condition={"status": status})
            
            # 按sort_order升序排序，sort_order相同时按param_id升序排序，不考虑常规状态
            params.sort(key=lambda x: (x.sort_order if x.sort_order is not None else 0, x.param_id))
            
            logger.info(f"成功获取状态为 {status} 的检测参数列表，共 {total} 条记录")
            return (params, total, None)
        except Exception as e:
            error_msg = f"获取检测参数列表失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, 0, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def search(search_params: Dict[str, Any], page: int = 1, limit: int = 100, db=None, redis=None):
        """
        搜索检测参数
        :param search_params: 搜索参数字典
        :param page: 当前页码，默认1
        :param limit: 每页数量，默认100
        :param db: 数据库会话，可选
        :param redis: Redis客户端，可选
        :return: 成功返回 (检测参数列表, 总记录数, None)，失败返回 (None, 0, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"搜索检测参数: {search_params}，页码: {page}，每页数量: {limit}")
            if not db or not redis:
                db, redis, close_db_func = get_db_redis_direct()
            
            # 配置搜索参数
            fuzzy_fields = ["param_name", "material_name"]
            related_fields = {
                "item": {
                    "field": "item_name",
                    "search_key": "item_name"
                }
            }
            
            param_dal = DetectionParamDAL(db, redis)
            params, total = param_dal.search(search_params, fuzzy_fields, related_fields, page, limit)
            
            # 按sort_order升序排序，sort_order相同时按param_id升序排序，不考虑常规状态
            params.sort(key=lambda x: (x.sort_order if x.sort_order is not None else 0, x.param_id))
            
            logger.info(f"搜索检测参数成功，共 {total} 条记录")
            return (params, total, None)
        except Exception as e:
            error_msg = f"搜索检测参数失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, 0, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def create(param_data):
        """
        创建新检测参数
        :param param_data: 检测参数数据字典
        :return: 成功返回 (检测参数对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"创建检测参数: {param_data}")
            # 验证必填字段
            if 'item_id' not in param_data or not param_data['item_id']:
                error_msg = "项目ID不能为空"
                logger.warning(error_msg)
                return (None, error_msg)
            if 'param_name' not in param_data or not param_data['param_name']:
                error_msg = "检测参数名称不能为空"
                logger.warning(error_msg)
                return (None, error_msg)
            
            # 提取standard_ids，默认为空列表
            standard_ids = param_data.pop('standard_ids', [])
            
            db, redis, close_db_func = get_db_redis_direct()
            # 检查项目是否存在且状态为启用
            item_dal = DetectionItemDAL(db, redis)
            item = item_dal.get_by_id(param_data['item_id'])
            if not item:
                error_msg = f"项目ID {param_data['item_id']} 不存在"
                logger.warning(error_msg)
                return (None, error_msg)
            if item.status != 1:
                error_msg = f"检测项目ID {param_data['item_id']} 已禁用，无法关联"
                logger.warning(error_msg)
                return (None, error_msg)
            
            # 检查检测项目关联的检测对象是否状态为启用
            if item.detection_object.status != 1:
                error_msg = f"检测项目ID {param_data['item_id']} 关联的检测对象已禁用，无法关联"
                logger.warning(error_msg)
                return (None, error_msg)
            
            # 检查规范是否存在
            standard_dal = DetectionStandardDAL(db, redis)
            if standard_ids:
                standards = standard_dal.get_by_ids(standard_ids)
                if len(standards) != len(standard_ids):
                    # 找出不存在的规范ID
                    existing_ids = [standard.standard_id for standard in standards]
                    missing_ids = [sid for sid in standard_ids if sid not in existing_ids]
                    error_msg = f"检测规范ID {missing_ids} 不存在，无法关联"
                    logger.warning(error_msg)
                    return (None, error_msg)
            
            # 创建检测参数
            param_dal = DetectionParamDAL(db, redis)
            param = param_dal.create(param_data)
            
            # 关联检测规范
            if standard_ids:
                param_dal.update_standards(param.param_id, standard_ids)
            
            # 重新查询参数对象，包含关联的规范信息
            param = param_dal.get_by_id(param.param_id, with_relations=True)
            
            # 重新生成SVG图片，确保新添加的参数能在图片中显示
            # 获取参数所属的项目信息
            item_id = param.item_id
            item_name = param.item.item_name if param.item else f"项目{item_id}"
            
            # 重新生成检测参数图片
            try:
                from app.services.image.image_service import ImageService
                from app.dal.data_image_dal import DataImageDAL
                
                # 重新生成检测参数图片
                ImageService.generate_detection_image(item_id, item_name)
                logger.info(f"成功重新生成检测参数图片: 项目{item_id}")
                
                # 清除Redis缓存，确保下次获取图片时从数据库获取新数据
                db, redis, close_db_func = get_db_redis_direct()
                
                # 清除所有设备类型的缓存
                device_types = ['pc', 'phone', 'tablet']
                data_unique_id = f"detection:{item_id}"
                
                for device_type in device_types:
                    # 直接清除缓存，使用与image_service.py中相同的缓存键格式
                    cache_key = f"data_img:{data_unique_id}:{device_type}"
                    from app.utils.redis_utils import RedisUtils
                    RedisUtils.delete_cache(redis, cache_key)
                    logger.info(f"清除Redis缓存: {cache_key}")
                
                if close_db_func:
                    close_db_func()
            except Exception as e:
                logger.error(f"重新生成检测参数图片失败: {str(e)}")
                # 图片生成失败不影响参数创建，继续执行
            
            logger.info(f"成功创建检测参数: {param.param_id}")
            return (param, None)
        except Exception as e:
            # 处理唯一约束冲突
            if 'Duplicate entry' in str(e):
                if '_item_material_param_uc' in str(e):
                    error_msg = "同一项目和材料下检测参数名称不能重复"
                elif '_item_param_uc' in str(e):
                    error_msg = "同一项目下检测参数名称不能重复"
                else:
                    error_msg = f"创建检测参数失败: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    return (None, error_msg)
                logger.warning(error_msg)
                return (None, error_msg)
            error_msg = f"创建检测参数失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def update(param_id, param_data):
        """
        更新检测参数信息
        :param param_id: 检测参数ID
        :param param_data: 要更新的检测参数数据
        :return: 成功返回 (检测参数对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"更新检测参数: {param_id}，数据: {param_data}")
            
            # 提取standard_ids，支持前端发送的standards字段
            standard_ids = param_data.pop('standard_ids', None)
            logger.info(standard_ids)
            logger.info("11111111111")
            # 如果没有standard_ids，但有standards字段，使用standards
            if standard_ids is None:
                standard_ids = param_data.pop('standards', None)
            
            db, redis, close_db_func = get_db_redis_direct()
            param_dal = DetectionParamDAL(db, redis)
            
            # 获取当前检测参数，用于检查状态变更
            current_param = param_dal.get_by_id(param_id)
            if not current_param:
                error_msg = f"检测参数ID {param_id} 不存在"
                logger.warning(error_msg)
                return (None, error_msg)
            
            # 只在更新item_id时检查项目和检测对象状态
            if 'item_id' in param_data and param_data['item_id']:
                item_dal = DetectionItemDAL(db, redis)
                item = item_dal.get_by_id(param_data['item_id'])
                if not item:
                    error_msg = f"项目ID {param_data['item_id']} 不存在"
                    logger.warning(error_msg)
                    return (None, error_msg)
                if item.status != 1:
                    error_msg = f"检测项目ID {param_data['item_id']} 已禁用，无法关联"
                    logger.warning(error_msg)
                    return (None, error_msg)
                if item.detection_object.status != 1:
                    error_msg = f"检测项目ID {param_data['item_id']} 关联的检测对象已禁用，无法关联"
                    logger.warning(error_msg)
                    return (None, error_msg)
            
            # 检查规范是否存在（如果提供了standard_ids）
            standard_dal = DetectionStandardDAL(db, redis)
            if standard_ids is not None:
                if standard_ids:
                    standards = standard_dal.get_by_ids(standard_ids)
                    if len(standards) != len(standard_ids):
                        # 找出不存在的规范ID
                        existing_ids = [standard.standard_id for standard in standards]
                        missing_ids = [sid for sid in standard_ids if sid not in existing_ids]
                        error_msg = f"检测规范ID {missing_ids} 不存在，无法关联"
                        logger.warning(error_msg)
                        return (None, error_msg)
            
            # 保存旧状态，用于检查状态变更
            old_status = current_param.status
            new_status = param_data.get('status', old_status)
            
            # 先更新检测参数
            param = param_dal.update(param_id, param_data)
            
            # 检查状态是否变更
            if 'status' in param_data and new_status != old_status:
                # 状态从禁用变为启用，递归启用其所属检测项目、检测对象和分类
                if new_status == 1 and old_status == 0:
                    # 使用状态管理器递归启用所有相关实体
                    StatusManager.recursively_enable_detection_param(param_id, db, redis)
            if not param:
                error_msg = f"检测参数ID {param_id} 不存在"
                logger.warning(error_msg)
                return (None, error_msg)
            
            # 更新关联的检测规范（如果提供了standard_ids）
            if standard_ids is not None:
                param_dal.update_standards(param_id, standard_ids)
            
            # 重新查询参数对象，包含关联的规范信息
            param = param_dal.get_by_id(param_id, with_relations=True)
            
            # 只要更新了检测参数，就重新生成SVG图片
            # 获取参数所属的项目信息
            item_id = param.item_id
            item_name = param.item.item_name if param.item else f"项目{item_id}"
            
            # 重新生成检测参数图片
            try:
                from app.services.image.image_service import ImageService
                from app.dal.data_image_dal import DataImageDAL
                
                # 重新生成检测参数图片
                ImageService.generate_detection_image(item_id, item_name)
                logger.info(f"成功重新生成检测参数图片: 项目{item_id}")
                
                # 清除Redis缓存，确保下次获取图片时从数据库获取新数据
                db, redis, close_db_func = get_db_redis_direct()
                
                # 清除所有设备类型的缓存
                device_types = ['pc', 'phone', 'tablet']
                data_unique_id = f"detection:{item_id}"
                
                for device_type in device_types:
                    # 直接清除缓存，使用与image_service.py中相同的缓存键格式
                    cache_key = f"data_img:{data_unique_id}:{device_type}"
                    from app.utils.redis_utils import RedisUtils
                    RedisUtils.delete_cache(redis, cache_key)
                    logger.info(f"清除Redis缓存: {cache_key}")
                
                if close_db_func:
                    close_db_func()
            except Exception as e:
                logger.error(f"重新生成检测参数图片失败: {str(e)}")
                # 图片生成失败不影响参数更新，继续执行
            
            logger.info(f"成功更新检测参数: {param_id}")
            return (param, None)
        except Exception as e:
            # 处理唯一约束冲突
            if 'Duplicate entry' in str(e):
                if '_item_material_param_uc' in str(e):
                    error_msg = "同一项目和材料下检测参数名称不能重复"
                elif '_item_param_uc' in str(e):
                    error_msg = "同一项目下检测参数名称不能重复"
                else:
                    error_msg = f"更新检测参数失败: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    return (None, error_msg)
                logger.warning(error_msg)
                return (None, error_msg)
            error_msg = f"更新检测参数失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def delete(param_id):
        """
        删除检测参数
        :param param_id: 检测参数ID
        :return: 成功返回 (True, None)，失败返回 (False, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"删除检测参数: {param_id}")
            db, redis, close_db_func = get_db_redis_direct()
            
            # 检查检测参数是否存在
            param_dal = DetectionParamDAL(db, redis)
            param = param_dal.get_by_id(param_id)
            if not param:
                error_msg = f"检测参数ID {param_id} 不存在"
                logger.warning(error_msg)
                return (False, error_msg)
            
            # 删除检测参数
            success = param_dal.delete(param_id)
            if success:
                logger.info(f"成功删除检测参数: {param_id}")
            else:
                logger.error(f"删除检测参数失败: {param_id}")
            return (success, None)
        except Exception as e:
            error_msg = f"删除检测参数失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_with_relations(param_id, db=None, redis=None):
        """
        获取检测参数及其关联数据
        :param param_id: 检测参数ID
        :param db: 数据库会话，可选
        :param redis: Redis客户端，可选
        :return: 成功返回 (检测参数对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"获取检测参数及其关联数据: {param_id}")
            # 如果没有传入会话，创建新会话
            if not db or not redis:
                db, redis, close_db_func = get_db_redis_direct()
            
            param_dal = DetectionParamDAL(db, redis)
            param = param_dal.get_by_id(param_id, with_relations=True)
            
            if param:
                logger.info(f"成功获取检测参数及其关联数据: {param_id}")
                return (param, None)
            else:
                error_msg = f"检测参数ID {param_id} 不存在"
                logger.warning(error_msg)
                return (None, error_msg)
        except Exception as e:
            error_msg = f"获取检测参数关联数据失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_enabled_by_item_id(item_id, db=None, redis=None):
        """
        根据项目ID获取所有启用的检测参数，并按排序号排列
        :param item_id: 检测项目ID
        :param db: 数据库会话，可选
        :param redis: Redis客户端，可选
        :return: 成功返回 (检测参数列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            logger.info(f"根据项目ID获取启用的检测参数: {item_id}")
            # 如果没有传入会话，创建新会话
            if not db or not redis:
                db, redis, close_db_func = get_db_redis_direct()
            
            param_dal = DetectionParamDAL(db, redis)
            # 查询状态为1（启用）的检测参数，使用with_relations=True加载关联数据
            params, total = param_dal.get_paginated(page=1, limit=1000, 
                                                 condition={"item_id": item_id, "status": 1})
            
            # 转换为字典列表，包含模板信息和规范信息
            param_dicts = [param.to_dict(include_template=True) for param in params]
            
            # 按排序号排列
            sorted_params = sorted(param_dicts, key=lambda x: x.get('sort_order', 0))
            
            logger.info(f"成功获取项目 {item_id} 的启用检测参数，共 {len(sorted_params)} 条记录")
            return (sorted_params, None)
        except Exception as e:
            error_msg = f"获取启用检测参数失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (None, error_msg)
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    

