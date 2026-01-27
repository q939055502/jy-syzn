# 检测服务初始化文件

# 导出所有检测相关服务类
from app.services.detection.category_service import CategoryService
from app.services.detection.detection_standard_service import DetectionStandardService
from app.services.detection.detection_object_service import DetectionObjectService
from app.services.detection.detection_item_service import DetectionItemService
from app.services.detection.detection_param_service import DetectionParamService
from app.services.detection.delegation_form_template_service import DelegationFormTemplateService

__all__ = [
    'CategoryService',
    'DetectionStandardService',
    'DetectionObjectService',
    'DetectionItemService',
    'DetectionParamService',
    'DelegationFormTemplateService'
]
