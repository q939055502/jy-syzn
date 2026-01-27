# 认证服务类
# 包含JWT令牌生成、验证和刷新等功能

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from werkzeug.security import check_password_hash
from app.models.user.user import User
from app.models.user.role import Role
from config import config
from app.services.user.user_service import UserService


class AuthService:
    """认证服务类，处理JWT令牌相关操作"""
    
    # 获取配置
    app_config = config['development']
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        生成access token
        :param data: 要包含在token中的数据
        :param expires_delta: token有效期
        :return: 生成的JWT token
        """
        to_encode = data.copy()
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=AuthService.app_config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # 添加过期时间到payload
        to_encode.update({"exp": expire})
        
        # 生成token
        encoded_jwt = jwt.encode(to_encode, AuthService.app_config.JWT_SECRET_KEY, algorithm=AuthService.app_config.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        生成refresh token
        :param data: 要包含在token中的数据
        :param expires_delta: token有效期
        :return: 生成的JWT token
        """
        to_encode = data.copy()
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=AuthService.app_config.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # 添加过期时间到payload
        to_encode.update({"exp": expire})
        
        # 生成token
        encoded_jwt = jwt.encode(to_encode, AuthService.app_config.JWT_SECRET_KEY, algorithm=AuthService.app_config.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def cache_user_info(user_id: int, user_info: dict) -> bool:
        """
        缓存用户信息到Redis
        :param user_id: 用户ID
        :param user_info: 用户信息
        :return: 缓存成功返回True，失败返回False
        """
        try:
            from app.extensions import redis_client
            if redis_client:
                from app.utils.redis_utils import RedisUtils
                
                # 缓存用户信息，过期时间与访问令牌一致
                cache_key = f"user:info:{user_id}"
                return RedisUtils.set_cache(redis_client, cache_key, user_info, AuthService.app_config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            else:
                return False
        except Exception as e:
            print(f"缓存用户信息失败: {e}")
            return False
    
    @staticmethod
    def cache_tokens(user_id: int, access_token: str, refresh_token: str) -> tuple[bool, bool]:
        """
        缓存令牌到Redis
        :param user_id: 用户ID
        :param access_token: 访问令牌
        :param refresh_token: 刷新令牌
        :return: 元组，第一个元素表示缓存成功与否，第二个元素表示是否有其他设备登录
        """
        try:
            from app.extensions import redis_client
            if redis_client:
                from app.utils.redis_utils import RedisUtils
                
                # 检查用户是否已经在线
                access_key = f"user:access_token:{user_id}"
                refresh_key = f"user:refresh_token:{user_id}"
                
                # 先获取旧令牌
                old_access_token = RedisUtils.get_cache(redis_client, access_key)
                old_refresh_token = RedisUtils.get_cache(redis_client, refresh_key)
                
                # 缓存访问令牌，过期时间与令牌一致
                access_ttl = AuthService.app_config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                
                # 缓存刷新令牌，过期时间与令牌一致
                refresh_ttl = AuthService.app_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
                
                # 更新缓存
                RedisUtils.set_cache(redis_client, access_key, access_token, access_ttl)
                RedisUtils.set_cache(redis_client, refresh_key, refresh_token, refresh_ttl)
                
                # 如果存在旧的访问令牌，将其添加到黑名单
                if old_access_token and old_access_token != access_token:
                    # 将旧的访问令牌添加到黑名单
                    AuthService.add_token_to_blacklist(old_access_token)
                    # 将旧的刷新令牌添加到黑名单
                    if old_refresh_token:
                        AuthService.add_token_to_blacklist(old_refresh_token)
                    return True, True
                
                return True, False
            else:
                return False, False
        except Exception as e:
            print(f"缓存令牌失败: {e}")
            return False, False
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        验证JWT token
        :param token: 要验证的token
        :return: 验证成功返回payload，失败返回None
        """
        try:
            # 先检查令牌是否在黑名单中
            from app.extensions import redis_client
            if redis_client:
                from app.utils.redis_utils import RedisUtils
                # 检查令牌是否在黑名单中，每个令牌单独存储
                blacklist_key = f"token:blacklist:{token}"
                if RedisUtils.get_cache(redis_client, blacklist_key) is not None:
                    return None
            
            # 解码token
            payload = jwt.decode(token, AuthService.app_config.JWT_SECRET_KEY, algorithms=[AuthService.app_config.JWT_ALGORITHM])
            
            # 获取用户名
            username = payload.get("sub")
            if not username:
                return None
            
            # 获取用户ID
            user = UserService.get_user_by_username(username)
            if not user or not user.is_active:
                return None
            
            # 检查令牌是否为最新的
            if redis_client:
                from app.utils.redis_utils import RedisUtils
                cached_access_token = RedisUtils.get_cache(redis_client, f"user:access_token:{user.id}")
                if cached_access_token and cached_access_token != token:
                    # 令牌不一致，说明有新的登录，当前令牌无效
                    return None
            
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def add_token_to_blacklist(token: str) -> bool:
        """
        将令牌添加到黑名单
        :param token: 要添加到黑名单的令牌
        :return: 添加成功返回True，失败返回False
        """
        try:
            from app.extensions import redis_client
            if not redis_client:
                return False
            
            from app.utils.redis_utils import RedisUtils
            
            # 解析令牌，获取过期时间
            payload = jwt.decode(token, AuthService.app_config.JWT_SECRET_KEY, algorithms=[AuthService.app_config.JWT_ALGORITHM], options={"verify_exp": False})
            exp = payload.get('exp')
            
            # 计算令牌剩余有效期
            import time
            current_time = time.time()
            if exp and current_time < exp:
                # 如果令牌未过期，计算剩余有效期并设置黑名单过期时间
                ttl = int(exp - current_time)
                # 为每个令牌单独创建一个键，设置独立的过期时间
                blacklist_key = f"token:blacklist:{token}"
                RedisUtils.set_cache(redis_client, blacklist_key, "1", ttl)
                return True
            return False
        except Exception as e:
            print(f"添加令牌到黑名单失败: {e}")
            return False
    
    @staticmethod
    def get_user_from_token(token: str) -> Optional[User]:
        """
        从token中获取用户
        :param token: JWT token
        :return: 用户对象或None
        """
        try:
            # 先检查令牌是否在黑名单中
            from app.extensions import redis_client
            if redis_client:
                from app.utils.redis_utils import RedisUtils
                # 检查令牌是否在黑名单中
                blacklist_key = f"token:blacklist:{token}"
                if RedisUtils.get_cache(redis_client, blacklist_key) is not None:
                    return None
            
            # 解码token
            payload = jwt.decode(token, AuthService.app_config.JWT_SECRET_KEY, algorithms=[AuthService.app_config.JWT_ALGORITHM])
            
            # 获取用户名
            username: str = payload.get("sub")
            if username is None:
                return None
            
            # 直接从数据库获取用户，预加载关系，避免返回分离对象
            from app.extensions import get_db_redis_direct
            db, redis, close_db_func = get_db_redis_direct()
            
            # 导入所需的模型类和函数
            from app.models.user.user import User
            from app.models.user.role import Role
            from sqlalchemy.orm import joinedload
            
            # 预加载用户关系
            user = db.query(User).options(
                joinedload(User.permissions),
                joinedload(User.roles).joinedload(Role.permissions)
            ).filter(User.username == username, User.is_active == True).first()
            
            # 关闭数据库会话
            if close_db_func:
                close_db_func()
            
            if not user:
                return None
            
            # 获取令牌类型（从令牌的过期时间判断）
            exp = payload.get("exp")
            if not exp:
                return None
            
            # 判断是访问令牌还是刷新令牌
            from datetime import datetime
            current_time = datetime.utcnow().timestamp()
            exp_time = datetime.fromtimestamp(exp).timestamp()
            
            # 计算令牌有效期
            token_ttl = exp_time - current_time
            
            # 访问令牌有效期较短（15分钟），刷新令牌有效期较长（7天）
            if token_ttl < 24 * 60 * 60:  # 小于1天，认为是访问令牌
                # 检查访问令牌是否为最新
                if redis_client:
                    from app.utils.redis_utils import RedisUtils
                    cached_access_token = RedisUtils.get_cache(redis_client, f"user:access_token:{user.id}")
                    if cached_access_token and cached_access_token != token:
                        return None
            # 对于刷新令牌，不需要检查是否为最新
            
            return user
        except JWTError:
            return None
        except Exception as e:
            print(f"从令牌获取用户失败: {e}")
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict:
        """
        验证用户身份
        :param username: 用户名
        :param password: 密码
        :return: 包含验证结果的字典
        """
        from werkzeug.security import check_password_hash
        from datetime import datetime
        
        # 用于保存需要关闭的数据库会话
        close_db_func = None
        try:
            from app.extensions import get_db_redis_direct
            # 获取数据库会话和Redis客户端
            db, redis, close_db_func = get_db_redis_direct()
            
            # 直接从数据库获取用户，避免使用UserService.get_user_by_username创建新会话
            # 同时预加载permissions和roles关系，包括角色的permissions，避免DetachedInstanceError
            from app.models.user.user import User
            from app.models.user.role import Role
            from sqlalchemy.orm import joinedload
            user = db.query(User).options(
                joinedload(User.permissions),
                joinedload(User.roles).joinedload(Role.permissions)
            ).filter(User.username == username).first()
            
            # 验证用户是否存在
            if not user:
                return {
                    "success": False,
                    "message": "用户名或密码错误",
                    "user": None
                }
            
            # 验证用户是否被禁用
            if not user.is_active:
                return {
                    "success": False,
                    "message": "账号已被禁用",
                    "user": None
                }
            
            # 验证密码
            if not check_password_hash(user.password, password):
                return {
                    "success": False,
                    "message": "用户名或密码错误",
                    "user": None
                }
            
            # 验证成功，更新最后登录时间
            try:
                user.last_login_at = datetime.utcnow()
                db.commit()
                db.refresh(user)
                
                # 清除缓存，确保缓存数据最新
                if redis:
                    from app.dal.user_dal import UserDAL
                    user_dal = UserDAL(db, redis)
                    user_dal.invalidate_cache(user.id, user.username)
            except Exception as e:
                # 更新最后登录时间失败不影响用户登录
                if 'db' in locals():
                    db.rollback()
            
            # 获取用户角色和权限信息，直接在会话内完成
            user_roles = []
            user_permissions = set()
            
            # 获取直接分配的权限
            for perm in user.permissions:
                user_permissions.add(perm.code)
            
            # 获取通过角色继承的权限
            for role in user.roles:
                user_roles.append(role.name)
                for perm in role.permissions:
                    user_permissions.add(perm.code)
            
            # 组装用户信息
            user_info = {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "roles": user_roles,
                "permissions": list(user_permissions)
            }
            
            return {
                "success": True,
                "message": "登录成功",
                "user_id": user.id,
                "username": user.username,
                "user_info": user_info
            }
        except Exception as e:
            # 捕获所有异常，确保返回合适的响应
            print(f"验证用户身份失败: {e}")
            return {
                "success": False,
                "message": "登录失败，请稍后重试",
                "user": None
            }
        finally:
            # 如果是自己创建的会话，关闭它
            if close_db_func:
                close_db_func()
    
    @staticmethod
    def get_user_with_permissions(user) -> dict:
        """
        获取包含角色和权限信息的用户数据
        :param user: 用户对象
        :return: 包含完整信息的用户字典
        """
        # 初始化返回值
        user_info = {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "roles": [],
            "permissions": []
        }
        
        # 直接从数据库重新获取用户，确保所有关系都已加载
        db, redis, close_db_func = None, None, None
        try:
            from app.extensions import get_db_redis_direct
            db, redis, close_db_func = get_db_redis_direct()
            
            # 导入所有需要的模型和函数
            from app.models.user.user import User as UserModel
            from app.models.user.role import Role as RoleModel
            from sqlalchemy.orm import joinedload
            
            # 重新查询用户，预加载所有关系
            db_user = db.query(UserModel).options(
                joinedload(UserModel.permissions),
                joinedload(UserModel.roles).joinedload(RoleModel.permissions)
            ).filter(UserModel.id == user.id).first()
            
            if db_user:
                # 提取角色和权限信息
                roles = []
                permissions = set()
                
                # 获取直接分配的权限
                for perm in db_user.permissions:
                    permissions.add(perm.code)
                
                # 获取角色及其权限
                for role in db_user.roles:
                    roles.append(role.name)
                    for perm in role.permissions:
                        permissions.add(perm.code)
                
                # 更新返回信息
                user_info["roles"] = roles
                user_info["permissions"] = list(permissions)
        except Exception as e:
            print(f"获取用户权限信息失败: {e}")
        finally:
            # 确保关闭数据库会话
            if close_db_func:
                close_db_func()
        
        return user_info
