from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.user.user import User
from app.schemas.detection import ResponseModel
from app.schemas.admin import UserCreate, UserUpdate, UserResponse
from app.extensions import get_db_and_redis
from app.services.admin import UserAdminService
from .dependencies import get_current_admin


router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("", response_model=ResponseModel, summary="创建新用户")
def create_user(
    user: UserCreate,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    创建新用户（仅管理员）
    
    - **username**: 用户名（唯一）
    - **password**: 密码
    - **name**: 真实姓名
    """
    db, redis = db_and_redis
    user_obj = UserAdminService.create_user(
        name=user.name,
        username=user.username,
        password=user.password
    )
    return ResponseModel(data=user_obj, message="用户创建成功")


@router.get("", response_model=ResponseModel, summary="获取用户列表")
def get_users(
    page: int = 1,
    limit: int = 10,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    获取用户列表（仅管理员）
    
    - **page**: 页码（默认1）
    - **limit**: 每页数量（默认10）
    """
    db, redis = db_and_redis
    users, total = UserAdminService.get_users(db=db, redis=redis, page=page, limit=limit)
    return ResponseModel(data=users, message="获取用户列表成功", total=total)


@router.get("/check-username", summary="检查用户名是否存在")
def check_username(
    username: str = Query(..., description="要检查的用户名"),
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    检查用户名是否已存在（仅管理员）
    
    - **username**: 要检查的用户名
    """
    db, redis = db_and_redis
    from app.dal.user_dal import UserDAL
    user_dal = UserDAL(db, redis)
    user = user_dal.get_by_username(username)
    return ResponseModel(
        data={"exists": user is not None},
        message="用户名检查成功"
    )


@router.get("/{user_id}", response_model=ResponseModel, summary="获取用户详情")
def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    获取用户详情（仅管理员）
    
    - **user_id**: 用户ID
    """
    db, redis = db_and_redis
    user = UserAdminService.get_user(db=db, redis=redis, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ResponseModel(data=user, message="获取用户详情成功")


@router.put("/{user_id}", response_model=ResponseModel, summary="更新用户信息")
def update_user(
    user_id: int,
    user: UserUpdate,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    更新用户信息（仅管理员）
    
    - **user_id**: 用户ID
    - **name**: 真实姓名
    - **password**: 密码（可选）
    """
    db, redis = db_and_redis
    user_obj = UserAdminService.update_user(
        user_id=user_id, **user.model_dump(exclude_unset=True)
    )
    return ResponseModel(data=user_obj, message="用户更新成功")


@router.delete("/{user_id}", response_model=ResponseModel, summary="删除用户", status_code=200)
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    删除用户（仅管理员）
    
    - **user_id**: 用户ID
    """
    db, redis = db_and_redis
    UserAdminService.delete_user(user_id=user_id)
    return ResponseModel(message="用户删除成功")


@router.patch("/{user_id}/toggle-active", response_model=ResponseModel, summary="切换用户激活状态")
def toggle_user_active(
    user_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin),
    db_and_redis: tuple = Depends(get_db_and_redis)
):
    """
    切换用户激活状态（仅管理员）
    
    - **user_id**: 用户ID
    - **is_active**: 激活状态
    """
    db, redis = db_and_redis
    user = UserAdminService.toggle_user_active(user_id=user_id, is_active=is_active)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ResponseModel(data=user, message="用户状态更新成功")
