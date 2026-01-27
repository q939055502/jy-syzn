# 权限服务类
# 包含权限相关的业务逻辑，如获取权限信息、创建权限、更新权限、删除权限等

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user.permission import Permission


class PermissionService:
    """权限服务类，处理权限相关的业务逻辑"""
    
    @staticmethod
    def get_permission_by_id(db: Session, permission_id: int) -> Optional[dict]:
        """
        根据权限ID获取权限信息
        :param db: 数据库会话对象
        :param permission_id: 权限ID
        :return: 权限字典或None
        """
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        return permission.to_dict() if permission else None
    
    @staticmethod
    def get_permission_by_code(db: Session, code: str) -> Optional[dict]:
        """
        根据权限代码获取权限信息
        :param db: 数据库会话对象
        :param code: 权限代码
        :return: 权限字典或None
        """
        permission = db.query(Permission).filter(Permission.code == code).first()
        return permission.to_dict() if permission else None
    
    @staticmethod
    def get_permissions(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[dict]:
        """
        获取权限列表
        :param db: 数据库会话对象
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :param is_active: 可选的权限状态过滤
        :return: 权限字典列表
        """
        query = db.query(Permission)
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        permissions = query.offset(skip).limit(limit).all()
        return [permission.to_dict() for permission in permissions]
    
    @staticmethod
    def create_permission(db: Session, code: str, resource: str, action: str, scope: str = 'all', description: Optional[str] = None) -> dict:
        """
        创建新权限
        :param db: 数据库会话对象
        :param code: 权限代码，必须唯一
        :param resource: 资源名称
        :param action: 操作类型
        :param scope: 权限范围. Defaults to 'all'.
        :param description: 权限描述. Defaults to None.
        :return: 创建的权限字典
        """
        # 使用模型类中定义的create_permission静态方法
        permission = Permission.create_permission(code, resource, action, scope, description, db, commit=True)
        return permission.to_dict()
    
    @staticmethod
    def update_permission(db: Session, permission_id: int, **kwargs) -> Optional[dict]:
        """
        更新权限信息
        :param db: 数据库会话对象
        :param permission_id: 权限ID
        :param kwargs: 要更新的权限信息
        :return: 更新后的权限字典或None
        """
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            for key, value in kwargs.items():
                if hasattr(permission, key):
                    setattr(permission, key, value)
            
            try:
                db.commit()
                db.refresh(permission)
                return permission.to_dict()
            except Exception as e:
                db.rollback()
                raise e
        return None
    
    @staticmethod
    def delete_permission(db: Session, permission_id: int) -> bool:
        """
        删除权限
        :param db: 数据库会话对象
        :param permission_id: 权限ID
        :return: 是否删除成功
        """
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            try:
                db.delete(permission)
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                raise e
        return False
    
    @staticmethod
    def toggle_permission_active(db: Session, permission_id: int, is_active: bool) -> Optional[dict]:
        """
        激活或停用权限
        :param db: 数据库会话对象
        :param permission_id: 权限ID
        :param is_active: 要设置的状态
        :return: 更新后的权限字典或None
        """
        return PermissionService.update_permission(db, permission_id, is_active=is_active)
    
    @staticmethod
    def get_permissions_by_resource(db: Session, resource: str, is_active: Optional[bool] = None) -> List[dict]:
        """
        根据资源名称获取权限列表
        :param db: 数据库会话对象
        :param resource: 资源名称
        :param is_active: 可选的权限状态过滤
        :return: 权限字典列表
        """
        query = db.query(Permission).filter(Permission.resource == resource)
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        permissions = query.all()
        return [permission.to_dict() for permission in permissions]
    
    @staticmethod
    def get_permissions_by_action(db: Session, action: str, is_active: Optional[bool] = None) -> List[dict]:
        """
        根据操作类型获取权限列表
        :param db: 数据库会话对象
        :param action: 操作类型
        :param is_active: 可选的权限状态过滤
        :return: 权限字典列表
        """
        query = db.query(Permission).filter(Permission.action == action)
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        permissions = query.all()
        return [permission.to_dict() for permission in permissions]