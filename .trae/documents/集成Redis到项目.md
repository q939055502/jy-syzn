# Redis集成实现计划

## 1. 目录结构设计

Redis集成将在现有项目结构基础上进行扩展，不需要创建新的目录，主要修改以下文件：

```
项目根目录/
├── config.py            # 添加Redis配置
├── app/
│   ├── extensions.py     # 添加Redis客户端初始化
│   └── utils/
│       └── redis_utils.py # 添加Redis工具函数（可选）
```

## 2. 实现内容

### 2.1 配置文件修改

在`config.py`中添加Redis相关配置：

| 配置项 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| REDIS_URL | 字符串 | redis://localhost:6379/0 | Redis连接URL |
| REDIS_HOST | 字符串 | localhost | Redis主机地址 |
| REDIS_PORT | 整数 | 6379 | Redis端口 |
| REDIS_DB | 整数 | 0 | Redis数据库编号 |
| REDIS_PASSWORD | 字符串 | None | Redis密码 |

### 2.2 扩展初始化

在`app/extensions.py`中添加Redis客户端初始化：

- 使用`redis-py`库创建Redis客户端
- 提供`init_redis`函数初始化Redis连接
- 提供`get_redis`依赖函数获取Redis客户端
- 提供Redis连接池管理

### 2.3 Redis工具函数（可选）

在`app/utils/redis_utils.py`中添加常用的Redis操作工具函数：

- 缓存操作：设置、获取、删除缓存
- 分布式锁：获取和释放锁
- 计数器：自增、自减操作
- 哈希操作：设置和获取哈希字段

### 2.4 依赖库

需要安装的依赖：
```
redis>=5.0.0
```

## 3. 实现步骤

1. 更新`config.py`，添加Redis配置
2. 安装Redis依赖
3. 修改`app/extensions.py`，添加Redis客户端初始化
4. 创建`app/utils/redis_utils.py`，添加Redis工具函数（可选）
5. 测试Redis连接和基本操作

## 4. 技术要点

1. **连接池管理**：使用Redis连接池提高性能
2. **错误处理**：添加适当的异常处理
3. **类型安全**：使用类型提示确保代码安全性
4. **配置优先级**：支持从环境变量读取配置，优先于默认值
5. **依赖注入**：使用FastAPI的依赖注入机制提供Redis客户端
6. **多环境支持**：不同环境可以配置不同的Redis实例

## 5. 预期效果

- 成功连接Redis服务器
- 提供可复用的Redis客户端
- 支持依赖注入获取Redis连接
- 提供常用的Redis操作工具函数
- 支持不同环境的Redis配置

## 6. 集成示例

### 使用示例

```python
from fastapi import APIRouter, Depends
from app.extensions import get_redis
from redis import Redis

router = APIRouter(prefix="/api")

@router.get("/redis-test")
def redis_test(redis: Redis = Depends(get_redis)):
    """测试Redis连接"""
    # 设置缓存
    redis.set("test_key", "test_value", ex=3600)
    # 获取缓存
    value = redis.get("test_key")
    return {
        "message": "Redis连接成功",
        "value": value.decode() if value else None
    }
```

### 缓存装饰器示例

```python
from functools import wraps
from app.extensions import get_redis
from redis import Redis

def redis_cache(expire=3600):
    """Redis缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = next(get_redis())
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # 尝试从缓存获取
            cached = redis.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            redis.set(cache_key, json.dumps(result), ex=expire)
            
            return result
        return wrapper
    return decorator
```

## 7. 测试计划

1. 验证Redis连接是否成功
2. 测试基本的Redis操作（set、get、delete）
3. 测试Redis工具函数
4. 测试缓存装饰器
5. 测试分布式锁

通过以上步骤，我们将成功将Redis集成到项目中，为后续的缓存、分布式锁等功能提供支持。