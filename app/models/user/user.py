# 用户模型类
# 基于SQLAlchemy的ORM模型，用于表示用户数据和与数据库的交互

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.extensions import Base
from app.models.associations import user_roles
from app.models.user.permission import user_permissions


class User(Base):
    """用户模型类，对应数据库中的users表"""
    # 表名
    __tablename__ = 'users'
    
    # 主键
    id = Column(Integer, primary_key=True)
    
    # 基本信息
    name = Column(String(100), nullable=False)
    username = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # 关系定义
    # 与角色的多对多关系
    roles = relationship('Role', secondary=user_roles, back_populates='users',
                        foreign_keys=[user_roles.c.user_id, user_roles.c.role_id])
    # 与权限的多对多直接关联关系
    permissions = relationship('Permission', secondary=user_permissions, back_populates='users')
    
    def __repr__(self):
        """返回用户对象的字符串表示"""
        return f"<User {self.username} ({self.id})>"
    
    def get_all_permissions(self):
        """
        获取用户的所有权限，包括直接分配的权限和通过角色继承的权限
        
        Returns:
            set: 包含所有权限对象的集合
        """
        all_permissions = set(self.permissions)  # 直接分配给用户的权限
        
        # 通过角色获取权限
        for role in self.roles:
            role_permissions = role.get_all_permissions()
            all_permissions.update(role_permissions)
        
        return all_permissions
    
    def get_permission_codes(self):
        """
        获取用户的所有权限代码，包括直接分配的权限和通过角色继承的权限
        
        Returns:
            set: 包含所有权限代码的集合
        """
        codes = {permission.code for permission in self.permissions}  # 直接分配的权限代码
        
        # 通过角色获取权限代码
        for role in self.roles:
            role_codes = role.get_permission_codes()
            codes.update(role_codes)
        
        return codes
    
    def has_permission(self, code):
        """
        检查用户是否拥有指定的权限
        
        Args:
            code: 权限代码
            
        Returns:
            bool: True表示拥有该权限，False表示没有
        """
        return code in self.get_permission_codes()
    
    def check_resource_permission(self, resource: str, action: str, scope: str = 'all') -> bool:
        """
        检查用户是否拥有指定资源和动作的权限，添加资源和动作的存在性检查
        
        Args:
            resource: 资源名称
            action: 操作类型
            scope: 权限范围（默认：all）
            
        Returns:
            bool: True表示拥有该权限，False表示没有
        """
        # 1. 检查资源是否存在
        if not resource:
            return False
        
        # 2. 检查动作是否存在
        if not action:
            return False
        
        # 3. 构造权限代码
        permission_code = f"{resource}_{action}"
        
        # 4. 检查用户是否拥有该权限
        return self.has_permission(permission_code)
    
    def to_dict(self):
        """
        将用户对象转换为字典，用于API响应
        :return: 包含用户信息的字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
