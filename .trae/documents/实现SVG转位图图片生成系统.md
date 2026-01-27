# 实现SVG转位图图片生成系统

## 一、核心功能设计

### 1. 数据库模型设计
- 创建 `DataImage` 模型类，包含以下字段：
  - `image_id`: 主键ID
  - `data_unique_id`: 数据唯一标识
  - `device_type`: 设备类型（pc/phone/tablet）
  - `svg_content`: SVG原始字符串
  - `png_data`: PNG位图二进制数据
  - `version`: 版本号
  - `created_at`: 创建时间
  - `updated_at`: 更新时间
- 设计复合唯一索引：`(data_unique_id, device_type)`

### 2. 服务层实现
- **SVG生成服务**：负责动态生成SVG字符串，包含文字坐标随机偏移、轻微旋转等防爬混淆
- **SVG转位图服务**：使用 `cairosvg` 库将SVG转换为PNG，添加半透明水印、随机干扰点等防爬效果
- **缓存管理服务**：实现Redis缓存的读写和过期管理
- **异步重生成服务**：使用FastAPI的BackgroundTasks实现批量重生成功能
- **任务进度服务**：通过Redis记录和查询任务进度

### 3. API接口设计
- **公开图片接口**：`GET /api/image/{data_unique_id}`，根据设备类型返回PNG图片
- **管理员批量重生成接口**：`POST /api/admin/image/regenerate`，支持按条件筛选并触发批量重生成
- **任务进度查询接口**：`GET /api/admin/image/task/{task_id}`，返回任务执行状态和进度

## 二、实现步骤

### 1. 安装依赖
- 添加 `cairosvg` 用于SVG转PNG
- 添加 `pillow` 用于图片处理
- 更新 `requirements.txt`

### 2. 创建数据库模型
- 在 `app/models` 目录下创建 `image` 子模块
- 实现 `DataImage` 模型类
- 更新 `__init__.py` 导出新模型

### 3. 实现数据访问层
- 创建 `DataImageDAL` 类，继承自 `BaseDAL`
- 实现模型的CRUD操作

### 4. 实现服务层
- 创建 `ImageService` 类，包含SVG生成、转位图、缓存管理等功能
- 实现异步批量重生成逻辑
- 实现任务进度管理

### 5. 实现API接口
- 创建 `image.py` 路由文件，添加公开图片接口
- 在 `admin` 路由下添加图片管理相关接口

### 6. 集成到现有系统
- 更新 `app.py` 注册新路由
- 更新数据库初始化脚本

## 三、技术要点

### 1. SVG生成与混淆
- 使用纯字符串拼接生成SVG，动态计算画布尺寸
- 添加文字坐标随机偏移（±1px）
- 添加文字轻微旋转（±0.5度）

### 2. SVG转位图
- 使用 `cairosvg.svg2png()` 进行转换
- 设置不同设备的分辨率（300dpi）
- 添加半透明水印（透明度0.1）
- 添加随机透明干扰点

### 3. 缓存策略
- Redis Key格式：`data_img:{data_unique_id}:{device_type}`
- 缓存过期时间：15天
- 缓存未命中时，从MySQL读取并回写Redis

### 4. 异步重生成
- 使用FastAPI的BackgroundTasks处理异步任务
- 通过Redis记录任务进度
- 支持按条件筛选目标数据

### 5. 权限控制
- 管理员接口通过OAuth2认证保护
- 仅超级管理员/指定运维角色可访问

## 四、文件结构

```
app/
├── models/
│   └── image/
│       └── data_image.py
├── dal/
│   └── data_image_dal.py
├── services/
│   └── image/
│       └── image_service.py
└── routes/
    ├── image.py
    └── admin/
        └── image.py
```

## 五、关键代码实现

### 1. 模型类实现
```python
class DataImage(Base):
    __tablename__ = "data_images"
    
    image_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data_unique_id = Column(String(255), nullable=False, index=True)
    device_type = Column(String(20), nullable=False, index=True)
    svg_content = Column(Text, nullable=False)
    png_data = Column(LargeBinary, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('data_unique_id', 'device_type', name='_data_device_uc'),
    )
```

### 2. 服务层核心方法
```python
class ImageService:
    @staticmethod
    def generate_svg(data: dict) -> str:
        # 生成带混淆的SVG字符串
        pass
    
    @staticmethod
    def svg_to_png(svg_content: str, device_type: str) -> bytes:
        # 将SVG转换为PNG，并添加防爬效果
        pass
    
    @staticmethod
    async def regenerate_images(background_tasks: BackgroundTasks, data_filter: dict) -> str:
        # 异步批量重生成图片
        pass
```

### 3. 公开图片接口
```python
@router.get("/api/image/{data_unique_id}", summary="获取图片")
def get_image(
    data_unique_id: str,
    device_type: str = Query(..., description="设备类型：pc/phone/tablet")
):
    # 从Redis或MySQL获取图片数据
    pass
```

## 六、测试与优化

1. **单元测试**：编写核心功能的单元测试
2. **性能测试**：测试SVG生成、转位图的性能
3. **防爬测试**：验证防爬效果
4. **缓存测试**：测试缓存命中率和失效机制
5. **异步测试**：测试批量重生成的异步执行效果

## 七、部署与监控

1. **依赖安装**：在生产环境安装 `cairosvg` 和 `pillow`
2. **日志记录**：添加关键操作的日志记录
3. **监控指标**：添加图片生成成功率、缓存命中率等监控指标
4. **错误处理**：完善异常处理机制，确保接口稳定可用