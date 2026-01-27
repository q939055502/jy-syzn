from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user.user import User
from app.schemas.detection import ResponseModel
from app.schemas.admin import RoleCreate, RoleUpdate, RoleResponse
from app.extensions import get_db_and_redis
from app.services.admin import RoleAdminService
from .dependencies import get_current_admin


router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("", response_model=ResponseModel, summary="创建角色")
def create_role(
    role: RoleCreate,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    创建角色（仅管理员）
    
    - **role_name**: 角色名称（唯一）
    - **permissions**: 权限列表
    """
    db, redis = db_and_redis
    
    # 处理角色数据
    role_data = {
        "name": role.role_name,
        "description": getattr(role, "description", None),
        "parent_id": getattr(role, "parent_id", None)
    }
    
    # 创建角色
    role_obj = RoleAdminService.create_role(db=db, **role_data)
    
    # 关联权限
    if role_obj and hasattr(role, "permissions") and role.permissions:
        from app.services.user.permission_service import PermissionService
        PermissionService.assign_permissions_to_role(
            db=db,
            role_id=role_obj.id,
            permission_codes=role.permissions
        )
        # 刷新角色对象，获取最新权限
        db.refresh(role_obj)
    
    # 转换为响应格式
    role_response = {
        "role_id": role_obj.id,
        "role_name": role_obj.name,
        "description": role_obj.description,
        "parent_id": role_obj.parent_id,
        "permissions": role.permissions,
        "created_at": role_obj.created_at,
        "updated_at": role_obj.updated_at
    }
    
    return ResponseModel(data=role_response, message="角色创建成功")


@router.get("", response_model=ResponseModel, summary="获取角色列表")
def get_roles(
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    获取角色列表（仅管理员）
    """
    db, redis = db_and_redis
    roles = RoleAdminService.get_roles(db=db)
    
    # 转换为API文档要求的格式
    roles_response = []
    for role in roles:
        role_dict = {
            "role_id": role.id,
            "role_name": role.name,
            "description": role.description,
            "parent_id": role.parent_id,
            "permissions": [permission.code for permission in role.permissions],
            "created_at": role.created_at,
            "updated_at": role.updated_at
        }
        roles_response.append(role_dict)
    
    return ResponseModel(data=roles_response, message="获取角色列表成功")


@router.put("/{role_id}", response_model=ResponseModel, summary="更新角色")
def update_role(
    role_id: int,
    role: RoleUpdate,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    更新角色（仅管理员）
    
    - **role_id**: 角色ID
    - **role_name**: 角色名称
    - **permissions**: 权限列表
    """
    db, redis = db_and_redis
    
    # 处理角色数据，排除permissions字段，单独处理
    role_data = role.model_dump(exclude_unset=True)
    permissions = role_data.pop("permissions", None)
    
    # 更新角色基本信息
    role_obj = RoleAdminService.update_role(db=db, role_id=role_id, **role_data)
    
    # 更新权限关联
    if role_obj and permissions is not None:
        from app.services.user.permission_service import PermissionService
        # 先清除现有权限关联
        PermissionService.remove_all_permissions_from_role(db=db, role_id=role_id)
        # 添加新的权限关联
        if permissions:
            PermissionService.assign_permissions_to_role(
                db=db,
                role_id=role_id,
                permission_codes=permissions
            )
        # 刷新角色对象，获取最新权限
        db.refresh(role_obj)
    
    # 转换为响应格式
    role_response = {
        "role_id": role_obj.id,
        "role_name": role_obj.name,
        "description": role_obj.description,
        "parent_id": role_obj.parent_id,
        "permissions": permissions or [permission.code for permission in role_obj.permissions],
        "created_at": role_obj.created_at,
        "updated_at": role_obj.updated_at
    }
    
    return ResponseModel(data=role_response, message="角色更新成功")


@router.delete("/{role_id}", response_model=ResponseModel, summary="删除角色", status_code=200)
def delete_role(
    role_id: int,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    删除角色（仅管理员）
    
    - **role_id**: 角色ID
    """
    db, redis = db_and_redis
    RoleAdminService.delete_role(db=db, role_id=role_id)
    return ResponseModel(message="角色删除成功")
