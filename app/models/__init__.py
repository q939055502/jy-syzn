# 数据访问层初始化文件
# 导入并暴露所有模型类

from .user.user import User
# 从detection子模块导入所有检测相关模型
from .detection import Category, DetectionObject, DetectionStandard, DetectionItem, DetectionParam, DelegationFormTemplate
# 从image子模块导入图片相关模型
from .image.data_image import DataImage
# 导入多对多中间表
from .associations import DetectionParamStandard

# 导出模型类列表
__all__ = ['User', 'Category', 'DetectionObject', 'DetectionStandard', 'DetectionItem', 'DetectionParam', 'DelegationFormTemplate', 'DataImage', 'DetectionParamStandard']
