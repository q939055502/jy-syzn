# 日志配置模块
# 集中管理应用程序的日志配置，包括文件保存、日志轮转等

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from config import config

# 获取当前环境配置
env_config = config[os.environ.get('FASTAPI_CONFIG') or 'default']

# 日志目录配置
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件路径
APP_LOG_FILE = os.path.join(LOG_DIR, 'app.log')
ACCESS_LOG_FILE = os.path.join(LOG_DIR, 'access.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'error.log')


class UvicornAccessFormatter(logging.Formatter):
    """自定义Uvicorn访问日志格式"""
    default_fmt = '%(asctime)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s'
    
    def format(self, record):
        # 确保记录包含必要的属性
        if not hasattr(record, 'client_addr'):
            record.client_addr = '-'  # 默认值
        if not hasattr(record, 'request_line'):
            record.request_line = '-'  # 默认值
        if not hasattr(record, 'status_code'):
            record.status_code = '-'  # 默认值
        
        return super().format(record)


def setup_logging():
    """
    设置应用程序的日志配置
    包括：
    1. 控制台日志输出
    2. 文件日志保存
    3. 日志轮转配置
    4. 不同级别的日志分离
    """
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    
    # 清除现有的处理器，避免重复配置
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 设置根日志级别
    root_logger.setLevel(getattr(logging, env_config.LOG_LEVEL))
    
    # 1. 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, env_config.LOG_LEVEL))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 2. 应用日志文件处理器 (按大小轮转)
    app_file_handler = RotatingFileHandler(
        APP_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # 保留5个备份文件
        encoding='utf-8'
    )
    app_file_handler.setLevel(getattr(logging, env_config.LOG_LEVEL))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    app_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(app_file_handler)
    
    # 3. 错误日志文件处理器 (按大小轮转，只记录错误)
    error_file_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # 保留5个备份文件
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_file_handler)
    
    # 4. 配置Uvicorn日志处理器
    # 移除Uvicorn默认处理器
    uvicorn_logger = logging.getLogger('uvicorn')
    for handler in uvicorn_logger.handlers[:]:
        uvicorn_logger.removeHandler(handler)
    
    uvicorn_error_logger = logging.getLogger('uvicorn.error')
    for handler in uvicorn_error_logger.handlers[:]:
        uvicorn_error_logger.removeHandler(handler)
    
    uvicorn_access_logger = logging.getLogger('uvicorn.access')
    for handler in uvicorn_access_logger.handlers[:]:
        uvicorn_access_logger.removeHandler(handler)
    
    # 为Uvicorn添加自定义处理器
    uvicorn_logger.addHandler(console_handler)
    uvicorn_logger.addHandler(app_file_handler)
    uvicorn_logger.addHandler(error_file_handler)
    
    uvicorn_error_logger.addHandler(console_handler)
    uvicorn_error_logger.addHandler(app_file_handler)
    uvicorn_error_logger.addHandler(error_file_handler)
    
    # 5. Uvicorn访问日志文件处理器 (按天轮转)
    access_file_handler = TimedRotatingFileHandler(
        ACCESS_LOG_FILE,
        when='midnight',  # 每天午夜轮转
        interval=1,  # 每天轮转一次
        backupCount=7,  # 保留7天的访问日志
        encoding='utf-8'
    )
    access_file_handler.setLevel(logging.INFO)
    access_formatter = UvicornAccessFormatter(
        '%(asctime)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    access_file_handler.setFormatter(access_formatter)
    
    uvicorn_access_logger.addHandler(console_handler)
    uvicorn_access_logger.addHandler(access_file_handler)
    
    # 6. 禁用某些不需要的日志
    # 例如，禁用uvicorn的默认访问日志，使用自定义的
    uvicorn_access_logger.setLevel(logging.INFO)
    
    return root_logger


# Uvicorn日志配置字典，用于传递给uvicorn.run()
uvicorn_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(asctime)s - %(levelname)s - %(client_addr)s - \"%(request_line)s\" %(status_code)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access_file": {
            "formatter": "access",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": ACCESS_LOG_FILE,
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": env_config.LOG_LEVEL,
        },
        "uvicorn.error": {
            "level": env_config.LOG_LEVEL,
        },
        "uvicorn.access": {
            "handlers": ["access", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}