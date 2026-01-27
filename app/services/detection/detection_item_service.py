# 检测项目服务类
# 包含检测项目相关的业务逻辑，如获取项目信息、创建项目、更新项目等

from app.models.detection import DetectionItem, DetectionObject
from app.extensions import get_db_and_redis, get_db_redis_direct
from app.dal.detection_dal import DetectionItemDAL, DetectionObjectDAL
from app.services.detection.status_manager import StatusManager


class DetectionItemService:
    """检测项目服务类，处理检测项目相关的业务逻辑"""
    
    @staticmethod
    def get_by_id(item_id):
        """
        根据ID获取检测项目信息
        :param item_id: 项目ID
        :return: 成功返回 (项目对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            item_dal = DetectionItemDAL(db, redis)
            item = item_dal.get_by_id(item_id)
            if item:
                # 获取检测对象信息
                detection_object = item.detection_object
                # 使用字典返回，只包含object_id和object_name，避免关系字段循环引用
                item_dict = {
                    'item_id': item.item_id,
                    'object_id': item.object_id,
                    'object_name': detection_object.object_name,
                    'item_name': item.item_name,
                    'description': item.description,
                    'sort_order': item.sort_order,
                    'status': item.status,
                    'create_time': item.create_time.isoformat() if item.create_time else None,
                    'update_time': item.update_time.isoformat() if item.update_time else None
                }
                return (item_dict, None)
            else:
                return (None, f"项目ID {item_id} 不存在")
        except Exception as e:
            return (None, f"获取检测项目失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_all():
        """
        获取所有检测项目列表
        :return: 成功返回 (项目列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            item_dal = DetectionItemDAL(db, redis)
            items = item_dal.get_all()
            # 使用字典列表返回，只包含object_id和object_name，避免关系字段循环引用
            items_list = [{
                'item_id': item.item_id,
                'object_id': item.object_id,
                'object_name': item.detection_object.object_name,
                'item_name': item.item_name,
                'description': item.description,
                'sort_order': item.sort_order,
                'status': item.status,
                'create_time': item.create_time.isoformat() if item.create_time else None,
                'update_time': item.update_time.isoformat() if item.update_time else None
            } for item in items]
            
            # 按sort_order升序排序，sort_order相同时按item_id升序排序
            items_list.sort(key=lambda x: (x.get('sort_order', 0), x.get('item_id', 0)))
            
            return (items_list, None)
        except Exception as e:
            return (None, f"获取检测项目列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_object_id(object_id):
        """
        根据检测对象ID获取检测项目列表
        :param object_id: 检测对象ID
        :return: 成功返回 (项目列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            item_dal = DetectionItemDAL(db, redis)
            items = item_dal.get_by_condition({"object_id": object_id})
            # 使用字典列表返回，只包含object_id和object_name，避免关系字段循环引用
            items_list = [{
                'item_id': item.item_id,
                'object_id': item.object_id,
                'object_name': item.detection_object.object_name,
                'item_name': item.item_name,
                'description': item.description,
                'sort_order': item.sort_order,
                'status': item.status,
                'create_time': item.create_time.isoformat() if item.create_time else None,
                'update_time': item.update_time.isoformat() if item.update_time else None
            } for item in items]
            
            # 按sort_order升序排序，sort_order相同时按item_id升序排序
            items_list.sort(key=lambda x: (x.get('sort_order', 0), x.get('item_id', 0)))
            
            return (items_list, None)
        except Exception as e:
            return (None, f"获取检测项目列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_status(status):
        """
        根据状态获取检测项目列表
        :param status: 状态：1=启用，0=禁用
        :return: 成功返回 (项目列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            item_dal = DetectionItemDAL(db, redis)
            items = item_dal.get_by_condition({"status": status})
            # 使用字典列表返回，只包含object_id和object_name，避免关系字段循环引用
            items_list = [{
                'item_id': item.item_id,
                'object_id': item.object_id,
                'object_name': item.detection_object.object_name,
                'item_name': item.item_name,
                'description': item.description,
                'sort_order': item.sort_order,
                'status': item.status,
                'create_time': item.create_time.isoformat() if item.create_time else None,
                'update_time': item.update_time.isoformat() if item.update_time else None
            } for item in items]
            
            # 按sort_order升序排序，sort_order相同时按item_id升序排序
            items_list.sort(key=lambda x: (x.get('sort_order', 0), x.get('item_id', 0)))
            
            return (items_list, None)
        except Exception as e:
            return (None, f"获取检测项目列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def create(item_data):
        """
        创建新检测项目
        :param item_data: 项目数据字典
        :return: 成功返回 (项目对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 验证必填字段
            if 'object_id' not in item_data or not item_data['object_id']:
                return (None, "检测对象ID不能为空")
            if 'item_name' not in item_data or not item_data['item_name']:
                return (None, "项目名称不能为空")
            
            # 获取数据库和Redis连接
            db, redis, close_db_func = get_db_redis_direct()
            
            # 检查检测对象是否存在且状态为启用
            object_dal = DetectionObjectDAL(db, redis)
            detection_object = object_dal.get_by_id(item_data['object_id'])
            if not detection_object:
                return (None, f"检测对象ID {item_data['object_id']} 不存在")
            if detection_object.status != 1:
                return (None, f"检测对象ID {item_data['object_id']} 已禁用，无法关联")
            
            # 创建项目
            item_dal = DetectionItemDAL(db, redis)
            item = item_dal.create(item_data)
            
            # 使用字典返回，只包含object_id和object_name，避免关系字段循环引用
            item_dict = {
                'item_id': item.item_id,
                'object_id': item.object_id,
                'object_name': detection_object.object_name,
                'item_name': item.item_name,
                'description': item.description,
                'sort_order': item.sort_order,
                'status': item.status,
                'create_time': item.create_time.isoformat() if item.create_time else None,
                'update_time': item.update_time.isoformat() if item.update_time else None
            }
            return (item_dict, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            # 处理唯一约束冲突
            if 'Duplicate entry' in str(e) and '_item_name_object_uc' in str(e):
                return (None, "同一检测对象下项目名称不能重复")
            return (None, f"创建检测项目失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def update(item_id, item_data):
        """
        更新检测项目信息
        :param item_id: 项目ID
        :param item_data: 要更新的项目数据
        :return: 成功返回 (项目对象, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库和Redis连接
            db, redis, close_db_func = get_db_redis_direct()
            
            # 检查项目是否存在
            item_dal = DetectionItemDAL(db, redis)
            item = item_dal.get_by_id(item_id)
            
            if not item:
                return (None, f"项目ID {item_id} 不存在")
            
            # 只在更新object_id时检查检测对象状态
            new_object = None
            if 'object_id' in item_data:
                # 检查新检测对象是否存在且状态为启用
                object_dal = DetectionObjectDAL(db, redis)
                detection_object = object_dal.get_by_id(item_data['object_id'])
                if not detection_object:
                    return (None, f"检测对象ID {item_data['object_id']} 不存在")
                if detection_object.status != 1:
                    return (None, f"检测对象ID {item_data['object_id']} 已禁用，无法关联")
                new_object = detection_object
            
            # 保存旧状态，用于检查状态变更
            old_status = item.status
            new_status = item_data.get('status', old_status)
            
            # 先更新项目
            updated_item = item_dal.update(item_id, item_data)
            
            # 检查状态是否变更
            if 'status' in item_data and new_status != old_status:
                # 状态从启用变为禁用，递归禁用所有关联的检测参数
                if new_status == 0 and old_status == 1:
                    # 使用状态管理器递归禁用所有相关实体
                    StatusManager.recursively_disable_detection_item(item_id, db, redis)
                # 状态从禁用变为启用，递归启用其所属检测对象和分类
                elif new_status == 1 and old_status == 0:
                    # 使用状态管理器递归启用所有相关实体
                    StatusManager.recursively_enable_detection_item(item_id, db, redis)
            
            # 获取最终的检测对象信息
            final_object = new_object if new_object else updated_item.detection_object
            
            # 使用字典返回，只包含object_id和object_name，避免关系字段循环引用
            item_dict = {
                'item_id': updated_item.item_id,
                'object_id': updated_item.object_id,
                'object_name': final_object.object_name,
                'item_name': updated_item.item_name,
                'description': updated_item.description,
                'sort_order': updated_item.sort_order,
                'status': updated_item.status,
                'create_time': updated_item.create_time.isoformat() if updated_item.create_time else None,
                'update_time': updated_item.update_time.isoformat() if updated_item.update_time else None
            }
            return (item_dict, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            # 处理唯一约束冲突
            if 'Duplicate entry' in str(e) and '_item_name_object_uc' in str(e):
                return (None, "同一检测对象下项目名称不能重复")
            return (None, f"更新检测项目失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def delete(item_id):
        """
        删除检测项目
        :param item_id: 项目ID
        :return: 成功返回 (True, None)，失败返回 (False, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库和Redis连接
            db, redis, close_db_func = get_db_redis_direct()
            
            # 检查项目是否存在
            item_dal = DetectionItemDAL(db, redis)
            item = item_dal.get_by_id(item_id)
            
            if not item:
                return (False, f"项目ID {item_id} 不存在")
            
            # 检查是否有检测参数关联
            if item.detection_params and len(item.detection_params) > 0:
                return (False, f"项目ID {item_id} 关联了 {len(item.detection_params)} 个检测参数，无法删除")
            
            # 删除项目
            success = item_dal.delete(item_id)
            return (success, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return (False, f"删除检测项目失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
