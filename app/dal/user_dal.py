# 用户数据访问层
# 封装用户相关的数据库和Redis操作，确保数据一致性

from typing import Optional, List, Dict
from sqlalchemy.orm import Session, joinedload
from redis import Redis
from app.models.user.user import User
from app.dal.base_dal import BaseDAL


class UserDAL(BaseDAL):
    """用户数据访问层，处理用户相关的数据访问操作"""
    
    def __init__(self, db: Session, redis: Redis):
        super().__init__(db, redis, User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        :param username: 用户名
        :return: 用户实例，不存在则返回None
        """
        # 直接从数据库查询，预加载roles和permissions关系
        # 避免Redis缓存带来的序列化/反序列化问题
        instance = self.db.query(self.model).options(
            joinedload(User.roles),
            joinedload(User.permissions)
        ).filter_by(username=username).first()
        
        return instance
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户身份
        :param username: 用户名
        :param password: 密码
        :return: 验证成功返回用户实例，否则返回None
        """
        # 直接从数据库查询，不使用缓存，预加载roles和permissions关系
        instance = self.db.query(self.model).options(
            joinedload(User.roles),
            joinedload(User.permissions)
        ).filter_by(username=username, is_active=True).first()
        return instance
    
    def invalidate_cache(self, user_id: int, username: str) -> None:
        """
        使用户缓存失效
        :param user_id: 用户ID
        :param username: 用户名
        """
        try:
            # 删除ID缓存
            self.delete_cache(self._get_cache_key(user_id))
            # 删除用户名缓存
            self.delete_cache(f"{self.cache_prefix}username:{username}")
        except Exception as e:
            print(f"Redis删除用户缓存失败: {e}")