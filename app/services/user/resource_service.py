# 资源服务类
# 包含资源相关的业务逻辑，如获取资源信息、创建资源、更新资源、删除资源等

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user.resource import Resource

class ResourceService:
    """资源服务类，处理资源相关的业务逻辑"""
    
    @staticmethod
    def get_resource_by_id(db: Session, resource_id: int) -> Optional[Resource]:
        """
        根据资源ID获取资源信息
        :param db: 数据库会话对象
        :param resource_id: 资源ID
        :return: 资源对象或None
        """
        return db.query(Resource).filter(Resource.id == resource_id).first()
    
    @staticmethod
    def get_resource_by_name(db: Session, name: str) -> Optional[Resource]:
        """
        根据资源名称获取资源信息
        :param db: 数据库会话对象
        :param name: 资源名称
        :return: 资源对象或None
        """
        return db.query(Resource).filter(Resource.name == name).first()
    
    @staticmethod
    def get_resources(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None, is_system_builtin: Optional[bool] = None) -> List[Resource]:
        """
        获取资源列表
        :param db: 数据库会话对象
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :param is_active: 可选的资源状态过滤
        :param is_system_builtin: 可选的资源类型过滤
        :return: 资源对象列表
        """
        query = db.query(Resource)
        if is_active is not None:
            query = query.filter(Resource.is_active == is_active)
        if is_system_builtin is not None:
            query = query.filter(Resource.is_system_builtin == is_system_builtin)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_resource(db: Session, name: str, display_name: str, description: Optional[str] = None, is_system_builtin: bool = False) -> Resource:
        """
        创建新资源
        :param db: 数据库会话对象
        :param name: 资源标识，必须唯一
        :param display_name: 资源显示名称
        :param description: 资源描述
        :param is_system_builtin: 是否系统内置，默认为False
        :return: 创建的资源对象
        """
        resource = Resource(
            name=name,
            display_name=display_name,
            description=description,
            is_system_builtin=is_system_builtin,
            is_active=True
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource
    
    @staticmethod
    def update_resource(db: Session, resource_id: int, **kwargs) -> Optional[Resource]:
        """
        更新资源信息
        :param db: 数据库会话对象
        :param resource_id: 资源ID
        :param kwargs: 要更新的资源信息
        :return: 更新后的资源对象或None
        """
        resource = ResourceService.get_resource_by_id(db, resource_id)
        if resource:
            for key, value in kwargs.items():
                if hasattr(resource, key):
                    setattr(resource, key, value)
            
            try:
                db.commit()
                db.refresh(resource)
                return resource
            except Exception as e:
                db.rollback()
                raise e
        return None
    
    @staticmethod
    def delete_resource(db: Session, resource_id: int) -> bool:
        """
        删除资源
        :param db: 数据库会话对象
        :param resource_id: 资源ID
        :return: 是否删除成功
        """
        resource = ResourceService.get_resource_by_id(db, resource_id)
        if resource:
            try:
                db.delete(resource)
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                raise e
        return False
    
    @staticmethod
    def toggle_resource_active(db: Session, resource_id: int, is_active: bool) -> Optional[Resource]:
        """
        激活或停用资源
        :param db: 数据库会话对象
        :param resource_id: 资源ID
        :param is_active: 要设置的状态
        :return: 更新后的资源对象或None
        """
        return ResourceService.update_resource(db, resource_id, is_active=is_active)