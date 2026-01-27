from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PermissionBase(BaseModel):
    """权限基础模型"""
    code: str = Field(..., description="权限代码")
    resource: str = Field(..., description="资源名称")
    action: str = Field(..., description="操作类型")
    scope: str = Field(default="all", description="权限范围")
    description: Optional[str] = Field(None, description="权限描述")


class PermissionCreate(PermissionBase):
    """创建权限请求模型"""
    pass


class PermissionUpdate(PermissionBase):
    """更新权限请求模型"""
    code: Optional[str] = Field(None, description="权限代码")
    resource: Optional[str] = Field(None, description="资源名称")
    action: Optional[str] = Field(None, description="操作类型")
    scope: Optional[str] = Field(None, description="权限范围")
    is_active: Optional[bool] = Field(None, description="是否激活")


class PermissionResponse(PermissionBase):
    """权限响应模型"""
    id: int = Field(..., description="权限ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
