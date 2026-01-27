# 用户管理员服务类
# 包含用户的管理操作，如创建用户、更新用户、删除用户等
# 这些操作只允许管理员执行

from werkzeug.security import generate_password_hash
from app.models.user.user import User
from app.extensions import get_db_and_redis, get_db_redis_direct
from app.dal.base_dal import BaseDAL


class UserAdminService:
    """用户管理员服务类，处理用户的管理操作"""
    
    @staticmethod
    def create_user(name, username, password):
        """
        创建新用户
        :param name: 用户名
        :param username: 用户登录名
        :param password: 用户密码（明文）
        :return: 创建的用户对象或None
        """
        # 生成密码哈希
        hashed_password = generate_password_hash(password)
        
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库会话和Redis客户端
            db, redis, close_db_func = get_db_redis_direct()
            
            # 创建用户DAL
            from app.dal.user_dal import UserDAL
            user_dal = UserDAL(db, redis)
            
            # 创建新用户对象
            user_data = {
                'name': name,
                'username': username,
                'password': hashed_password
            }
            
            # 创建用户
            return user_dal.create(user_data)
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            if 'db' in locals():
                db.rollback()
            return None
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """
        更新用户信息
        :param user_id: 用户ID
        :param kwargs: 要更新的用户信息
        :return: 更新后的用户对象或None
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库会话和Redis客户端
            db, redis, close_db_func = get_db_redis_direct()
            
            # 创建用户DAL
            from app.dal.user_dal import UserDAL
            user_dal = UserDAL(db, redis)
            
            # 如果更新的是密码，需要重新哈希
            if 'password' in kwargs and kwargs['password']:
                kwargs['password'] = generate_password_hash(kwargs['password'])
            
            # 更新用户
            return user_dal.update(user_id, kwargs)
        except Exception as e:
            print(f"更新用户失败: {str(e)}")
            if 'db' in locals():
                db.rollback()
            return None
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def toggle_user_active(user_id, is_active):
        """
        切换用户激活状态
        :param user_id: 用户ID
        :param is_active: 激活状态
        :return: 更新后的用户字典或None
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库会话和Redis客户端
            db, redis, close_db_func = get_db_redis_direct()
            
            # 创建用户DAL
            from app.dal.user_dal import UserDAL
            user_dal = UserDAL(db, redis)
            
            # 获取用户信息
            user = user_dal.get_by_id(user_id)
            if not user:
                return None
            
            # 更新用户激活状态
            updated_user = user_dal.update(user_id, {'is_active': is_active})
            if not updated_user:
                return None
            
            # 如果是禁用用户，处理令牌失效
            if not is_active:
                # 清除Redis中的用户令牌和信息缓存
                from app.utils.redis_utils import RedisUtils
                
                # 获取用户的访问令牌和刷新令牌
                access_token = RedisUtils.get_cache(redis, f"user:access_token:{user_id}")
                refresh_token = RedisUtils.get_cache(redis, f"user:refresh_token:{user_id}")
                
                # 将令牌添加到黑名单
                from app.services.auth.auth_service import AuthService
                if access_token:
                    AuthService.add_token_to_blacklist(access_token)
                if refresh_token:
                    AuthService.add_token_to_blacklist(refresh_token)
                
                # 清除用户令牌缓存
                RedisUtils.delete_cache(redis, f"user:access_token:{user_id}")
                RedisUtils.delete_cache(redis, f"user:refresh_token:{user_id}")
                
                # 清除用户信息缓存
                RedisUtils.delete_cache(redis, f"user:info:{user_id}")
                
                # 清除用户数据缓存
                user_dal.invalidate_cache(user_id, user.username)
            
            return updated_user.to_dict()
        except Exception as e:
            print(f"切换用户激活状态失败: {str(e)}")
            if 'db' in locals():
                db.rollback()
            return None
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def delete_user(user_id):
        """
        删除用户
        :param user_id: 用户ID
        :return: 是否删除成功
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库会话和Redis客户端
            db, redis, close_db_func = get_db_redis_direct()
            
            # 创建用户DAL
            from app.dal.user_dal import UserDAL
            user_dal = UserDAL(db, redis)
            
            # 删除用户
            return user_dal.delete(user_id)
        except Exception as e:
            print(f"删除用户失败: {str(e)}")
            if 'db' in locals():
                db.rollback()
            return False
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_all_users():
        """
        获取所有用户列表
        :return: 用户对象列表
        """
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            # 获取数据库会话和Redis客户端
            db, redis, close_db_func = get_db_redis_direct()
            
            # 创建用户DAL
            user_dal = BaseDAL(db, redis, User)
            
            # 获取所有用户
            return user_dal.get_all()
        except Exception as e:
            print(f"获取所有用户失败: {str(e)}")
            return []
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()

    @staticmethod
    def get_users(db, redis, page=1, limit=10):
        """
        获取用户列表
        :param db: 数据库会话
        :param redis: Redis客户端
        :param page: 页码，默认1
        :param limit: 每页数量，默认10
        :return: 用户列表和总数
        """
        # 创建用户DAL
        user_dal = BaseDAL(db, redis, User)
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 使用joinedload预加载关联数据，避免N+1查询
        from sqlalchemy.orm import joinedload
        users = user_dal.db.query(User).options(
            joinedload(User.roles)
        ).offset(offset).limit(limit).all()
        
        # 转换为字典列表，并添加is_online字段
        users_list = []
        for user in users:
            user_dict = user.to_dict()
            # 检查用户是否在线
            from app.utils.redis_utils import RedisUtils
            access_key = f"user:access_token:{user.id}"
            access_token = RedisUtils.get_cache(redis, access_key)
            user_dict['is_online'] = access_token is not None
            
            # 添加角色信息
            user_dict['roles'] = [role.name for role in user.roles]
            
            users_list.append(user_dict)
        
        # 获取总数
        total = user_dal.count()
        
        return users_list, total

    @staticmethod
    def get_user(db, redis, user_id):
        """
        获取用户详情
        :param db: 数据库会话
        :param redis: Redis客户端
        :param user_id: 用户ID
        :return: 用户对象或None
        """
        # 创建用户DAL
        user_dal = BaseDAL(db, redis, User)
        
        # 使用joinedload预加载关联数据
        from sqlalchemy.orm import joinedload
        from app.models.user.role import Role
        user = user_dal.db.query(User).options(
            joinedload(User.roles).joinedload(Role.permissions),
            joinedload(User.permissions)
        ).filter(User.id == user_id).first()
        
        if user:
            user_dict = user.to_dict()
            # 检查用户是否在线
            from app.utils.redis_utils import RedisUtils
            access_key = f"user:access_token:{user_id}"
            access_token = RedisUtils.get_cache(redis, access_key)
            user_dict['is_online'] = access_token is not None
            
            # 添加角色信息
            user_dict['roles'] = [role.name for role in user.roles]
            
            # 添加权限信息
            all_permissions = user.get_permission_codes()
            user_dict['permissions'] = list(all_permissions)
            
            return user_dict
        return None
