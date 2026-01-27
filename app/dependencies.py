# 依赖注入函数
# 包含获取当前用户、当前活跃用户和当前管理员用户的依赖函数

from fastapi import Depends, HTTPException, status
from app.routes.auth import oauth2_scheme
from app.services.auth.auth_service import AuthService
from app.models.user.user import User


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前用户
    
    :param token: OAuth2 访问令牌
    :return: 用户对象
    """
    # 从令牌中获取用户
    user = AuthService.get_user_from_token(token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户
    
    :param current_user: 当前用户
    :return: 活跃用户对象
    """
    # 检查用户是否活跃
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    return current_user


async def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    获取当前管理员用户
    
    :param current_user: 当前活跃用户
    :return: 管理员用户对象
    """
    # 检查用户是否为管理员
    # 假设用户模型有role字段，管理员角色值为'admin'
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    
    return current_user


def get_current_user_with_permission(permission_code: str):
    """
    获取具有特定权限的当前用户
    
    :param permission_code: 权限代码
    :return: 依赖函数
    
    Raises:
        HTTPException: 如果用户没有该权限
    """
    async def dependency(current_user: User = Depends(get_current_active_user)):
        # 检查用户是否有特定权限
        # 假设用户模型有has_permission方法
        if not hasattr(current_user, 'has_permission') or not current_user.has_permission(permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要 {permission_code} 权限"
            )
        return current_user
    return dependency
