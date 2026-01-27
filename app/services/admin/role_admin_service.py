# 角色管理员服务类
# 包含角色的管理操作，如创建角色、更新角色、删除角色等
# 这些操作只允许管理员执行

from app.models.user.role import Role
from app.dal.base_dal import BaseDAL
from app.extensions import get_db_and_redis


class RoleAdminService:
    """角色管理员服务类，处理角色的管理操作"""
    
    @staticmethod
    def create_role(db, **kwargs):
        """
        创建新角色
        :param db: 数据库会话
        :param kwargs: 角色数据
        :return: 创建的角色对象或None
        """
        try:
            # 创建角色DAL
            role_dal = BaseDAL(db, None, Role)
            
            # 创建角色
            return role_dal.create(kwargs)
        except Exception as e:
            print(f"创建角色失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def update_role(db, role_id, **kwargs):
        """
        更新角色信息
        :param db: 数据库会话
        :param role_id: 角色ID
        :param kwargs: 要更新的角色信息
        :return: 更新后的角色对象或None
        """
        try:
            # 创建角色DAL
            role_dal = BaseDAL(db, None, Role)
            
            # 更新角色
            return role_dal.update(role_id, kwargs)
        except Exception as e:
            print(f"更新角色失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def delete_role(db, role_id):
        """
        删除角色
        :param db: 数据库会话
        :param role_id: 角色ID
        :return: 是否删除成功
        """
        try:
            # 创建角色DAL
            role_dal = BaseDAL(db, None, Role)
            
            # 删除角色
            return role_dal.delete(role_id)
        except Exception as e:
            print(f"删除角色失败: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def get_roles(db):
        """
        获取所有角色列表
        :param db: 数据库会话
        :return: 角色对象列表
        """
        try:
            # 创建角色DAL
            role_dal = BaseDAL(db, None, Role)
            
            # 获取所有角色
            return role_dal.get_all()
        except Exception as e:
            print(f"获取所有角色失败: {str(e)}")
            return []
    
    @staticmethod
    def get_role_by_id(db, role_id):
        """
        根据ID获取角色详情
        :param db: 数据库会话
        :param role_id: 角色ID
        :return: 角色对象或None
        """
        try:
            # 创建角色DAL
            role_dal = BaseDAL(db, None, Role)
            
            # 获取角色
            return role_dal.get_by_id(role_id)
        except Exception as e:
            print(f"获取角色详情失败: {str(e)}")
            return None
    
    @staticmethod
    def get_role_by_name(db, role_name):
        """
        根据名称获取角色
        :param db: 数据库会话
        :param role_name: 角色名称
        :return: 角色对象或None
        """
        try:
            # 创建角色DAL
            role_dal = BaseDAL(db, None, Role)
            
            # 根据名称获取角色
            return role_dal.get_by_field('role_name', role_name)
        except Exception as e:
            print(f"根据名称获取角色失败: {str(e)}")
            return None
