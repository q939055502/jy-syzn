# 分类服务类
# 包含分类相关的业务逻辑，如获取分类信息、创建分类、更新分类等

from app.extensions import get_db_and_redis, get_db_redis_direct
from app.dal.detection_dal import CategoryDAL, DetectionObjectDAL
from app.models.detection import DetectionObject
from app.services.detection.status_manager import StatusManager


class CategoryService:
    """分类服务类，处理分类相关的业务逻辑"""
    
    @staticmethod
    def get_by_id(category_id):
        """
        根据ID获取分类信息
        :param category_id: 分类ID
        :return: 成功返回 (分类字典, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            category_dal = CategoryDAL(db, redis)
            category = category_dal.get_by_id(category_id)
            if category:
                # 转换为字典，确保时间字段格式正确
                category_dict = {
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'parent_id': category.parent_id,
                    'sort_order': category.sort_order,
                    'status': category.status,
                    'create_time': category.create_time.isoformat() if category.create_time else None,
                    'update_time': category.update_time.isoformat() if category.update_time else None
                }
                return (category_dict, None)
            else:
                return (None, f"分类ID {category_id} 不存在")
        except Exception as e:
            return (None, f"获取分类失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_all():
        """
        获取所有分类列表
        :return: 成功返回 (分类字典列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            category_dal = CategoryDAL(db, redis)
            categories = category_dal.get_all()
            
            # 转换为字典列表，确保时间字段格式正确
            categories_list = []
            for category in categories:
                category_dict = {
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'parent_id': category.parent_id,
                    'sort_order': category.sort_order,
                    'status': category.status,
                    'create_time': category.create_time.isoformat() if category.create_time else None,
                    'update_time': category.update_time.isoformat() if category.update_time else None
                }
                categories_list.append(category_dict)
            
            return (categories_list, None)
        except Exception as e:
            return (None, f"获取分类列表失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_by_parent_id(parent_id):
        """
        根据父分类ID获取分类列表
        :param parent_id: 父分类ID
        :return: 成功返回 (分类字典列表, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            category_dal = CategoryDAL(db, redis)
            categories = category_dal.get_by_parent_id(parent_id)
            
            # 转换为字典列表，确保时间字段格式正确
            categories_list = []
            for category in categories:
                category_dict = {
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'parent_id': category.parent_id,
                    'sort_order': category.sort_order,
                    'status': category.status,
                    'create_time': category.create_time.isoformat() if category.create_time else None,
                    'update_time': category.update_time.isoformat() if category.update_time else None
                }
                categories_list.append(category_dict)
            
            return (categories_list, None)
        except Exception as e:
            return (None, f"获取子分类失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def create(category_data):
        """
        创建新分类
        :param category_data: 分类数据字典
        :return: 成功返回 (分类字典, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 验证必填字段
            if 'category_name' not in category_data or not category_data['category_name']:
                return (None, "分类名称不能为空")
            
            # 处理父分类ID
            parent_id = category_data.get('parent_id')
            if parent_id:
                # 检查父分类是否存在
                check_db, check_redis, check_close_func = get_db_redis_direct()
                try:
                    category_dal = CategoryDAL(check_db, check_redis)
                    parent_category = category_dal.get_by_id(parent_id)
                    if not parent_category:
                        return (None, f"父分类ID {parent_id} 不存在")
                finally:
                    check_close_func()
            
            # 创建分类
            db, redis, close_db_func = get_db_redis_direct()
            category_dal = CategoryDAL(db, redis)
            category = category_dal.create(category_data)
            # 转换为字典，确保时间字段格式正确
            category_dict = {
                'category_id': category.category_id,
                'category_name': category.category_name,
                'parent_id': category.parent_id,
                'sort_order': category.sort_order,
                'status': category.status,
                'create_time': category.create_time.isoformat() if category.create_time else None,
                'update_time': category.update_time.isoformat() if category.update_time else None
            }
            return (category_dict, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            # 处理唯一约束冲突
            if 'Duplicate entry' in str(e) and '_category_name_parent_uc' in str(e):
                return (None, "同一父分类下分类名称不能重复")
            return (None, f"创建分类失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def update(category_id, category_data):
        """
        更新分类信息
        :param category_id: 分类ID
        :param category_data: 要更新的分类数据
        :return: 成功返回 (分类字典, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 检查分类是否存在
            db, redis, close_db_func = get_db_redis_direct()
            category_dal = CategoryDAL(db, redis)
            category = category_dal.get_by_id(category_id)
            
            if not category:
                return (None, f"分类ID {category_id} 不存在")
            
            # 处理父分类ID
            if 'parent_id' in category_data:
                parent_id = category_data['parent_id']
                if parent_id != category.parent_id:
                    if parent_id:
                        # 检查新的父分类是否存在
                        parent_category = category_dal.get_by_id(parent_id)
                        if not parent_category:
                            return (None, f"父分类ID {parent_id} 不存在")
            
            # 保存旧状态，用于检查状态变更
            old_status = category.status
            new_status = category_data.get('status', old_status)
            
            # 检查状态是否变更
            if 'status' in category_data and new_status != old_status:
                # 状态从启用变为禁用，递归禁用所有相关实体
                if new_status == 0 and old_status == 1:
                    # 使用状态管理器递归禁用所有相关实体
                    StatusManager.recursively_disable_category(category_id, db, redis)
                # 状态从禁用变为启用，递归启用所有上级分类
                elif new_status == 1 and old_status == 0:
                    # 使用状态管理器递归启用所有相关实体
                    StatusManager.recursively_enable_category(category_id, db, redis)
            
            # 更新分类
            category = category_dal.update(category_id, category_data)
            
            # 确保分类对象存在
            if not category:
                return (None, f"分类ID {category_id} 不存在")
            
            # 返回字典，包含正确格式化的时间字段
            category_dict = {
                'category_id': category.category_id,
                'category_name': category.category_name,
                'parent_id': category.parent_id,
                'sort_order': category.sort_order,
                'status': category.status,
                'create_time': category.create_time.isoformat() if category.create_time else None,
                'update_time': category.update_time.isoformat() if category.update_time else None
            }
            return (category_dict, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            # 处理唯一约束冲突
            if 'Duplicate entry' in str(e) and '_category_name_parent_uc' in str(e):
                return (None, "同一父分类下分类名称不能重复")
            return (None, f"更新分类失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def delete(category_id):
        """
        删除分类
        :param category_id: 分类ID
        :return: 成功返回 (True, None)，失败返回 (False, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            category_dal = CategoryDAL(db, redis)
            object_dal = DetectionObjectDAL(db, redis)
            
            # 检查是否有子分类
            child_count = len(category_dal.get_by_parent_id(category_id))
            if child_count > 0:
                return (False, f"分类ID {category_id} 存在 {child_count} 个子分类，无法删除")
            
            # 检查是否有关联的检测对象
            associated_objects = object_dal.get_by_category_id(category_id)
            object_count = len(associated_objects)
            if object_count > 0:
                return (False, f"分类ID {category_id} 关联了 {object_count} 个检测对象，无法删除")
            
            success = category_dal.delete(category_id)
            return (success, None)
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return (False, f"删除分类失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_category_tree():
        """
        获取分类树结构
        :return: 成功返回 (分类树, None)，失败返回 (None, 错误信息)
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            category_dal = CategoryDAL(db, redis)
            categories = category_dal.get_all()
            
            # 构建分类字典
            category_dict = {}
            category_list = []
            
            # 先将所有分类转换为字典，方便后续处理
            for category in categories:
                category_dict[category.category_id] = {
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'parent_id': category.parent_id,
                    'sort_order': category.sort_order,
                    'status': category.status,
                    'create_time': category.create_time.isoformat() if category.create_time else None,
                    'update_time': category.update_time.isoformat() if category.update_time else None,
                    'children': []
                }
                category_list.append(category_dict[category.category_id])
            
            # 构建树形结构
            category_tree = []
            for category in category_list:
                if not category['parent_id']:
                    # 顶级分类
                    category_tree.append(category)
                else:
                    # 子分类
                    parent_id = category['parent_id']
                    if parent_id in category_dict:
                        category_dict[parent_id]['children'].append(category)
            
            # 按sort_order排序，包括各级子分类
            def sort_by_order(items):
                """递归按sort_order排序"""
                items.sort(key=lambda x: x['sort_order'])
                for item in items:
                    if item['children']:
                        sort_by_order(item['children'])
                return items
            
            sorted_tree = sort_by_order(category_tree)
            return (sorted_tree, None)
        except Exception as e:
            return (None, f"获取分类树失败: {str(e)}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()