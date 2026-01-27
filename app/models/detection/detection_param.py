# 检测参数表模型类
# 基于SQLAlchemy的ORM模型，用于表示具体检测参数数据和与数据库的交互
# 主要用于管理单个检测参数的详细信息，如名称、价格、单位等

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.extensions import Base

# 从associations导入多对多中间表
from app.models.associations import DetectionParamStandard


class DetectionParam(Base):
    """检测参数表模型类，对应数据库中的detection_param表
    
    该表用于管理单个检测参数的详细信息，如检测参数名称、价格、单位等
    """
    # 表名
    __tablename__ = 'detection_param'
    
    # 主键
    param_id = Column(Integer, primary_key=True, comment='参数ID，主键')
    
    # 外键
    item_id = Column(Integer, ForeignKey('detection_item.item_id'), nullable=False,
                     comment='项目ID，关联到detection_item表')
    
    # 关联委托单模板（多对一关系）
    template_id = Column(Integer, ForeignKey('delegation_form_template.template_id'), nullable=True,
                       comment='委托单模板ID，关联到delegation_form_template表')
    
    # 基本信息
    param_name = Column(String(255), nullable=False, comment='检测参数名称')
    price = Column(String(100), nullable=True, comment='检测价格，带单位，如：50.00元/组')
    sample_processing_fee = Column(String(100), nullable=True, comment='样品加工费，带单位，如：20.00元/组')
    is_regular_param = Column(Integer, default=1, comment='是否为常规参数：1=是，0=否')
    sort_order = Column(Integer, default=0, comment='排序序号，用于控制显示顺序')
    status = Column(Integer, default=1, comment='状态：1=启用，0=禁用')
    
    # 检测指南相关字段（从DetectionGuide迁移）
    sampling_batch = Column(String(255), nullable=True, comment='组批规则：如"每批次≤500吨取1组"')
    sampling_frequency = Column(String(255), nullable=True, comment='取样频率：如"每月1次"')
    sampling_require = Column(String(255), nullable=True, comment='取样要求：如"需使用无菌采样袋，采样量≥500g"')
    inspection_require = Column(String(255), nullable=True, comment='送检要求：如"样品需在24小时内送检"')
    required_info = Column(String(255), nullable=True, comment='所需信息：如"产品名称、批次号、生产日期、规格"')
    report_time = Column(String(50), nullable=True, comment='报告时间：如"常规5个工作日，加急3个工作日"')
    sample_image_path = Column(String(255), nullable=True, comment='取样方法示意图路径')
    
    # 唯一约束：同一项目下参数名称唯一
    __table_args__ = (
        UniqueConstraint('item_id', 'param_name', name='_item_param_uc'),
    )
    
    # 时间戳
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系定义
    # 一个检测参数属于一个检测项目
    item = relationship('DetectionItem', back_populates='detection_params',
                       info={'comment': '所属检测项目'})
    
    # 多对多关系：一个检测参数可以使用多个检测规范
    standards = relationship('DetectionStandard', secondary=DetectionParamStandard.__tablename__, 
                           back_populates='params', lazy='selectin',
                           info={'comment': '检测参数使用的所有检测规范'})
    
    # 多对一关系：一个检测参数只可以关联一个委托单模板
    template = relationship('DelegationFormTemplate', back_populates='params', lazy='selectin',
                          info={'comment': '检测参数使用的委托单模板'})
    
    def __repr__(self):
        """返回检测参数对象的字符串表示
        
        :return: 包含检测参数名称和ID的字符串
        """
        return f"<DetectionParam {self.param_name} ({self.param_id})>"
    
    @property
    def standard_ids(self):
        """返回关联的检测规范ID列表"""
        return [standard.standard_id for standard in self.standards] if self.standards else []
    
    def to_dict(self, include_standards=True, include_template=False, include_item=True, 
                standard_fields=None, template_fields=None, item_fields=None):
        """
        将检测参数对象转换为字典，用于API响应
        
        :param include_standards: 是否包含关联的检测规范信息，默认为True
        :param include_template: 是否包含关联的委托单模板信息，默认为False
        :param include_item: 是否包含关联的检测项目信息，默认为True
        :param standard_fields: 检测规范返回字段列表，None表示返回所有字段
        :param template_fields: 委托单模板返回字段列表，None表示返回所有字段
        :param item_fields: 检测项目返回字段列表，None表示返回所有字段
        :return: 包含检测参数信息的字典
        """
        # 基本字段
        data = {
            'param_id': self.param_id,
            'item_id': self.item_id,
            'template_id': self.template_id,
            'param_name': self.param_name,
            'price': self.price,
            'sample_processing_fee': self.sample_processing_fee,
            'is_regular_param': self.is_regular_param,
            'sort_order': self.sort_order,
            'status': self.status,
            'sampling_batch': self.sampling_batch,
            'sampling_frequency': self.sampling_frequency,
            'sampling_require': self.sampling_require,
            'inspection_require': self.inspection_require,
            'required_info': self.required_info,
            'report_time': self.report_time,
            'sample_image_path': self.sample_image_path,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }
        
        # 始终添加standard_ids字段
        data['standard_ids'] = self.standard_ids
        
        # 返回关联的检测项目信息（默认包含）
        if include_item and hasattr(self, 'item') and self.item:
            item_data = {
                'item_id': self.item.item_id,
                'item_name': self.item.item_name,
                'status': self.item.status
            }
            # 根据指定字段过滤
            if item_fields:
                item_data = {k: v for k, v in item_data.items() if k in item_fields}
            data['item'] = item_data
            
            # 返回关联的检测对象信息
            if hasattr(self.item, 'detection_object') and self.item.detection_object:
                data['object_id'] = self.item.detection_object.object_id
                data['object_name'] = self.item.detection_object.object_name
        
        # 返回关联的检测规范，包括id、规范代码、规范名称
        if include_standards:
            standards_list = []
            for standard in self.standards or []:
                # 返回id、规范代码、规范名称
                standard_data = {
                    'standard_id': standard.standard_id,
                    'standard_code': standard.standard_code,
                    'standard_name': standard.standard_name
                }
                # 根据指定字段过滤
                if standard_fields:
                    standard_data = {k: v for k, v in standard_data.items() if k in standard_fields}
                standards_list.append(standard_data)
            data['standards'] = standards_list
        
        # 返回关联的委托单模板，包括id、模板名称、模板版本等
        if include_template and hasattr(self, 'template') and self.template:
            from app.services.utils.link_generator import LinkGeneratorService
            from app.services.detection.utils.file_utils import generate_file_path
            
            template_data = {
                'template_id': self.template.template_id,
                'template_name': self.template.template_name,
                'template_version': self.template.template_version,
                'template_code': self.template.template_code,
                'file_path': self.template.file_path,
                'file_type': self.template.file_type
            }
            
            # 使用新的链接生成服务生成带签名的下载链接
            file_extension = self.template.file_type[1:] if self.template.file_type.startswith('.') else self.template.file_type
            file_path = generate_file_path(
                "delegation_form_templates",
                self.template.template_name,
                self.template.template_code,
                file_extension
            )
            template_data['download_url'] = LinkGeneratorService.generate_signed_url(file_path.as_posix())
            
            # 根据指定字段过滤
            if template_fields:
                template_data = {k: v for k, v in template_data.items() if k in template_fields}
            data['template'] = template_data
        
        return data