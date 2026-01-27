# 通用认证依赖
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth.auth_service import AuthService


# OAuth2 密码流配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    获取当前用户，验证token有效性
    
    :param token: 访问令牌
    :return: 当前用户对象
    :raises HTTPException: 如果令牌无效或过期
    """
    user = AuthService.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(current_user = Depends(get_current_user)):
    """
    获取当前活跃用户
    
    :param current_user: 当前用户对象
    :return: 当前用户对象
    """
    return current_user
