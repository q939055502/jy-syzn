from fastapi import APIRouter, HTTPException
from typing import Optional
from app.schemas.detection import (
    DetectionStandardCreate, DetectionStandardUpdate, DetectionStandardResponse,
    ResponseModel, ListResponseModel
)
from app.services.detection import DetectionStandardService

# 创建路由实例
router = APIRouter()


@router.get("/standards", response_model=ListResponseModel[DetectionStandardResponse])
def get_standards(page: int = 1, limit: int = 100, status: Optional[int] = None):
    """获取所有检测规范，支持分页和状态筛选"""
    if status is not None:
        # 按状态获取检测规范
        standards, error = DetectionStandardService.get_by_status(status)
    else:
        # 获取所有检测规范
        standards, error = DetectionStandardService.get_all()
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # 处理分页
    start = (page - 1) * limit
    end = start + limit
    paginated_standards = standards[start:end]
    
    return {"data": paginated_standards, "total": len(standards), "message": "获取检测规范列表成功"}


@router.get("/standards/{standard_id}", response_model=ResponseModel[DetectionStandardResponse])
def get_standard(standard_id: int):
    """获取单个检测规范"""
    standard, error = DetectionStandardService.get_by_id(standard_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": standard, "message": "获取检测规范成功"}


@router.post("/standards", response_model=ResponseModel[DetectionStandardResponse], status_code=201)
def create_standard(standard: DetectionStandardCreate):
    """创建检测规范"""
    standard_obj, error = DetectionStandardService.create(standard.model_dump())
    if error:
        if "不能为空" in error:
            raise HTTPException(status_code=400, detail=error)
        if "不能重复" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": standard_obj, "message": "创建检测规范成功", "code": 201}


@router.put("/standards/{standard_id}", response_model=ResponseModel[DetectionStandardResponse])
def update_standard(standard_id: int, standard: DetectionStandardUpdate):
    """更新检测规范"""
    standard_obj, error = DetectionStandardService.update(standard_id, standard.model_dump(exclude_unset=True))
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        if "不能为空" in error:
            raise HTTPException(status_code=400, detail=error)
        if "不能重复" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": standard_obj, "message": "更新检测规范成功"}


@router.delete("/standards/{standard_id}", response_model=ResponseModel[DetectionStandardResponse], status_code=200)
def delete_standard(standard_id: int):
    """删除检测规范"""
    success, error = DetectionStandardService.delete(standard_id)
    if error:
        print(f"Delete standard error: {error}")
        error_str = str(error)
        if "不存在" in error_str:
            raise HTTPException(status_code=404, detail=error_str)
        if "无法删除" in error_str:
            raise HTTPException(status_code=400, detail=error_str)
        raise HTTPException(status_code=500, detail=error_str)
    return {"data": None, "message": "删除检测规范成功"}


@router.patch("/standards/{standard_id}/enable", response_model=ResponseModel[DetectionStandardResponse])
def enable_standard(standard_id: int):
    """启用检测规范"""
    standard, error = DetectionStandardService.enable_standard(standard_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": standard, "message": "启用检测规范成功"}


@router.patch("/standards/{standard_id}/disable", response_model=ResponseModel[DetectionStandardResponse])
def disable_standard(standard_id: int):
    """禁用检测规范"""
    standard, error = DetectionStandardService.disable_standard(standard_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": standard, "message": "禁用检测规范成功"}
