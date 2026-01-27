from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Base
from datetime import datetime

class ApiPermission(Base):
    """接口权限绑定关系模型类
    用于存储接口与权限的绑定关系，实现接口级别的权限控制
    """
    __tablename__ = 'api_permissions'  # 数据库表名

    id = Column(Integer, primary_key=True, index=True)  # 主键ID，索引
    path = Column(String(255), nullable=False, index=True)  # 接口路径，非空，索引
    method = Column(String(10), nullable=False, index=True)  # 接口方法，非空，索引
    description = Column(String(200))  # 接口描述
    is_active = Column(Boolean, default=True)  # 是否启用，默认为True
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间，自动更新
    
    # 外键关联
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False, index=True)  # 关联的权限ID
    
    # 关系定义
    permission = relationship('Permission', backref='api_permissions')  # 反向引用权限

    def __repr__(self):
        """返回接口权限绑定的字符串表示"""
        return f'<ApiPermission {self.path} [{self.method}] - Permission: {self.permission.code}>'

    @staticmethod
    def create_api_permission(path, method, permission_id, description=None, is_active=True, db=None, commit=True):
        """创建新的接口权限绑定

        Args:
            path (str): 接口路径
            method (str): 接口方法
            permission_id (int): 权限ID
            description (str, optional): 接口描述. Defaults to None.
            is_active (bool, optional): 是否启用. Defaults to True.
            db (Session, optional): 数据库会话对象. Defaults to None.
            commit (bool, optional): 是否立即提交到数据库. Defaults to True.

        Returns:
            ApiPermission: 创建的接口权限绑定对象

        Raises:
            Exception: 当数据库操作失败时抛出异常
        """
        api_permission = ApiPermission(
            path=path,
            method=method,
            permission_id=permission_id,
            description=description,
            is_active=is_active
        )
        if db:
            db.add(api_permission)
            if commit:
                try:
                    db.commit()
                except Exception as e:
                    db.rollback()
                    raise e
        return api_permission

    @staticmethod
    def get_api_permissions_by_permission(permission_id, db=None):
        """根据权限ID获取所有关联的接口权限绑定

        Args:
            permission_id (int): 权限ID
            db (Session, optional): 数据库会话对象. Defaults to None.

        Returns:
            List[ApiPermission]: 接口权限绑定列表
        """
        if db is None:
            from app.extensions import db as extension_db
            db = next(extension_db.get_db())
        
        return db.query(ApiPermission).filter_by(permission_id=permission_id, is_active=True).all()

    @staticmethod
    def get_permission_by_api(path, method, db=None):
        """根据接口路径和方法获取关联的权限

        Args:
            path (str): 接口路径
            method (str): 接口方法
            db (Session, optional): 数据库会话对象. Defaults to None.

        Returns:
            Permission: 关联的权限对象，如果没有找到则返回None
        """
        if db is None:
            from app.extensions import db as extension_db
            db = next(extension_db.get_db())
        
        api_permission = db.query(ApiPermission).filter_by(
            path=path, method=method, is_active=True
        ).first()
        
        return api_permission.permission if api_permission else None