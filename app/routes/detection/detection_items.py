from fastapi import APIRouter, HTTPException
from typing import Optional
from app.schemas.detection import (
    DetectionItemCreate, DetectionItemUpdate, DetectionItemResponse,
    ResponseModel, ListResponseModel
)
from app.services.detection import DetectionItemService

# 创建路由实例
router = APIRouter()


@router.get("/items", response_model=ListResponseModel[DetectionItemResponse])
def get_items(page: int = 1, limit: int = 100, status: Optional[int] = None):
    """获取所有检测项目，支持分页和状态筛选"""
    if status is not None:
        # 按状态获取检测项目
        items, error = DetectionItemService.get_by_status(status)
    else:
        # 获取所有检测项目
        items, error = DetectionItemService.get_all()
    
    if error:
        return ListResponseModel(code=500, message=error, data=None, total=0)
    
    # 处理分页
    start = (page - 1) * limit
    end = start + limit
    paginated_items = items[start:end]
    
    return ListResponseModel(code=200, message="获取检测项目列表成功", data=paginated_items, total=len(items))


@router.get("/items/{item_id}", response_model=ResponseModel[DetectionItemResponse])
def get_item(item_id: int):
    """获取单个检测项目"""
    item, error = DetectionItemService.get_by_id(item_id)
    if error:
        if "不存在" in error:
            return ResponseModel(code=404, message=error, data=None)
        return ResponseModel(code=500, message=error, data=None)
    return ResponseModel(code=200, message="获取检测项目成功", data=item)


@router.post("/items", response_model=ResponseModel[DetectionItemResponse])
def create_item(item: DetectionItemCreate):
    """创建检测项目"""
    item_obj, error = DetectionItemService.create(item.dict())
    if error:
        if "不能为空" in error or "不能重复" in error or "已禁用" in error:
            return ResponseModel(code=400, message=error, data=None)
        if "不存在" in error:
            return ResponseModel(code=404, message=error, data=None)
        return ResponseModel(code=500, message=error, data=None)
    return ResponseModel(code=201, message="创建检测项目成功", data=item_obj)


@router.put("/items/{item_id}", response_model=ResponseModel[DetectionItemResponse])
def update_item(item_id: int, item: DetectionItemUpdate):
    """更新检测项目"""
    item_obj, error = DetectionItemService.update(item_id, item.dict(exclude_unset=True))
    if error:
        if "不能为空" in error or "不能重复" in error or "已禁用" in error:
            return ResponseModel(code=400, message=error, data=None)
        if "不存在" in error:
            return ResponseModel(code=404, message=error, data=None)
        return ResponseModel(code=500, message=error, data=None)
    return ResponseModel(code=200, message="更新检测项目成功", data=item_obj)


@router.delete("/items/{item_id}", response_model=ResponseModel)
def delete_item(item_id: int):
    """删除检测项目"""
    success, error = DetectionItemService.delete(item_id)
    if error:
        if "不存在" in error:
            return ResponseModel(code=404, message=error, data=None)
        if "关联了" in error:
            return ResponseModel(code=400, message=error, data=None)
        return ResponseModel(code=500, message=error, data=None)
    return ResponseModel(code=200, message="删除检测项目成功", data=None)
