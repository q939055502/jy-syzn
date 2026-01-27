# -*- coding: utf-8 -*-
"""
重置数据库表结构
用于删除现有表并重新创建，以应用新的模型定义
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.extensions import init_db, Base, engine
from config import config
from app.models import *

# 加载配置
config_name = os.environ.get('FASTAPI_CONFIG') or 'default'
app_config = config[config_name]

print(f"配置环境: {config_name}")
print(f"数据库连接: {app_config.SQLALCHEMY_DATABASE_URI}")

# 初始化数据库
engine, SessionLocal = init_db(app_config)

print("\n开始重置数据库...")

# 显式导入所有模型类，确保所有表都能被正确创建
from app.models.user import user, role, permission, resource, action, scope
from app.models.detection import Category, DetectionStandard, DetectionItem, DetectionGuide, DelegationFormTemplate, DetectionParam

# 删除所有表
print("1. 删除所有现有表...")

# 禁用外键约束
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    conn.commit()

# 删除所有表
Base.metadata.drop_all(bind=engine)

# 启用外键约束
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()

print("所有表删除成功!")

# 重新创建所有表
print("2. 重新创建所有表...")
Base.metadata.create_all(bind=engine)
print("所有表创建成功!")

print("\n数据库重置完成!")