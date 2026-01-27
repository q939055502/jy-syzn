from fastapi import APIRouter


# 延迟导入，避免循环依赖
def register_admin_routes():
    """注册所有admin路由"""
    router = APIRouter(prefix="/api/admin", tags=["管理员操作"])
    
    # 动态导入路由模块
    from .users import router as users_router
    from .roles import router as roles_router
    from .permissions import router as permissions_router
    
    # 注册路由
    router.include_router(users_router)
    router.include_router(roles_router)
    router.include_router(permissions_router)
    
    return router


# 导出路由注册函数
__all__ = ["register_admin_routes"]
