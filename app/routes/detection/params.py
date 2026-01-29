from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.schemas.detection import (
    DetectionParamCreate, DetectionParamUpdate, DetectionParamResponse,
    ResponseModel, ListResponseModel
)
from app.services.detection import DetectionParamService

# 创建路由实例
router = APIRouter()


@router.get("/params", response_model=ListResponseModel[DetectionParamResponse])
def get_params(
    page: int = Query(1, ge=1, description="当前页码"),
    limit: int = Query(100, ge=1, le=1000, description="每页数量"),
    param_name: Optional[str] = Query(None, description="检测参数名称"),
    material_name: Optional[str] = Query(None, description="材料名称"),
    item_id: Optional[int] = Query(None, description="项目ID"),
    status: Optional[int] = Query(None, description="状态：1=启用，0=禁用")
):
    """获取所有检测参数，支持分页和过滤"""
    # 构建过滤参数
    filter_params = {}
    if item_id is not None:
        filter_params["item_id"] = item_id
    if status is not None:
        filter_params["status"] = status
    
    # 判断是否需要搜索
    if param_name or material_name:
        search_params = {}
        if param_name:
            search_params["param_name"] = param_name
        if material_name:
            search_params["material_name"] = material_name
        if item_id:
            search_params["item_id"] = item_id
        if status:
            search_params["status"] = status
        
        params, total, error = DetectionParamService.search(search_params, page=page, limit=limit)
    else:
        # 获取所有检测参数
        params, total, error = DetectionParamService.get_all(page=page, limit=limit)
    
    if error:
        return ListResponseModel(code=500, message=error, data=None, total=0)
    
    # 将检测参数转换为字典
    param_dicts = []
    for param in params:
        # 使用to_dict方法
        param_dict = param.to_dict(include_standards=True, include_template=True)
        param_dicts.append(param_dict)
    
    return ListResponseModel(code=200, message="获取检测参数列表成功", data=param_dicts, total=total)


@router.get("/params/{param_id}", response_model=ResponseModel[DetectionParamResponse])
def get_param(param_id: int):
    """获取单个检测参数"""
    param, error = DetectionParamService.get_with_relations(param_id)
    if error:
        if "不存在" in error:
            return ResponseModel(code=404, message=error, data=None)
        return ResponseModel(code=500, message=error, data=None)
    
    # 将检测参数转换为字典
    param_dict = param.to_dict(include_standards=True, include_template=True)
    
    return ResponseModel(code=200, message="获取检测参数成功", data=param_dict)


@router.post("/params", response_model=ResponseModel[DetectionParamResponse])
def create_param(param: DetectionParamCreate):
    """创建检测参数"""
    # 注意：实际项目中需要添加权限验证，仅允许管理员访问
    param_obj, error = DetectionParamService.create(param.dict())
    if error:
        if "不能为空" in error or "不能重复" in error or "已禁用" in error:
            return ResponseModel(code=400, message=error, data=None)
        if "不存在" in error:
            return ResponseModel(code=404, message=error, data=None)
        return ResponseModel(code=500, message=error, data=None)
    # 将检测参数转换为字典
    param_dict = param_obj.to_dict(include_standards=True, include_template=True)
    return ResponseModel(code=201, message="创建检测参数成功", data=param_dict)


@router.put("/params/{param_id}", response_model=ResponseModel[DetectionParamResponse])
def update_param(param_id: int, param: DetectionParamUpdate):
    """更新检测参数"""
    # 注意：实际项目中需要添加权限验证，仅允许管理员访问
    param_obj, error = DetectionParamService.update(param_id, param.dict(exclude_unset=True))
    if error:
        if "不能为空" in error or "不能重复" in error or "已禁用" in error:
            return ResponseModel(code=400, message=error, data=None)
        if "不存在" in error:
            return ResponseModel(code=404, message=error, data=None)
        return ResponseModel(code=500, message=error, data=None)
    # 将检测参数转换为字典
    param_dict = param_obj.to_dict(include_standards=True, include_template=True)
    return ResponseModel(code=200, message="更新检测参数成功", data=param_dict)


@router.delete("/params/{param_id}", response_model=ResponseModel)
def delete_param(param_id: int):
    """删除检测参数"""
    # 注意：实际项目中需要添加权限验证，仅允许管理员访问
    success, error = DetectionParamService.delete(param_id)
    if error:
        if "不存在" in error:
            return ResponseModel(code=404, message=error, data=None)
        if "关联了" in error:
            return ResponseModel(code=400, message=error, data=None)
        return ResponseModel(code=500, message=error, data=None)
    return ResponseModel(code=200, message="删除检测参数成功", data=None)
