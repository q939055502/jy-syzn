# 统一管理所有多对多中间表
# 包含检测模块和用户模块的多对多关系定义

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table, Boolean, Numeric, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.extensions import Base

# 用户模块多对多中间表

# 用户-角色关联表
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('created_by', Integer, ForeignKey('users.id')),
    Column('is_active', Boolean, default=True)
)

# 角色-权限关联表
role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('created_by', Integer, ForeignKey('users.id')),
    Column('is_active', Boolean, default=True),
    extend_existing=True
)

# 权限-资源关联表
permission_resources = Table('permission_resources', Base.metadata,
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('resource_id', Integer, ForeignKey('resources.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('is_active', Boolean, default=True),
    extend_existing=True
)

# 权限-动作关联表
permission_actions = Table('permission_actions', Base.metadata,
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('action_id', Integer, ForeignKey('actions.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('is_active', Boolean, default=True),
    extend_existing=True
)

# 权限-范围关联表
permission_scopes = Table('permission_scopes', Base.metadata,
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('scope_id', Integer, ForeignKey('scopes.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('is_active', Boolean, default=True),
    extend_existing=True
)

# 检测模块多对多中间表

# DetectionParam和DetectionStandard的多对多关系表
class DetectionParamStandard(Base):
    """检测参数与检测规范的多对多关系表
    
    用于存储检测参数和检测规范之间的关联关系，一个参数可以使用多个规范，
    一个规范也可以被多个参数使用。
    """
    __tablename__ = 'detection_param_standard'
    
    # 复合主键
    param_id = Column(Integer, ForeignKey('detection_param.param_id'), primary_key=True, comment='检测参数ID')
    standard_id = Column(Integer, ForeignKey('detection_standard.standard_id'), primary_key=True, comment='检测规范ID')
    
    # 额外字段
    is_main = Column(Integer, default=0, comment='是否主规范：1=主规范，0=辅助规范')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f"<DetectionParamStandard param_id={self.param_id}, standard_id={self.standard_id}>"
    
    def to_dict(self):
        return {
            'param_id': self.param_id,
            'standard_id': self.standard_id,
            'is_main': self.is_main,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }

# 导出所有关联表和中间表模型
__all__ = ['user_roles', 'role_permissions', 'permission_resources', 'permission_actions', 'permission_scopes', 'DetectionParamStandard']
