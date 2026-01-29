from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
from app.schemas.detection import (
    DelegationFormTemplateCreate, DelegationFormTemplateUpdate, DelegationFormTemplateResponse,
    ResponseModel, ListResponseModel
)
from app.services.detection import DelegationFormTemplateService
from app.services.detection.utils.file_utils import is_allowed_file
from app.dependencies import get_current_active_user
from app.models.user.user import User

# 创建路由实例
router = APIRouter()


@router.get("/templates", response_model=ListResponseModel[DelegationFormTemplateResponse])
def get_templates(page: int = 1, limit: int = 100, search_keyword: Optional[str] = None, status: Optional[int] = None):
    """获取委托单模板列表，支持分页、搜索和状态筛选"""
    if search_keyword:
        # 执行搜索，同时传递status参数进行过滤
        templates, error = DelegationFormTemplateService.search(search_keyword, status)
    elif status is not None:
        # 按状态获取模板
        templates, error = DelegationFormTemplateService.get_by_status(status)
    else:
        # 获取所有模板
        templates, error = DelegationFormTemplateService.get_all()
    
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    # 处理分页
    start = (page - 1) * limit
    end = start + limit
    paginated_templates = templates[start:end]
    
    return {"data": paginated_templates, "total": len(templates), "message": "获取委托单模板列表成功"}


@router.get("/templates/{template_id}", response_model=ResponseModel[DelegationFormTemplateResponse])
def get_template(template_id: int):
    """获取单个委托单模板"""
    template, error = DelegationFormTemplateService.get_by_id(template_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": template, "message": "获取委托单模板成功"}


@router.post("/templates", response_model=ResponseModel[DelegationFormTemplateResponse], status_code=201)
async def create_template(
    template_name: str = Form(...),
    template_code: str = Form(...),
    status: Optional[int] = Form(1),
    remark: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """创建委托单模板"""
    # 验证文件格式
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="不支持的文件格式，仅允许.doc、.docx、.xls、.xlsx格式")
    
    # 始终从上传文件的文件名中提取文件类型，忽略前端传送过来的文件类型
    from app.services.detection.utils.file_utils import get_file_extension
    file_type = get_file_extension(file.filename)
    
    # 构建模板数据字典
    template_data = {
        "template_name": template_name,
        "template_code": template_code,
        "file_type": file_type,
        "upload_user": current_user.username,  # 使用当前登录用户的用户名
        "status": status,
        "remark": remark
    }
    
    template_obj, error = DelegationFormTemplateService.create(template_data, file)
    if error:
        if "不能为空" in error:
            raise HTTPException(status_code=400, detail=error)
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        if "不能重复" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": template_obj, "message": "创建委托单模板成功", "code": 201}


@router.put("/templates/{template_id}", response_model=ResponseModel[DelegationFormTemplateResponse])
async def update_template(
    template_id: int,
    template_name: Optional[str] = Form(None),
    template_code: Optional[str] = Form(None),
    status: Optional[int] = Form(None),
    remark: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user)
):
    """更新委托单模板"""
    # 验证文件格式（如果有文件上传）
    if file and not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="不支持的文件格式，仅允许.doc、.docx、.xls、.xlsx格式")
    
    # 构建模板数据字典
    template_data = {}
    if template_name is not None:
        template_data["template_name"] = template_name
    if template_code is not None:
        template_data["template_code"] = template_code
    # 总是使用当前登录用户的用户名作为上传人
    template_data["upload_user"] = current_user.username
    if status is not None:
        template_data["status"] = status
    if remark is not None:
        template_data["remark"] = remark
    
    template_obj, error = DelegationFormTemplateService.update(template_id, template_data, file)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        if "不能为空" in error:
            raise HTTPException(status_code=400, detail=error)
        if "不能重复" in error:
            raise HTTPException(status_code=400, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": template_obj, "message": "更新委托单模板成功"}


@router.delete("/templates/{template_id}", response_model=ResponseModel, status_code=200)
def delete_template(template_id: int):
    """删除委托单模板"""
    success, error = DelegationFormTemplateService.delete(template_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"message": "删除委托单模板成功"}


@router.get("/templates/{template_id}/usage", response_model=ResponseModel)
def get_template_usage(template_id: int):
    """获取委托单模板的使用情况"""
    usage_list, error = DelegationFormTemplateService.get_usage_info(template_id)
    if error:
        if "不存在" in error:
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return {"data": usage_list, "message": "获取委托单模板使用情况成功"}
