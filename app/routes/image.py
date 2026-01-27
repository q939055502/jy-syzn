# 图片相关路由
# 包含公开的图片获取接口

from fastapi import APIRouter, Query, Response, HTTPException, status, Body
from pydantic import BaseModel
from app.services.image.image_service import ImageService
from app.services.detection.detection_param_service import DetectionParamService
from app.schemas.detection import ResponseModel


# 创建路由实例
router = APIRouter(prefix="/api/image", tags=["image"])


# 定义请求体模型
class DetectionImageRequest(BaseModel):
    """检测参数图片生成请求模型"""
    item_id: int
    item_name: str
    device_type: str = "pc"


@router.get("/{data_unique_id}", summary="获取图片")
def get_image(
    data_unique_id: str,
    device_type: str = Query(..., description="设备类型：pc/phone/tablet", regex="^(pc|phone|tablet)$"),
    image_type: str = Query("png", description="图片类型：png或svg", regex="^(png|svg)$")
):
    """
    根据数据唯一标识和设备类型获取图片
    
    - **data_unique_id**: 数据唯一标识
    - **device_type**: 设备类型，必须是pc、phone或tablet中的一个
    - **image_type**: 图片类型，可选值：png或svg，默认：png
    
    返回PNG或SVG图片，可直接用于img标签的src属性
    """
    # 使用ImageService获取图片数据
    image_data = ImageService.get_image(data_unique_id, device_type, image_type)
    
    # 根据图片类型返回不同的媒体类型
    media_type = "image/png" if image_type == "png" else "image/svg+xml"
    
    # 返回Response对象，包含图片数据和正确的media_type
    return Response(content=image_data, media_type=media_type)


@router.post("/detection", response_model=ResponseModel, summary="生成检测参数图片")
def generate_detection_image(
    request: DetectionImageRequest = Body(..., description="检测参数图片生成请求")
):
    """
    生成检测参数图片
    
    - **item_id**: 检测项目ID
    - **item_name**: 检测项目名称
    - **device_type**: 设备类型，可选值：pc/phone/tablet，默认：pc
    
    生成检测参数图片并保存到数据库和Redis，返回成功或失败信息
    """
    try:
        # 调用Service层生成检测参数图片
        result = ImageService.generate_detection_image(request.item_id, request.item_name)
        
        return ResponseModel(
            data={
                "data_unique_id": result["data_unique_id"],
                "item_id": result["item_id"],
                "item_name": result["item_name"],
                "device_type": request.device_type
            },
            message="检测参数图片生成成功"
        )
    except Exception as e:
        # 处理Service层抛出的异常
        if "没有启用的检测参数" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检测参数图片生成失败: {str(e)}"
        )
