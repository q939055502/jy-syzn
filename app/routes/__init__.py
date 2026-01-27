# API路由包

# 导出路由
from app.routes.detection import router as detection_router
from app.routes.auth import router as auth_router
from app.routes.public import router as public_router

__all__ = [
    'detection_router',
    'auth_router',
    'public_router'
]
