# 用户相关模型导出文件
# 将所有用户相关的模型统一导出，方便其他模块导入使用

from app.models.user.user import User
from app.models.user.role import Role
from app.models.user.permission import Permission
from app.models.user.api_permission import ApiPermission
from app.models.associations import user_roles, role_permissions

__all__ = [
    'User',          # 用户模型
    'Role',          # 角色模型
    'Permission',    # 权限模型
    'ApiPermission', # 接口权限绑定模型
    'user_roles',    # 用户角色关联表
    'role_permissions' # 角色权限关联表
]