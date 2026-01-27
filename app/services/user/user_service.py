# 用户服务类
# 包含用户相关的业务逻辑，如获取用户信息、验证用户等
# 管理操作（创建、更新、删除用户）已移至UserAdminService

from werkzeug.security import check_password_hash
from datetime import datetime
from app.models.user.user import User
from app.extensions import get_db_and_redis, get_db_redis_direct
from app.dal.user_dal import UserDAL


class UserService:
    """用户服务类，处理用户相关的业务逻辑"""
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        根据用户ID获取用户信息，优先从Redis缓存获取
        :param user_id: 用户ID
        :return: 用户对象或None
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            user_dal = UserDAL(db, redis)
            return user_dal.get_by_id(user_id)
        except Exception as e:
            print(f"获取用户失败: {e}")
            return None
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_user_by_username(username):
        """
        根据用户名获取用户信息，优先从Redis缓存获取
        :param username: 用户名
        :return: 用户对象或None
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            user_dal = UserDAL(db, redis)
            return user_dal.get_by_username(username)
        except Exception as e:
            print(f"获取用户失败: {e}")
            return None
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def authenticate_user(username, password):
        """
        验证用户身份
        :param username: 用户名
        :param password: 密码
        :return: 验证成功返回用户对象，失败返回None
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            user_dal = UserDAL(db, redis)
            
            # 先获取用户（不限制is_active）
            user = user_dal.get_by_username(username)
            
            # 验证用户是否存在
            if not user:
                return None
            
            # 验证用户是否被禁用
            if not user.is_active:
                return None
            
            # 验证密码
            if check_password_hash(user.password, password):
                try:
                    # 更新最后登录时间
                    user.last_login_at = datetime.utcnow()
                    db.commit()
                    db.refresh(user)
                    
                    # 清除缓存，确保缓存数据最新
                    user_dal.invalidate_cache(user.id, user.username)
                    
                    return user
                except Exception as e:
                    # 更新最后登录时间失败不影响用户登录
                    if 'db' in locals():
                        db.rollback()
                    return user
            return None
        except Exception as e:
            print(f"验证用户失败: {e}")
            return None
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def invalidate_user_cache(user_id, username):
        """
        使用户缓存失效
        :param user_id: 用户ID
        :param username: 用户名
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            db, redis, close_db_func = get_db_redis_direct()
            user_dal = UserDAL(db, redis)
            user_dal.invalidate_cache(user_id, username)
        except Exception as e:
            # Redis操作失败，记录日志
            print(f"Redis删除用户缓存失败: {e}")
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()