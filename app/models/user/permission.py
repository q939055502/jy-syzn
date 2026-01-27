from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Base
from datetime import datetime  # 导入日期时间相关模块

# 角色-权限关联表将从user_role.py导入

from app.models.associations import role_permissions

# 导入资源、动作、范围模型
from app.models.user.resource import Resource
from app.models.user.action import Action
from app.models.user.scope import Scope

# 用户-权限直接关联表
user_permissions = Table('user_permissions', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('expires_at', DateTime)
)

# 导入新创建的关联表
from app.models.associations import permission_resources, permission_actions, permission_scopes

class Permission(Base):
    """权限模型类
    用于表示系统中的权限，定义了对资源的操作许可
    支持分层动态权限管理，关联资源、动作、范围
    """
    __tablename__ = 'permissions'  # 数据库表名

    id = Column(Integer, primary_key=True, index=True)  # 权限ID，主键，索引
    code = Column(String(100), unique=True, index=True, nullable=False)  # 权限代码，唯一，索引，非空
    
    # 保留原有字段，支持向后兼容，逐步过渡到新的关联关系
    resource = Column(String(50), nullable=False)  # 资源名称，非空
    action = Column(String(50), nullable=False)  # 操作类型，非空
    scope = Column(String(50), default='all')  # 权限范围，默认为'all'，可选值：'all', 'own', 'specific'
    
    description = Column(String(200))  # 权限描述
    is_active = Column(Boolean, default=True)  # 是否激活，默认为True
    is_system_builtin = Column(Boolean, default=False)  # 是否系统内置，默认为False
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间，自动更新
    
    # 新增关联关系 - 多对多关系
    resources = relationship('Resource', secondary=permission_resources, backref='permissions')  # 权限关联的资源，多对多关系
    actions = relationship('Action', secondary=permission_actions, backref='permissions')  # 权限关联的动作，多对多关系
    scopes = relationship('Scope', secondary=permission_scopes, backref='permissions')  # 权限关联的范围，多对多关系
    
    # 原有关系定义
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')  # 权限所属的角色，多对多关系
    users = relationship('User', secondary=user_permissions, back_populates='permissions')  # 拥有该权限的用户，多对多直接关联关系

    def __repr__(self):
        """返回权限的字符串表示"""
        return f'<Permission {self.code} (ID: {self.id})>'

    def __hash__(self):
        """定义Permission对象的哈希方法，使其可以用于集合操作

        Returns:
            int: 基于权限ID的哈希值
        """
        return hash(self.id)

    def to_dict(self):
        """将权限对象转换为字典

        Returns:
            dict: 包含权限信息的字典
        """
        return {
            "id": self.id,
            "code": self.code,
            "resource": self.resource,
            "action": self.action,
            "scope": self.scope,
            "description": self.description,
            "is_active": self.is_active,
            "is_system_builtin": self.is_system_builtin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def create_permission(code, resource, action, scope='all', description=None, db=None, commit=True):
        """创建新权限

        Args:
            code (str): 权限代码，必须唯一
            resource (str): 资源名称
            action (str): 操作类型
            scope (str, optional): 权限范围. Defaults to 'all'.
            description (str, optional): 权限描述. Defaults to None.
            db (Session, optional): 数据库会话对象. Defaults to None.
            commit (bool, optional): 是否立即提交到数据库. Defaults to True.

        Returns:
            Permission: 创建的权限对象

        Raises:
            Exception: 当数据库操作失败时抛出异常
        """
        permission = Permission(
            code=code,
            resource=resource,
            action=action,
            scope=scope,
            description=description
        )
        if db:
            db.add(permission)
            if commit:
                try:
                    db.commit()
                except Exception as e:
                    db.rollback()
                    raise e
        return permission




