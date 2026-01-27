# 扩展初始化文件
# 定义并初始化所有FastAPI扩展

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_migrate import Migrate
import redis
from typing import Generator


# 创建模型基类
Base = declarative_base()

# 创建扩展实例
migrate = Migrate()

# 数据库连接对象
engine = None
SessionLocal = None

# Redis连接对象
redis_client = None
redis_pool = None

# 初始化数据库函数

def init_db(app_config):
    """初始化数据库连接和会话工厂"""
    global engine, SessionLocal
    # 从app配置中获取数据库URL
    database_url = app_config.SQLALCHEMY_DATABASE_URI
    print(f"Creating engine with URL: {database_url}")
    
    # 处理MySQL数据库不存在的情况
    if database_url.startswith('mysql'):
        try:
            # 解析数据库URL获取连接参数
            from sqlalchemy.engine.url import make_url
            url = make_url(database_url)
            
            # 提取数据库名
            db_name = url.database
            
            # 创建不带数据库名的连接URL
            no_db_url = url.set(database='mysql')
            
            print(f"Checking if database '{db_name}' exists...")
            
            # 创建临时引擎连接到MySQL服务器
            temp_engine = create_engine(
                no_db_url,
                pool_pre_ping=True,
                pool_size=1,
                max_overflow=0
            )
            
            # 连接到MySQL服务器并检查数据库是否存在
            with temp_engine.connect() as conn:
                # 导入text函数用于执行原始SQL
                from sqlalchemy import text
                
                # 检查数据库是否存在
                result = conn.execute(
                    text(f"SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'")
                )
                db_exists = result.scalar() is not None
                
                if not db_exists:
                    print(f"Database '{db_name}' does not exist, creating it...")
                    # 创建数据库
                    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    print(f"Database '{db_name}' created successfully!")
                else:
                    print(f"Database '{db_name}' already exists.")
            
            # 关闭临时引擎
            temp_engine.dispose()
            
        except Exception as e:
            print(f"Warning: Failed to check/create database: {str(e)}")
            print("Continuing with regular engine creation...")
    
    # 增加数据库连接池大小，缓解连接池耗尽问题
    engine = create_engine(
        database_url,
        pool_size=20,  # 连接池默认大小，默认5
        max_overflow=40,  # 连接池允许的最大溢出连接数，默认10
        pool_timeout=30,  # 获取连接的超时时间，默认30秒
        pool_recycle=3600  # 连接的回收时间，默认为-1（不回收）
    )
    print(f"Engine created: {engine}")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"SessionLocal created: {SessionLocal}")
    return engine, SessionLocal

# 获取数据库会话的依赖函数
def get_db():
    """获取数据库会话的依赖函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化Redis函数
def init_redis(app_config):
    """初始化Redis连接和连接池"""
    global redis_client, redis_pool
    
    try:
        # 优先使用REDIS_URL配置
        if hasattr(app_config, 'REDIS_URL') and app_config.REDIS_URL:
            print(f"Initializing Redis with URL: {app_config.REDIS_URL}")
            # 创建Redis连接池
            redis_pool = redis.ConnectionPool.from_url(
                app_config.REDIS_URL,
                decode_responses=True  # 自动将bytes解码为字符串
            )
        else:
            # 使用单独的配置项
            print(f"Initializing Redis with host: {app_config.REDIS_HOST}, port: {app_config.REDIS_PORT}, db: {app_config.REDIS_DB}")
            # 创建Redis连接池
            redis_pool = redis.ConnectionPool(
                host=app_config.REDIS_HOST,
                port=app_config.REDIS_PORT,
                db=app_config.REDIS_DB,
                password=app_config.REDIS_PASSWORD,
                decode_responses=True  # 自动将bytes解码为字符串
            )
        
        # 创建Redis客户端
        redis_client = redis.Redis(connection_pool=redis_pool)
        
        # 测试连接
        redis_client.ping()
        print("Redis connection established successfully!")
        
        return redis_client
    except Exception as e:
        print(f"Failed to initialize Redis: {str(e)}")
        raise

# 获取Redis客户端的依赖函数
def get_redis() -> Generator[redis.Redis, None, None]:
    """获取Redis客户端的依赖函数"""
    try:
        if not redis_client:
            raise RuntimeError("Redis client not initialized. Call init_redis() first.")
        yield redis_client
    finally:
        # Redis客户端使用连接池，不需要手动关闭
        pass

# 获取数据库和Redis的组合依赖函数
def get_db_and_redis() -> Generator[tuple, None, None]:
    """
    获取数据库会话和Redis客户端的组合依赖函数
    
    支持两种使用方式：
    1. 作为FastAPI依赖注入：yield的finally块会自动执行，关闭数据库会话
    2. 直接调用next()：返回(db, redis)元组，需要手动关闭数据库会话
    """
    db = None
    try:
        # 获取数据库会话
        db = SessionLocal()
        
        # 获取Redis客户端
        if not redis_client:
            raise RuntimeError("Redis client not initialized. Call init_redis() first.")
        
        yield db, redis_client
    finally:
        # 关闭数据库会话
        if db:
            db.close()
        # Redis客户端使用连接池，不需要手动关闭
        pass

# 直接获取数据库和Redis的辅助函数
def get_db_redis_direct() -> tuple:
    """
    直接获取数据库会话和Redis客户端的辅助函数
    
    返回值：
    - db: 数据库会话
    - redis_client: Redis客户端，如果未初始化则返回None
    - close_func: 关闭资源的函数，调用后会关闭数据库会话
    """
    # 创建新的数据库会话
    db = SessionLocal()
    
    def close_func():
        """关闭数据库会话"""
        try:
            db.close()
        except Exception:
            pass
    
    # 获取Redis客户端，如果未初始化则返回None
    redis_instance = redis_client if redis_client else None
    
    return db, redis_instance, close_func
