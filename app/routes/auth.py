# 认证相关路由
# 包含登录、刷新令牌、注销等功能

from fastapi import APIRouter, Depends, HTTPException, status, Response, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from app.services.auth.auth_service import AuthService
from app.models.user.user import User
from app.schemas.detection import ResponseModel


router = APIRouter(prefix="/api/auth", tags=["认证"])

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# 令牌数据模型
class TokenData(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    user: dict

# 访问令牌数据模型
class AccessTokenData(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


# 添加登录请求模型
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


@router.post("/token", response_model=ResponseModel[TokenData], summary="获取访问令牌")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = Response()
):
    """
    获取访问令牌和刷新令牌
    
    - **username**: 用户名
    - **password**: 密码
    
    返回:
    - **access_token**: 访问令牌，用于访问受保护的API
    - **token_type**: 令牌类型，固定为"bearer"
    - **refresh_token**: 刷新令牌，用于获取新的访问令牌
    - **user**: 用户信息
    """
    # 使用新的认证方法
    from app.services.auth.auth_service import AuthService
    auth_result = AuthService.authenticate_user(form_data.username, form_data.password)
    
    # 根据认证结果返回不同的错误信息
    if not auth_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=auth_result["message"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证成功，获取用户ID和用户名
    user_id = auth_result["user_id"]
    username = auth_result["username"]
    
    # 生成访问令牌
    access_token = AuthService.create_access_token(data={"sub": username})
    
    # 生成刷新令牌
    refresh_token = AuthService.create_refresh_token(data={"sub": username})
    
    # 使用认证服务返回的预获取用户信息
    user_info = auth_result["user_info"]
    
    # 缓存用户信息和令牌到Redis
    AuthService.cache_user_info(user_id, user_info)
    _, is_other_device_login = AuthService.cache_tokens(user_id, access_token, refresh_token)
    
    # 准备响应数据
    token_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "user": user_info
    }
    
    # 根据是否有其他设备登录返回不同的消息
    message = "登录成功，您的账号已在其他设备登录" if is_other_device_login else "登录成功"
    
    # 返回令牌和用户信息
    return {"data": token_data, "message": message}


# 刷新令牌请求模型
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")

@router.post("/refresh", response_model=ResponseModel[AccessTokenData], summary="刷新访问令牌")
def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    response: Response = Response()
):
    """
    使用刷新令牌获取新的访问令牌和刷新令牌
    
    - **refresh_token**: 刷新令牌
    
    返回:
    - **access_token**: 新的访问令牌
    - **token_type**: 令牌类型，固定为"bearer"
    - **refresh_token**: 新的刷新令牌
    """
    # 从刷新令牌中获取用户
    refresh_token = refresh_request.refresh_token
    user = AuthService.get_user_from_token(refresh_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成新的访问令牌
    access_token = AuthService.create_access_token(data={"sub": user.username})
    
    # 生成新的刷新令牌
    new_refresh_token = AuthService.create_refresh_token(data={"sub": user.username})
    
    # 将旧的刷新令牌添加到黑名单
    AuthService.add_token_to_blacklist(refresh_token)
    
    # 更新Redis中的令牌缓存
    AuthService.cache_tokens(user.id, access_token, new_refresh_token)
    
    # 准备响应数据
    access_token_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }
    
    return {"data": access_token_data, "message": "令牌刷新成功"}


@router.post("/logout", response_model=ResponseModel, summary="注销登录")
def logout(
    token: str = Depends(oauth2_scheme),
    response: Response = Response()
):
    """
    注销登录
    
    - **Authorization**: 访问令牌，格式为 Bearer {token}
    
    注销后，令牌将被添加到黑名单，无法再用于访问API
    """
    # 从令牌中获取用户
    user = AuthService.get_user_from_token(token)
    
    if user:
        # 清除Redis中的用户令牌缓存
        from app.extensions import get_redis
        from app.utils.redis_utils import RedisUtils
        redis = next(get_redis())
        
        # 获取用户的刷新令牌
        refresh_token = RedisUtils.get_cache(redis, f"user:refresh_token:{user.id}")
        
        # 将访问令牌添加到黑名单
        AuthService.add_token_to_blacklist(token)
        
        # 将刷新令牌添加到黑名单
        if refresh_token:
            AuthService.add_token_to_blacklist(refresh_token)
        
        # 清除访问令牌和刷新令牌缓存
        RedisUtils.delete_cache(redis, f"user:access_token:{user.id}")
        RedisUtils.delete_cache(redis, f"user:refresh_token:{user.id}")
    else:
        # 如果无法获取用户，至少将当前访问令牌添加到黑名单
        AuthService.add_token_to_blacklist(token)
    
    return {"message": "注销成功"}


@router.get("/me", response_model=ResponseModel, summary="获取当前用户信息")
def get_current_user_info(
    token: str = Depends(oauth2_scheme)
):
    """
    获取当前用户信息
    
    - **Authorization**: 访问令牌，格式为 Bearer {token}
    """
    # 从令牌中获取用户
    user = AuthService.get_user_from_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取包含角色和权限信息的用户数据
    user_info = AuthService.get_user_with_permissions(user)
    
    return {"data": user_info, "message": "获取用户信息成功"}
