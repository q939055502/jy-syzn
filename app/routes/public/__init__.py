from fastapi import APIRouter

# 创建公开路由实例
router = APIRouter(prefix="/api/public", tags=["public"])

# 导入子路由
from .files import router as files_router
from .detection import router as detection_router

# 注册子路由
router.include_router(files_router)
router.include_router(detection_router)

# 导出路由
__all__ = ["router"]
