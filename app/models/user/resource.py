# 资源模型类
# 用于表示系统中的资源，支持分层动态权限管理

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.extensions import Base
from datetime import datetime

class Resource(Base):
    """资源模型类
    用于表示系统中的资源，定义了权限管理的资源对象
    支持分层管理：系统内置资源和业务自定义资源
    """
    __tablename__ = 'resources'  # 数据库表名

    id = Column(Integer, primary_key=True, index=True)  # 资源ID，主键，索引
    name = Column(String(50), unique=True, index=True, nullable=False)  # 资源标识，唯一，索引，非空
    display_name = Column(String(100), nullable=False)  # 资源显示名称，非空
    description = Column(String(200))  # 资源描述
    is_system_builtin = Column(Boolean, default=False)  # 是否系统内置，默认为False
    is_active = Column(Boolean, default=True)  # 是否激活，默认为True
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间，自动更新
    
    # 关系定义 - 后续在Permission模型中定义多对多关系
    
    def __repr__(self):
        """返回资源的字符串表示"""
        return f'<Resource {self.name} (ID: {self.id})>'
    
    def to_dict(self):
        """将资源对象转换为字典

        Returns:
            dict: 包含资源信息的字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "is_system_builtin": self.is_system_builtin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
