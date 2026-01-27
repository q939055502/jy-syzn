# 范围服务类
# 包含范围相关的业务逻辑，如获取范围信息、创建范围、更新范围、删除范围等

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user.scope import Scope

class ScopeService:
    """范围服务类，处理范围相关的业务逻辑"""
    
    @staticmethod
    def get_scope_by_id(db: Session, scope_id: int) -> Optional[Scope]:
        """
        根据范围ID获取范围信息
        :param db: 数据库会话对象
        :param scope_id: 范围ID
        :return: 范围对象或None
        """
        return db.query(Scope).filter(Scope.id == scope_id).first()
    
    @staticmethod
    def get_scope_by_name(db: Session, name: str) -> Optional[Scope]:
        """
        根据范围名称获取范围信息
        :param db: 数据库会话对象
        :param name: 范围名称
        :return: 范围对象或None
        """
        return db.query(Scope).filter(Scope.name == name).first()
    
    @staticmethod
    def get_scopes(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None, is_system_builtin: Optional[bool] = None) -> List[Scope]:
        """
        获取范围列表
        :param db: 数据库会话对象
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :param is_active: 可选的范围状态过滤
        :param is_system_builtin: 可选的范围类型过滤
        :return: 范围对象列表
        """
        query = db.query(Scope)
        if is_active is not None:
            query = query.filter(Scope.is_active == is_active)
        if is_system_builtin is not None:
            query = query.filter(Scope.is_system_builtin == is_system_builtin)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_scope(db: Session, name: str, display_name: str, description: Optional[str] = None, is_system_builtin: bool = False) -> Scope:
        """
        创建新范围
        :param db: 数据库会话对象
        :param name: 范围标识，必须唯一
        :param display_name: 范围显示名称
        :param description: 范围描述
        :param is_system_builtin: 是否系统内置，默认为False
        :return: 创建的范围对象
        """
        scope = Scope(
            name=name,
            display_name=display_name,
            description=description,
            is_system_builtin=is_system_builtin,
            is_active=True
        )
        db.add(scope)
        db.commit()
        db.refresh(scope)
        return scope
    
    @staticmethod
    def update_scope(db: Session, scope_id: int, **kwargs) -> Optional[Scope]:
        """
        更新范围信息
        :param db: 数据库会话对象
        :param scope_id: 范围ID
        :param kwargs: 要更新的范围信息
        :return: 更新后的范围对象或None
        """
        scope = ScopeService.get_scope_by_id(db, scope_id)
        if scope:
            for key, value in kwargs.items():
                if hasattr(scope, key):
                    setattr(scope, key, value)
            
            try:
                db.commit()
                db.refresh(scope)
                return scope
            except Exception as e:
                db.rollback()
                raise e
        return None
    
    @staticmethod
    def delete_scope(db: Session, scope_id: int) -> bool:
        """
        删除范围
        :param db: 数据库会话对象
        :param scope_id: 范围ID
        :return: 是否删除成功
        """
        scope = ScopeService.get_scope_by_id(db, scope_id)
        if scope:
            try:
                db.delete(scope)
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                raise e
        return False
    
    @staticmethod
    def toggle_scope_active(db: Session, scope_id: int, is_active: bool) -> Optional[Scope]:
        """
        激活或停用范围
        :param db: 数据库会话对象
        :param scope_id: 范围ID
        :param is_active: 要设置的状态
        :return: 更新后的范围对象或None
        """
        return ScopeService.update_scope(db, scope_id, is_active=is_active)