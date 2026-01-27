from fastapi import APIRouter, HTTPException
from typing import Optional
from app.schemas.detection import (
    DetectionObjectCreate, DetectionObjectUpdate, DetectionObjectResponse,
    ResponseModel, ListResponseModel
)
from app.services.detection import DetectionObjectService

# 创建路由实例
router = APIRouter()


@router.get("/objects", response_model=ListResponseModel[DetectionObjectResponse])
def get_objects(page: int = 1, limit: int = 100, status: Optional[int] = None, search: Optional[str] = None):
    """获取检测对象列表，支持分页、状态过滤和名称/编码搜索"""
    if search:
        # 调用搜索服务方法，同时传递status参数进行过滤
        objects, error = DetectionObjectService.search(search, status)
    elif status is not None:
        # 调用按状态查询方法
        objects, error = DetectionObjectService.get_by_status(status)
    else:
        # 获取所有
        objects, error = DetectionObjectService.get_all()
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # 处理分页
    start = (page - 1) * limit
    end = start + limit
    paginated_objects = objects[start:end]
    
    return {"data": paginated_objects, "total": len(objects), "message": "获取检测对象列表成功"}


@router.get("/objects/{object_id}", response_model=ResponseModel[DetectionObjectResponse])
def get_object(object_id: int):
    """获取单个检测对象"""
    obj, error = DetectionObjectService.get_by_id(object_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": obj, "message": "获取检测对象成功"}


@router.post("/objects", response_model=ResponseModel[DetectionObjectResponse], status_code=201)
def create_object(obj: DetectionObjectCreate):
    """创建检测对象"""
    obj_data, error = DetectionObjectService.create(obj.model_dump())
    if error:
        if "不能为空" in error or "已禁用" in error or "不能重复" in error:
            raise HTTPException(status_code=400, detail=error)
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": obj_data, "message": "创建检测对象成功", "code": 201}


@router.put("/objects/{object_id}", response_model=ResponseModel[DetectionObjectResponse])
def update_object(object_id: int, obj: DetectionObjectUpdate):
    """更新检测对象"""
    obj_data, error = DetectionObjectService.update(object_id, obj.model_dump(exclude_unset=True))
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        if "不能为空" in error or "已禁用" in error or "不能重复" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": obj_data, "message": "更新检测对象成功"}


@router.delete("/objects/{object_id}", response_model=ResponseModel, status_code=200)
def delete_object(object_id: int):
    """删除检测对象"""
    success, error = DetectionObjectService.delete(object_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        if "关联了" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"message": "删除检测对象成功"}