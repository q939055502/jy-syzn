# 检测对象表模型类
# 基于SQLAlchemy的ORM模型，用于表示检测对象数据和与数据库的交互
# 主要用于管理检测对象的详细信息，如材料名称、类型等

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.extensions import Base


class DetectionObject(Base):
    """检测对象表模型类，对应数据库中的detection_object表
    
    该表用于管理检测对象的详细信息，如材料名称、类型等
    """
    # 表名
    __tablename__ = 'detection_object'
    
    # 主键
    object_id = Column(Integer, primary_key=True, comment='检测对象ID，主键')
    
    # 基本信息
    object_code = Column(String(50), unique=True, nullable=True, comment='检测对象编码')
    object_name = Column(String(100), nullable=False, comment='检测对象名称')
    category_id = Column(Integer, ForeignKey('category.category_id'), nullable=False, comment='所属分类ID')
    description = Column(String(255), nullable=True, comment='检测对象描述')
    sort_order = Column(Integer, default=0, comment='排序序号')
    status = Column(Integer, default=1, comment='状态：1=启用，0=禁用')
    
    # 时间戳
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 唯一约束：同一分类下检测对象名称唯一
    __table_args__ = (
        UniqueConstraint('category_id', 'object_name', name='_category_object_name_uc'),
    )
    
    # 关系定义
    # 一个检测对象属于一个分类
    category = relationship('Category', back_populates='detection_objects',
                           info={'comment': '所属分类'})
    
    # 一个检测对象可以包含多个检测项目
    detection_items = relationship('DetectionItem', back_populates='detection_object',
                                  info={'comment': '包含的检测项目'})
    
    def __repr__(self):
        """返回检测对象对象的字符串表示
        
        :return: 包含检测对象名称和ID的字符串
        """
        return f"<DetectionObject {self.object_name} ({self.object_id})>"
    
    def to_dict(self):
        """
        将检测对象对象转换为字典，用于API响应
        
        :return: 包含检测对象信息的字典
        """
        return {
            'object_id': self.object_id,
            'object_code': self.object_code,
            'object_name': self.object_name,
            'category_id': self.category_id,
            'description': self.description,
            'sort_order': self.sort_order,
            'status': self.status,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }