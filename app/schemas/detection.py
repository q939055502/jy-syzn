from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Generic, TypeVar, Dict, Any
from datetime import datetime, date

# 定义泛型类型变量
T = TypeVar('T')


# 分类模型
class CategoryBase(BaseModel):
    """分类基础模型"""
    category_name: str = Field(..., description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: Optional[int] = Field(0, description="排序序号")
    status: Optional[int] = Field(1, description="状态：1=启用，0=禁用")


class CategoryCreate(CategoryBase):
    """创建分类请求模型"""
    pass


class CategoryUpdate(CategoryBase):
    """更新分类请求模型"""
    category_name: Optional[str] = Field(None, description="分类名称")


class CategoryResponse(CategoryBase):
    """分类响应模型"""
    category_id: int = Field(..., description="分类ID")
    create_time: Optional[str] = Field(None, description="创建时间")
    update_time: Optional[str] = Field(None, description="更新时间")

    class Config:
        from_attributes = True

# 更新前向引用
CategoryResponse.model_rebuild()


# 检测规范模型
class DetectionStandardBase(BaseModel):
    """检测规范基础模型"""
    standard_code: str = Field(..., description="规范编号")
    standard_name: str = Field(..., description="规范名称")
    standard_type: Optional[str] = Field(None, description="规范类型")
    effective_time: Optional[date] = Field(None, description="生效日期")
    invalid_time: Optional[date] = Field(None, description="失效日期")
    status: Optional[int] = Field(1, description="状态：1=有效，0=作废，2=待生效")
    replace_id: Optional[int] = Field(None, description="替代的规范ID")
    remark: Optional[str] = Field(None, description="备注信息")


class DetectionStandardCreate(DetectionStandardBase):
    """创建检测规范请求模型"""
    pass


class DetectionStandardUpdate(DetectionStandardBase):
    """更新检测规范请求模型"""
    standard_code: Optional[str] = Field(None, description="规范编号")
    standard_name: Optional[str] = Field(None, description="规范名称")


class DetectionStandardResponse(DetectionStandardBase):
    """检测规范响应模型"""
    standard_id: int = Field(..., description="规范ID")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


# 检测对象模型
class DetectionObjectBase(BaseModel):
    """检测对象基础模型"""
    object_name: str = Field(..., description="检测对象名称")
    object_code: Optional[str] = Field(None, description="检测对象编码")
    category_id: int = Field(..., description="分类ID")
    description: Optional[str] = Field(None, description="检测对象描述")
    sort_order: Optional[int] = Field(0, description="排序序号")
    status: Optional[int] = Field(1, description="状态：1=启用，0=禁用")


class DetectionObjectCreate(DetectionObjectBase):
    """创建检测对象请求模型"""
    pass


class DetectionObjectUpdate(DetectionObjectBase):
    """更新检测对象请求模型"""
    object_name: Optional[str] = Field(None, description="检测对象名称")
    category_id: Optional[int] = Field(None, description="分类ID")


class DetectionObjectResponse(DetectionObjectBase):
    """检测对象响应模型"""
    object_id: int = Field(..., description="检测对象ID")
    create_time: Optional[str] = Field(None, description="创建时间")
    update_time: Optional[str] = Field(None, description="更新时间")
    category_name: Optional[str] = Field(None, description="分类名称")

    class Config:
        from_attributes = True


# 检测项目模型
class DetectionItemBase(BaseModel):
    """检测项目基础模型"""
    object_id: int = Field(..., description="检测对象ID")
    item_name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    sort_order: Optional[int] = Field(0, description="排序序号")
    status: Optional[int] = Field(1, description="状态：1=启用，0=禁用")


class DetectionItemCreate(DetectionItemBase):
    """创建检测项目请求模型"""
    pass


class DetectionItemUpdate(DetectionItemBase):
    """更新检测项目请求模型"""
    object_id: Optional[int] = Field(None, description="检测对象ID")
    item_name: Optional[str] = Field(None, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")


class DetectionItemResponse(DetectionItemBase):
    """检测项目响应模型"""
    item_id: int = Field(..., description="项目ID")
    create_time: Optional[str] = Field(None, description="创建时间")
    update_time: Optional[str] = Field(None, description="更新时间")
    object_name: Optional[str] = Field(None, description="检测对象名称")

    class Config:
        from_attributes = True


# 检测参数模型
class DetectionParamBase(BaseModel):
    """检测参数基础模型"""
    item_id: int = Field(..., description="项目ID")
    param_name: str = Field(..., description="检测参数名称")
    price: Optional[str] = Field(None, description="检测价格，带单位，如：50.00元/组")
    sample_processing_fee: Optional[str] = Field(None, description="样品加工费，带单位，如：20.00元/组")
    is_regular_param: Optional[int] = Field(1, description="是否为常规参数：1=是，0=否")
    sort_order: Optional[int] = Field(0, description="排序序号")
    status: Optional[int] = Field(1, description="状态：1=启用，0=禁用")
    template_id: Optional[int] = Field(None, description="关联的委托单模板ID")
    # 检测指南相关字段（从DetectionGuide迁移）
    sampling_batch: Optional[str] = Field(None, description="组批规则：如\"每批次≤500吨取1组\"")
    sampling_frequency: Optional[str] = Field(None, description="取样频率：如\"每月1次\"")
    sampling_require: Optional[str] = Field(None, description="取样要求：如\"需使用无菌采样袋，采样量≥500g\"")
    inspection_require: Optional[str] = Field(None, description="送检要求：如\"样品需在24小时内送检\"")
    required_info: Optional[str] = Field(None, description="所需信息：如\"产品名称、批次号、生产日期、规格\"")
    report_time: Optional[str] = Field(None, description="报告时间：如\"常规5个工作日，加急3个工作日\"")
    sample_image_path: Optional[str] = Field(None, description="取样方法示意图路径")


class DetectionParamCreate(DetectionParamBase):
    """创建检测参数请求模型"""
    standard_ids: Optional[List[int]] = Field([], description="关联的检测规范ID列表")


class DetectionParamUpdate(DetectionParamBase):
    """更新检测参数请求模型"""
    item_id: Optional[int] = Field(None, description="项目ID")
    param_name: Optional[str] = Field(None, description="检测参数名称")
    standard_ids: Optional[List[int]] = Field(None, description="关联的检测规范ID列表")


class DetectionParamResponse(DetectionParamBase):
    """检测参数响应模型"""
    param_id: int = Field(..., description="参数ID")
    create_time: Optional[str] = Field(None, description="创建时间")
    update_time: Optional[str] = Field(None, description="更新时间")
    standard_ids: Optional[List[int]] = Field([], description="关联的检测规范ID列表")
    standards: Optional[List[Dict[str, Any]]] = Field([], description="关联的检测规范列表")
    object_id: Optional[int] = Field(None, description="检测对象ID")
    object_name: Optional[str] = Field(None, description="检测对象名称")
    template: Optional[Dict[str, Any]] = Field(None, description="关联的委托单模板信息")

    class Config:
        from_attributes = True


# 委托单模板模型
class DelegationFormTemplateBase(BaseModel):
    """委托单模板基础模型"""
    template_name: str = Field(..., description="模板名称")
    template_version: str = Field(..., description="模板版本")
    template_code: Optional[str] = Field(None, description="模板编号")
    file_path: str = Field(..., description="模板文件路径")
    file_type: Optional[str] = Field(None, description="文件类型")
    upload_user: Optional[str] = Field(None, description="上传人")
    status: Optional[int] = Field(1, description="状态：1=启用，0=禁用")
    remark: Optional[str] = Field(None, description="备注")


class DelegationFormTemplateCreate(DelegationFormTemplateBase):
    """创建委托单模板请求模型"""
    pass


class DelegationFormTemplateUpdate(DelegationFormTemplateBase):
    """更新委托单模板请求模型"""
    template_name: Optional[str] = Field(None, description="模板名称")
    template_version: Optional[str] = Field(None, description="模板版本")
    file_path: Optional[str] = Field(None, description="模板文件路径")


class DelegationFormTemplateResponse(DelegationFormTemplateBase):
    """委托单模板响应模型"""
    template_id: int = Field(..., description="模板ID")
    upload_time: Optional[datetime] = Field(None, description="上传时间")
    download_url: Optional[str] = Field(None, description="模板下载链接")

    class Config:
        from_attributes = True


# 简化的委托单模板下载信息模型
class TemplateDownloadInfo(BaseModel):
    """简化的委托单模板下载信息模型"""
    id: int = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    code: Optional[str] = Field(None, description="模板编号")
    download_url: Optional[str] = Field(None, description="模板下载链接")

    class Config:
        from_attributes = False





# 通用响应模型
class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")


class ListResponseModel(BaseModel, Generic[T]):
    """列表响应模型"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[List[T]] = Field(None, description="响应数据列表")
    total: int = Field(0, description="数据总数")
