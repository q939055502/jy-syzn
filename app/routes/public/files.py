from fastapi import APIRouter, HTTPException, Response, Request
from pathlib import Path
import os
from app.services.utils.link_generator import LinkGeneratorService

# 创建路由实例
router = APIRouter(prefix="/files", tags=["public/files"])

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# 允许下载的文件路径前缀列表
ALLOWED_PREFIXES = [
    Path("static"),
    Path("upload"),
    Path("files")
]


def validate_file_path(file_path: str) -> bool:
    """
    验证文件路径是否安全，防止目录遍历攻击
    :param file_path: 要验证的文件路径（字符串格式）
    :return: 安全返回True，否则返回False
    """
    try:
        # 移除file_path开头的斜杠，确保Path对象能正确构建路径
        normalized_file_path = file_path.lstrip('/')
        
        # 直接构建绝对路径，避免Path对象的编码问题
        abs_file_path = (PROJECT_ROOT / normalized_file_path).resolve()
        
        # 检查文件是否存在
        if not abs_file_path.exists() or not abs_file_path.is_file():
            return False
        
        # 检查文件是否在允许的前缀目录下
        for allowed_prefix in ALLOWED_PREFIXES:
            allowed_abs_path = (PROJECT_ROOT / allowed_prefix).resolve()
            if abs_file_path.is_relative_to(allowed_abs_path):
                return True
        
        return False
    except Exception as e:
        # 如果路径处理出错，返回False
        return False


def return_file_response(file_path: str) -> Response:
    """
    返回文件响应，共用的文件读取和响应生成逻辑
    :param file_path: 文件路径，相对于项目根目录
    :return: 文件响应
    """
    try:
        # 直接使用相对路径构建绝对路径，不通过Path对象
        import os
        
        # 移除file_path开头的斜杠，确保os.path.join能正确构建路径
        normalized_file_path = file_path.lstrip('/')
        abs_file_path_str = os.path.join(PROJECT_ROOT, normalized_file_path)
        
        # 验证文件是否存在
        if not os.path.exists(abs_file_path_str) or not os.path.isfile(abs_file_path_str):
            raise HTTPException(status_code=404, detail="文件不存在或无权访问")
        
        # 检查文件是否在允许的前缀目录下
        allowed = False
        for prefix in ALLOWED_PREFIXES:
            prefix_path = os.path.join(PROJECT_ROOT, str(prefix))
            if abs_file_path_str.startswith(prefix_path):
                allowed = True
                break
        if not allowed:
            raise HTTPException(status_code=404, detail="文件不存在或无权访问")
        
        # 获取文件扩展名，用于设置Content-Type
        _, file_ext = os.path.splitext(abs_file_path_str)
        file_ext = file_ext.lower()
        
        # 设置默认的Content-Type
        content_type = "application/octet-stream"
        
        # 根据文件扩展名设置合适的Content-Type
        if file_ext in [".txt", ".log"]:
            content_type = "text/plain"
        elif file_ext in [".csv"]:
            content_type = "text/csv"
        elif file_ext in [".pdf"]:
            content_type = "application/pdf"
        elif file_ext in [".doc", ".docx"]:
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_ext in [".xls", ".xlsx"]:
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_ext in [".png"]:
            content_type = "image/png"
        elif file_ext in [".jpg", ".jpeg"]:
            content_type = "image/jpeg"
        elif file_ext in [".gif"]:
            content_type = "image/gif"
        elif file_ext in [".json"]:
            content_type = "application/json"
        elif file_ext in [".xml"]:
            content_type = "application/xml"
        
        # 返回文件响应，使用FileResponse可以自动处理编码问题
        from fastapi.responses import FileResponse
        return FileResponse(
            path=abs_file_path_str,
            media_type=content_type,
            filename=os.path.basename(abs_file_path_str)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")


@router.get("/download/signed")
async def download_signed_file(request: Request):
    """
    带签名的公开文件下载接口
    :param request: 请求对象，用于获取查询参数和客户端IP
    :return: 文件响应
    """
    try:
        # 获取查询参数
        query_params = dict(request.query_params)
        
        # 获取客户端IP
        client_ip = request.client.host
        
        # 保存原始file_path用于签名验证
        original_file_path = query_params.get("file_path")
        
        # 验证签名
        if not LinkGeneratorService.validate_signed_url(query_params, client_ip):
            raise HTTPException(status_code=403, detail="无效的下载链接或链接已过期")
        
        # 获取文件路径
        if not original_file_path:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 返回文件响应
        return return_file_response(original_file_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")
