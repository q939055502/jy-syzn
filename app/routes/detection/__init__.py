from fastapi import APIRouter, Depends
from app.routes.dependencies import get_current_active_user

# 创建主路由实例，添加认证依赖
router = APIRouter(
    prefix="/api/detection", 
    tags=["detection"],
    dependencies=[Depends(get_current_active_user)]  # 全局认证依赖，所有检测接口需要登录
)

# 导入子路由
from .categories import router as categories_router
from .standards import router as standards_router
from .detection_items import router as detection_items_router
from .detection_objects import router as detection_objects_router
from .params import router as params_router
from .templates import router as templates_router

# 注册子路由
router.include_router(categories_router)
router.include_router(standards_router)
router.include_router(detection_objects_router)
router.include_router(detection_items_router)
router.include_router(params_router)
router.include_router(templates_router)
