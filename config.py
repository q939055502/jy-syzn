# 配置文件
# 包含不同环境的配置类，支持开发、测试和生产环境

import os


class BaseConfig:
    """基础配置类，包含所有环境共享的配置"""
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_hard_to_guess_string'
    APP_NAME = 'Flask Project'
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES') or 15)
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get('REFRESH_TOKEN_EXPIRE_DAYS') or 7)
    
    # Redis Session配置
    SESSION_EXPIRE_SECONDS = int(os.environ.get('SESSION_EXPIRE_SECONDS') or 1800)
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # 其他基础配置
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG = True
    
    # 开发环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123@127.0.0.1:3306/jy_syzn?charset=utf8mb4'
    
    # 开发环境日志级别
    LOG_LEVEL = 'DEBUG'


class TestingConfig(BaseConfig):
    """测试环境配置"""
    TESTING = True
    
    # 测试环境数据库配置（内存数据库）
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or 'sqlite:///:memory:'
    
    # 测试环境不需要CSRF保护
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    # 生产环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    
    # 生产环境日志级别
    LOG_LEVEL = 'WARNING'


# 配置字典，用于根据环境变量选择对应的配置类
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
