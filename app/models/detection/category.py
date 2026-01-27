# 分类表模型类
# 基于SQLAlchemy的ORM模型，用于表示检测项目的分类数据和与数据库的交互
# 主要用于对检测项目组进行分类管理，支持树形结构（通过parent_id实现）

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.extensions import Base


class Category(Base):
    """分类表模型类，对应数据库中的category表
    
    该表用于管理检测项目的分类结构，支持多级分类
    """
    # 表名
    __tablename__ = 'category'
    
    # 主键
    category_id = Column(Integer, primary_key=True, comment='分类ID，主键')
    
    # 基本信息
    category_name = Column(String(100), nullable=False, comment='分类名称')
    parent_id = Column(Integer, ForeignKey('category.category_id'), nullable=True, default=None, comment='父分类ID，NULL表示顶级分类')
    sort_order = Column(Integer, default=0, comment='排序序号，用于控制显示顺序')
    status = Column(Integer, default=1, comment='状态：1=启用，0=禁用')
    
    # 唯一约束：同一父分类下分类名称唯一
    __table_args__ = (
        UniqueConstraint('category_name', 'parent_id', name='_category_name_parent_uc'),
    )
    
    # 时间戳
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    # 一个分类可以有多个检测对象
    detection_objects = relationship('DetectionObject', back_populates='category', lazy=True, info={'comment': '分类下的所有检测对象'})
    
    # 自引用关系，用于实现树形结构
    parent = relationship('Category', remote_side=[category_id], backref='children', lazy=True, info={'comment': '父分类'})
    
    def __repr__(self):
        """返回分类对象的字符串表示
        
        :return: 包含分类名称和ID的字符串
        """
        return f"<Category {self.category_name} ({self.category_id})>"
    
    def to_dict(self):
        """
        将分类对象转换为字典，用于API响应
        
        :return: 包含分类信息的字典
        """
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'status': self.status,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }
