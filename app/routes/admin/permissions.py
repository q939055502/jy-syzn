from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user.user import User
from app.schemas.detection import ResponseModel
from app.schemas.admin import PermissionCreate, PermissionUpdate, PermissionResponse
from app.extensions import get_db_and_redis
from app.services.admin import PermissionAdminService
from .dependencies import get_current_admin


router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.post("", response_model=ResponseModel, summary="创建权限")
def create_permission(
    permission: PermissionCreate,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    创建权限（仅管理员）
    
    - **code**: 权限代码（唯一）
    - **resource**: 资源名称
    - **action**: 操作类型
    - **scope**: 权限范围（默认：all）
    - **description**: 权限描述
    """
    db, redis = db_and_redis
    permission_obj = PermissionAdminService.create_permission(
        db=db,
        **permission.model_dump()
    )
    return ResponseModel(data=permission_obj, message="权限创建成功")


@router.get("", response_model=ResponseModel, summary="获取权限列表")
def get_permissions(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    获取权限列表（仅管理员）
    
    - **skip**: 跳过的记录数（默认：0）
    - **limit**: 返回的最大记录数（默认：100）
    - **is_active**: 权限状态过滤（可选）
    """
    db, redis = db_and_redis
    permissions = PermissionAdminService.get_permissions(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    return ResponseModel(data=permissions, message="获取权限列表成功")


@router.get("/{permission_id}", response_model=ResponseModel, summary="获取权限详情")
def get_permission(
    permission_id: int,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    获取权限详情（仅管理员）
    
    - **permission_id**: 权限ID
    """
    db, redis = db_and_redis
    permission = PermissionAdminService.get_permission_by_id(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return ResponseModel(data=permission, message="获取权限详情成功")


@router.put("/{permission_id}", response_model=ResponseModel, summary="更新权限")
def update_permission(
    permission_id: int,
    permission: PermissionUpdate,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    更新权限（仅管理员）
    
    - **permission_id**: 权限ID
    - **code**: 权限代码
    - **resource**: 资源名称
    - **action**: 操作类型
    - **scope**: 权限范围
    - **is_active**: 是否激活
    - **description**: 权限描述
    """
    db, redis = db_and_redis
    permission_obj = PermissionAdminService.update_permission(
        db=db,
        permission_id=permission_id,
        **permission.model_dump(exclude_unset=True)
    )
    if not permission_obj:
        raise HTTPException(status_code=404, detail="权限不存在")
    return ResponseModel(data=permission_obj, message="权限更新成功")


@router.delete("/{permission_id}", response_model=ResponseModel, summary="删除权限", status_code=200)
def delete_permission(
    permission_id: int,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    删除权限（仅管理员）
    
    - **permission_id**: 权限ID
    """
    db, redis = db_and_redis
    success = PermissionAdminService.delete_permission(db=db, permission_id=permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="权限不存在")
    return ResponseModel(message="权限删除成功")


@router.patch("/{permission_id}/toggle-active", response_model=ResponseModel, summary="切换权限激活状态")
def toggle_permission_active(
    permission_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    切换权限激活状态（仅管理员）
    
    - **permission_id**: 权限ID
    - **is_active**: 激活状态
    """
    db, redis = db_and_redis
    permission = PermissionAdminService.toggle_permission_active(
        db=db,
        permission_id=permission_id,
        is_active=is_active
    )
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return ResponseModel(data=permission, message="权限状态更新成功")
