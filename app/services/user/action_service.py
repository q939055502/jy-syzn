# 动作服务类
# 包含动作相关的业务逻辑，如获取动作信息、创建动作、更新动作、删除动作等

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user.action import Action

class ActionService:
    """动作服务类，处理动作相关的业务逻辑"""
    
    @staticmethod
    def get_action_by_id(db: Session, action_id: int) -> Optional[Action]:
        """
        根据动作ID获取动作信息
        :param db: 数据库会话对象
        :param action_id: 动作ID
        :return: 动作对象或None
        """
        return db.query(Action).filter(Action.id == action_id).first()
    
    @staticmethod
    def get_action_by_name(db: Session, name: str) -> Optional[Action]:
        """
        根据动作名称获取动作信息
        :param db: 数据库会话对象
        :param name: 动作名称
        :return: 动作对象或None
        """
        return db.query(Action).filter(Action.name == name).first()
    
    @staticmethod
    def get_actions(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None, is_system_builtin: Optional[bool] = None) -> List[Action]:
        """
        获取动作列表
        :param db: 数据库会话对象
        :param skip: 跳过的记录数
        :param limit: 返回的最大记录数
        :param is_active: 可选的动作状态过滤
        :param is_system_builtin: 可选的动作类型过滤
        :return: 动作对象列表
        """
        query = db.query(Action)
        if is_active is not None:
            query = query.filter(Action.is_active == is_active)
        if is_system_builtin is not None:
            query = query.filter(Action.is_system_builtin == is_system_builtin)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_action(db: Session, name: str, display_name: str, description: Optional[str] = None, is_system_builtin: bool = False) -> Action:
        """
        创建新动作
        :param db: 数据库会话对象
        :param name: 动作标识，必须唯一
        :param display_name: 动作显示名称
        :param description: 动作描述
        :param is_system_builtin: 是否系统内置，默认为False
        :return: 创建的动作对象
        """
        action = Action(
            name=name,
            display_name=display_name,
            description=description,
            is_system_builtin=is_system_builtin,
            is_active=True
        )
        db.add(action)
        db.commit()
        db.refresh(action)
        return action
    
    @staticmethod
    def update_action(db: Session, action_id: int, **kwargs) -> Optional[Action]:
        """
        更新动作信息
        :param db: 数据库会话对象
        :param action_id: 动作ID
        :param kwargs: 要更新的动作信息
        :return: 更新后的动作对象或None
        """
        action = ActionService.get_action_by_id(db, action_id)
        if action:
            for key, value in kwargs.items():
                if hasattr(action, key):
                    setattr(action, key, value)
            
            try:
                db.commit()
                db.refresh(action)
                return action
            except Exception as e:
                db.rollback()
                raise e
        return None
    
    @staticmethod
    def delete_action(db: Session, action_id: int) -> bool:
        """
        删除动作
        :param db: 数据库会话对象
        :param action_id: 动作ID
        :return: 是否删除成功
        """
        action = ActionService.get_action_by_id(db, action_id)
        if action:
            try:
                db.delete(action)
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                raise e
        return False
    
    @staticmethod
    def toggle_action_active(db: Session, action_id: int, is_active: bool) -> Optional[Action]:
        """
        激活或停用动作
        :param db: 数据库会话对象
        :param action_id: 动作ID
        :param is_active: 要设置的状态
        :return: 更新后的动作对象或None
        """
        return ActionService.update_action(db, action_id, is_active=is_active)