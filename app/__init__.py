# -*- coding: utf-8 -*-
"""
应用包初始化文件
"""

import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导出模型，方便其他模块导入
from .models import Category, DetectionStandard, DetectionItem, DetectionParam, User
from .models.user.role import Role
from .models.user.permission import Permission

# 导出扩展和依赖
from .extensions import init_db, get_db, get_redis, get_db_and_redis, engine, Base, SessionLocal

# 导出路由
from .routes.detection import router as detection_router
from .routes.auth import router as auth_router

# 导出依赖
from .dependencies import get_current_user, get_current_admin

__all__ = [
    # 模型
    'Category',
    'DetectionStandard',
    'DetectionItem',
    'DetectionParam',
    'User',
    'Role',
    'Permission',
    
    # 扩展和依赖
    'init_db',
    'get_db',
    'get_redis',
    'get_db_and_redis',
    'engine',
    'Base',
    'SessionLocal',
    
    # 路由
    'detection_router',
    'auth_router',
    
    # 依赖
    'get_current_user',
    'get_current_admin'
]

