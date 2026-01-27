# 检测对象服务类
# 包含检测对象相关的业务逻辑，如获取对象信息、创建对象、更新对象等

from typing import Optional
from app.models.detection import DetectionObject, Category
from app.extensions import get_db_and_redis, get_db_redis_direct
from app.dal.detection_dal import DetectionObjectDAL, CategoryDAL
from app.services.detection.status_manager import StatusManager


class DetectionObjectService:
    """检测对象服务类，处理检测对象相关的业务逻辑"""
    
    @staticmethod
    def get_by_id(object_id):
        """
        根据ID获取检测对象信息
        :param object_id: 检测对象ID
        :return: 成功返回 (检测对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            object_dal = DetectionObjectDAL(db, redis)
            detection_object = object_dal.get_by_id(object_id)
            if detection_object:
                # 获取分类信息
                category = detection_object.category
                # 使用字典返回，包含分类详细信息和直接的分类名称字段
                object_dict = {
                    'object_id': detection_object.object_id,
                    'object_code': detection_object.object_code,
                    'object_name': detection_object.object_name,
                    'category_id': detection_object.category_id,
                    'category_name': category.category_name,  # 直接返回分类名称
                    'description': detection_object.description,
                    'sort_order': detection_object.sort_order,
                    'status': detection_object.status,
                    'create_time': detection_object.create_time.isoformat() if detection_object.create_time else None,
                    'update_time': detection_object.update_time.isoformat() if detection_object.update_time else None
                }
                return (object_dict, None)
            else:
                return (None, f"检测对象ID {object_id} 不存在")
        except Exception as e:
            return (None, f"获取检测对象失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_all():
        """
        获取所有检测对象列表
        :return: 成功返回 (检测对象列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            object_dal = DetectionObjectDAL(db, redis)
            detection_objects = object_dal.get_all()
            # 使用字典列表返回，包含分类详细信息和直接的分类名称字段
            objects_list = [{
                'object_id': obj.object_id,
                'object_code': obj.object_code,
                'object_name': obj.object_name,
                'category_id': obj.category_id,
                'category_name': obj.category.category_name,  # 直接返回分类名称
                'description': obj.description,
                'sort_order': obj.sort_order,
                'status': obj.status,
                'create_time': obj.create_time.isoformat() if obj.create_time else None,
                'update_time': obj.update_time.isoformat() if obj.update_time else None
            } for obj in detection_objects]
            
            # 按sort_order升序排序，sort_order相同时按object_id升序排序
            objects_list.sort(key=lambda x: (x.get('sort_order', 0), x.get('object_id', 0)))
            return (objects_list, None)
        except Exception as e:
            return (None, f"获取检测对象列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_category_id(category_id):
        """
        根据分类ID获取检测对象列表
        :param category_id: 分类ID
        :return: 成功返回 (检测对象列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            object_dal = DetectionObjectDAL(db, redis)
            detection_objects = object_dal.get_by_category_id(category_id)
            # 使用字典列表返回，包含分类详细信息和直接的分类名称字段
            objects_list = [{
                'object_id': obj.object_id,
                'object_code': obj.object_code,
                'object_name': obj.object_name,
                'category_id': obj.category_id,
                'category_name': obj.category.category_name,  # 直接返回分类名称
                'description': obj.description,
                'sort_order': obj.sort_order,
                'status': obj.status,
                'create_time': obj.create_time.isoformat() if obj.create_time else None,
                'update_time': obj.update_time.isoformat() if obj.update_time else None
            } for obj in detection_objects]
            # 按sort_order升序排序，sort_order相同时按object_id升序排序
            objects_list.sort(key=lambda x: (x.get('sort_order', 0), x.get('object_id', 0)))
            return (objects_list, None)
        except Exception as e:
            return (None, f"获取检测对象列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_status(status):
        """
        根据状态获取检测对象列表
        :param status: 状态：1=启用，0=禁用
        :return: 成功返回 (检测对象列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            object_dal = DetectionObjectDAL(db, redis)
            detection_objects = object_dal.get_by_condition({"status": status})
            # 使用字典列表返回，包含分类详细信息和直接的分类名称字段
            objects_list = [{
                'object_id': obj.object_id,
                'object_code': obj.object_code,
                'object_name': obj.object_name,
                'category_id': obj.category_id,
                'category_name': obj.category.category_name,  # 直接返回分类名称
                'description': obj.description,
                'sort_order': obj.sort_order,
                'status': obj.status,
                'create_time': obj.create_time.isoformat() if obj.create_time else None,
                'update_time': obj.update_time.isoformat() if obj.update_time else None
            } for obj in detection_objects]
            # 按sort_order升序排序，sort_order相同时按object_id升序排序
            objects_list.sort(key=lambda x: (x.get('sort_order', 0), x.get('object_id', 0)))
            return (objects_list, None)
        except Exception as e:
            return (None, f"获取检测对象列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def search(keyword, status: Optional[int] = None):
        """
        根据关键词搜索检测对象，支持名称和编码搜索，并可按状态过滤
        :param keyword: 搜索关键词
        :param status: 状态过滤：1=启用，0=禁用，None=不过滤
        :return: 成功返回 (检测对象列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            object_dal = DetectionObjectDAL(db, redis)
            
            # 使用DAL层的search方法，支持关键词搜索和状态过滤
            detection_objects = object_dal.search(keyword, status)
            
            # 使用字典列表返回，包含分类详细信息和直接的分类名称字段
            objects_list = [{
                'object_id': obj.object_id,
                'object_code': obj.object_code,
                'object_name': obj.object_name,
                'category_id': obj.category_id,
                'category_name': obj.category.category_name,  # 直接返回分类名称
                'description': obj.description,
                'sort_order': obj.sort_order,
                'status': obj.status,
                'create_time': obj.create_time.isoformat() if obj.create_time else None,
                'update_time': obj.update_time.isoformat() if obj.update_time else None
            } for obj in detection_objects]
            # 按sort_order升序排序，sort_order相同时按object_id升序排序
            objects_list.sort(key=lambda x: (x.get('sort_order', 0), x.get('object_id', 0)))
            return (objects_list, None)
        except Exception as e:
            return (None, f"搜索检测对象失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def create(object_data):
        """
        创建新检测对象
        :param object_data: 检测对象数据字典
        :return: 成功返回 (检测对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 验证必填字段
            if 'category_id' not in object_data or not object_data['category_id']:
                return (None, "分类ID不能为空")
            if 'object_name' not in object_data or not object_data['object_name']:
                return (None, "检测对象名称不能为空")
            
            # 获取数据库和Redis连接
            db, redis, close_db_func = get_db_redis_direct()
            
            # 检查分类是否存在且状态为启用
            category_dal = CategoryDAL(db, redis)
            category = category_dal.get_by_id(object_data['category_id'])
            if not category:
                return (None, f"分类ID {object_data['category_id']} 不存在")
            if category.status != 1:
                return (None, f"分类ID {object_data['category_id']} 已禁用，无法关联")
            
            # 创建检测对象
            object_dal = DetectionObjectDAL(db, redis)
            detection_object = object_dal.create(object_data)
            
            # 使用字典返回，包含分类详细信息和直接的分类名称字段
            object_dict = {
                'object_id': detection_object.object_id,
                'object_code': detection_object.object_code,
                'object_name': detection_object.object_name,
                'category_id': detection_object.category_id,
                'category_name': category.category_name,  # 直接返回分类名称
                'description': detection_object.description,
                'sort_order': detection_object.sort_order,
                'status': detection_object.status,
                'create_time': detection_object.create_time.isoformat() if detection_object.create_time else None,
                'update_time': detection_object.update_time.isoformat() if detection_object.update_time else None
            }
            return (object_dict, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            # 处理唯一约束冲突
            if 'Duplicate entry' in str(e) and '_category_object_name_uc' in str(e):
                return (None, "同一分类下检测对象名称不能重复")
            return (None, f"创建检测对象失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def update(object_id, object_data):
        """
        更新检测对象信息
        :param object_id: 检测对象ID
        :param object_data: 要更新的检测对象数据
        :return: 成功返回 (检测对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库和Redis连接
            db, redis, close_db_func = get_db_redis_direct()
            
            # 检查检测对象是否存在
            object_dal = DetectionObjectDAL(db, redis)
            detection_object = object_dal.get_by_id(object_id)
            
            if not detection_object:
                return (None, f"检测对象ID {object_id} 不存在")
            
            # 只在更新category_id时检查分类状态
            new_category = None
            if 'category_id' in object_data and object_data['category_id']:
                category_id = object_data['category_id']
                # 检查新分类是否存在且状态为启用
                category_dal = CategoryDAL(db, redis)
                new_category = category_dal.get_by_id(category_id)
                if not new_category:
                    return (None, f"分类ID {category_id} 不存在")
                if new_category.status != 1:
                    return (None, f"分类ID {category_id} 已禁用，无法关联")
            
            # 保存旧状态，用于检查状态变更
            old_status = detection_object.status
            new_status = object_data.get('status', old_status)
            
            # 先更新检测对象
            updated_object = object_dal.update(object_id, object_data)
            
            # 检查状态是否变更
            if 'status' in object_data and new_status != old_status:
                # 状态从启用变为禁用，递归禁用所有关联的检测项目和检测参数
                if new_status == 0 and old_status == 1:
                    # 使用状态管理器递归禁用所有相关实体
                    StatusManager.recursively_disable_detection_object(object_id, db, redis)
                # 状态从禁用变为启用，递归启用其所属分类及其上级分类
                elif new_status == 1 and old_status == 0:
                    # 使用状态管理器递归启用所有相关实体
                    StatusManager.recursively_enable_detection_object(object_id, db, redis)
            
            # 获取最终的分类信息
            final_category = new_category if new_category else updated_object.category
            
            # 使用字典返回，包含分类详细信息和直接的分类名称字段
            object_dict = {
                'object_id': updated_object.object_id,
                'object_code': updated_object.object_code,
                'object_name': updated_object.object_name,
                'category_id': updated_object.category_id,
                'category_name': final_category.category_name,  # 直接返回分类名称
                'description': updated_object.description,
                'sort_order': updated_object.sort_order,
                'status': updated_object.status,
                'create_time': updated_object.create_time.isoformat() if updated_object.create_time else None,
                'update_time': updated_object.update_time.isoformat() if updated_object.update_time else None
            }
            return (object_dict, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            # 处理唯一约束冲突
            if 'Duplicate entry' in str(e) and '_category_object_name_uc' in str(e):
                return (None, "同一分类下检测对象名称不能重复")
            return (None, f"更新检测对象失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def delete(object_id):
        """
        删除检测对象
        :param object_id: 检测对象ID
        :return: 成功返回 (True, None)，失败返回 (False, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库和Redis连接
            db, redis, close_db_func = get_db_redis_direct()
            
            # 检查检测对象是否存在
            object_dal = DetectionObjectDAL(db, redis)
            detection_object = object_dal.get_by_id(object_id)
            
            if not detection_object:
                return (False, f"检测对象ID {object_id} 不存在")
            
            # 检查是否有检测项目关联
            if detection_object.detection_items and len(detection_object.detection_items) > 0:
                return (False, f"检测对象ID {object_id} 关联了 {len(detection_object.detection_items)} 个检测项目，无法删除")
            
            # 删除检测对象
            success = object_dal.delete(object_id)
            return (success, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return (False, f"删除检测对象失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()