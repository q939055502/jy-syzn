from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.extensions import Base
from datetime import datetime  # 导入日期时间相关模块
from app.models.associations import user_roles, role_permissions

class Role(Base):
    """角色模型类
    用于表示系统中的角色，角色可以拥有多个权限，也可以有父角色
    """
    __tablename__ = 'roles'  # 数据库表名

    id = Column(Integer, primary_key=True, index=True)  # 角色ID，主键，索引
    name = Column(String(50), unique=True, index=True, nullable=False)  # 角色名称，唯一，索引，非空
    description = Column(Text)  # 角色描述
    parent_id = Column(Integer, ForeignKey('roles.id'))  # 父角色ID，外键关联自身表
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间，自动更新
    is_active = Column(Boolean, default=True)  # 是否激活，默认为True

    # 关系定义
    parent = relationship('Role', remote_side=[id], back_populates='children')  # 父角色关系
    children = relationship('Role', remote_side=[parent_id], back_populates='parent')  # 子角色关系
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')  # 角色拥有的权限，多对多关系
    users = relationship('User', secondary=user_roles, back_populates='roles',
                        foreign_keys=[user_roles.c.role_id, user_roles.c.user_id])  # 拥有该角色的用户，多对多关系

    def __repr__(self):
        """返回角色的字符串表示"""
        return f'<Role {self.name} (ID: {self.id})>'

    def get_all_permissions(self):
        """获取角色及其父角色的所有权限

        Returns:
            set: 包含所有权限对象的集合
        """
        permissions = set(self.permissions)  # 当前角色的权限
        if self.parent:  # 如果有父角色
            permissions.update(self.parent.get_all_permissions())  # 递归获取父角色的权限
        return permissions

    def get_permission_codes(self):
        """获取角色及其父角色的所有权限代码

        Returns:
            set: 包含所有权限代码的集合
        """
        codes = {permission.code for permission in self.permissions}  # 当前角色的权限代码
        if self.parent:  # 如果有父角色
            codes.update(self.parent.get_permission_codes())  # 递归获取父角色的权限代码
        return codes