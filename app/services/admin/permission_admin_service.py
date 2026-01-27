# 权限管理员服务类
# 包含权限的管理操作，如创建权限、更新权限、删除权限等
# 这些操作只允许管理员执行

from app.models.user.permission import Permission
from app.dal.base_dal import BaseDAL
from app.extensions import get_db_and_redis


class PermissionAdminService:
    """权限管理员服务类，处理权限的管理操作"""
    
    @staticmethod
    def create_permission(db, **kwargs):
        """
        创建新权限
        :param db: 数据库会话
        :param kwargs: 权限数据
        :return: 创建的权限对象或None
        """
        try:
            # 创建权限DAL
            permission_dal = BaseDAL(db, None, Permission)
            
            # 创建权限
            return permission_dal.create(kwargs)
        except Exception as e:
            print(f"创建权限失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def update_permission(db, permission_id, **kwargs):
        """
        更新权限信息
        :param db: 数据库会话
        :param permission_id: 权限ID
        :param kwargs: 要更新的权限信息
        :return: 更新后的权限对象或None
        """
        try:
            # 创建权限DAL
            permission_dal = BaseDAL(db, None, Permission)
            
            # 更新权限
            return permission_dal.update(permission_id, kwargs)
        except Exception as e:
            print(f"更新权限失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def delete_permission(db, permission_id):
        """
        删除权限
        :param db: 数据库会话
        :param permission_id: 权限ID
        :return: 是否删除成功
        """
        try:
            # 创建权限DAL
            permission_dal = BaseDAL(db, None, Permission)
            
            # 删除权限
            return permission_dal.delete(permission_id)
        except Exception as e:
            print(f"删除权限失败: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def get_permissions(db, skip=0, limit=100, is_active=None):
        """
        获取权限列表
        :param db: 数据库会话
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :param is_active: 权限状态过滤
        :return: 权限对象列表
        """
        try:
            # 创建权限DAL
            permission_dal = BaseDAL(db, None, Permission)
            
            # 构建查询
            query = permission_dal.db.query(Permission)
            
            # 添加过滤条件
            if is_active is not None:
                query = query.filter_by(is_active=is_active)
            
            # 执行查询
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            print(f"获取权限列表失败: {str(e)}")
            return []
    
    @staticmethod
    def get_permission_by_id(db, permission_id):
        """
        根据ID获取权限详情
        :param db: 数据库会话
        :param permission_id: 权限ID
        :return: 权限对象或None
        """
        try:
            # 创建权限DAL
            permission_dal = BaseDAL(db, None, Permission)
            
            # 获取权限
            return permission_dal.get_by_id(permission_id)
        except Exception as e:
            print(f"获取权限详情失败: {str(e)}")
            return None
    
    @staticmethod
    def get_permission_by_code(db, code):
        """
        根据代码获取权限
        :param db: 数据库会话
        :param code: 权限代码
        :return: 权限对象或None
        """
        try:
            # 创建权限DAL
            permission_dal = BaseDAL(db, None, Permission)
            
            # 根据代码获取权限
            return permission_dal.get_by_field('code', code)
        except Exception as e:
            print(f"根据代码获取权限失败: {str(e)}")
            return None
    
    @staticmethod
    def toggle_permission_active(db, permission_id, is_active):
        """
        切换权限激活状态
        :param db: 数据库会话
        :param permission_id: 权限ID
        :param is_active: 激活状态
        :return: 更新后的权限对象或None
        """
        try:
            # 创建权限DAL
            permission_dal = BaseDAL(db, None, Permission)
            
            # 更新权限激活状态
            return permission_dal.update(permission_id, {'is_active': is_active})
        except Exception as e:
            print(f"切换权限激活状态失败: {str(e)}")
            db.rollback()
            return None
