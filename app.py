# 应用主入口文件
# 创建FastAPI应用实例，加载配置，初始化扩展，并注册路由

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 导入配置
from config import config

# 导入扩展
from app.extensions import init_db, Base, engine

# 导入路由
from app.routes.detection import router as detection_router
from app.routes.auth import router as auth_router
from app.routes.admin import register_admin_routes
from app.routes.public import router as public_router
from app.routes.image import router as image_router

# 加载配置
config_name = os.environ.get('FASTAPI_CONFIG') or 'default'
app_config = config[config_name]

# 添加调试输出
print(f"Configuration name: {config_name}")
print(f"Database URI: {app_config.SQLALCHEMY_DATABASE_URI}")

# 创建FastAPI应用实例
app = FastAPI(
    title="检测标准管理系统",
    description="一个用于管理检测标准的Web应用",
    version="1.0.0"
)

# 添加CORS中间件
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法，包括OPTIONS
    allow_headers=["*"],  # 允许所有请求头
)

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 初始化扩展
print("Initializing database...")
engine, SessionLocal = init_db(app_config)
print(f"Engine created: {engine}")
print(f"SessionLocal created: {SessionLocal}")

# 创建所有表（如果不存在）
if engine is not None:
    print("Creating database tables...")
    # 重新创建所有表（如果不存在）
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
else:
    raise RuntimeError("Database engine not initialized properly")

# 初始化Redis（可选）
try:
    from app.extensions import init_redis
    redis_client = init_redis(app_config)
except Exception as e:
    print(f"Redis初始化失败，将继续运行应用: {str(e)}")
    redis_client = None

# 导入并配置日志
from app.core.logging_config import setup_logging, uvicorn_log_config
setup_logging()

# 注册路由
app.include_router(detection_router)
app.include_router(auth_router)
app.include_router(register_admin_routes())
app.include_router(public_router)
app.include_router(image_router)

# 定义基础路由
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": app_config.APP_NAME})

# 健康检查路由
@app.get("/health")
def health_check():
    return {"status": "ok", "app_name": app_config.APP_NAME, "version": "1.0.0"}

# API路由示例
@app.get("/api/health")
async def api_health_check():
    """
    健康检查接口
    :return: 健康状态信息
    """
    return {"status": "healthy", "app_name": app_config.APP_NAME}

# 如果直接运行该文件，启动应用
if __name__ == '__main__':
    import uvicorn
    # 获取端口配置，默认1314
    port = int(os.environ.get('PORT', 1314))
    # 使用logging_config.py中定义的日志配置
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_config=uvicorn_log_config
    )
