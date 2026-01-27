# 数据图片模型类
# 基于SQLAlchemy的ORM模型，用于存储SVG和PNG图片数据

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime, UniqueConstraint
from app.extensions import Base


class DataImage(Base):
    """数据图片模型类，对应数据库中的data_images表"""
    # 表名
    __tablename__ = 'data_images'
    
    # 主键
    image_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 核心字段
    data_unique_id = Column(String(255), nullable=False, index=True, comment="数据唯一标识")
    device_type = Column(String(20), nullable=False, index=True, comment="设备类型：pc/phone/tablet")
    svg_content = Column(Text(length=16777215), nullable=False, comment="SVG原始字符串")
    png_data = Column(LargeBinary(length=16777215), nullable=False, comment="PNG位图二进制数据")
    version = Column(Integer, default=1, comment="版本号")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 表级约束
    __table_args__ = (
        UniqueConstraint('data_unique_id', 'device_type', name='_data_device_uc'),
    )
    
    # 映射器参数，明确指定主键字段
    __mapper_args__ = {
        'primary_key': [image_id],
    }
    
    def __repr__(self):
        """返回数据图片对象的字符串表示"""
        return f"<DataImage {self.data_unique_id} ({self.device_type})>"
