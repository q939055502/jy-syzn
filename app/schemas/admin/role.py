from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """角色基础模型"""
    role_name: str = Field(..., description="角色名称")
    permissions: List[str] = Field(..., description="权限列表")
    description: Optional[str] = Field(None, description="角色描述")
    parent_id: Optional[int] = Field(None, description="父角色ID")


class RoleCreate(RoleBase):
    """创建角色请求模型"""
    pass


class RoleUpdate(RoleBase):
    """更新角色请求模型"""
    role_name: Optional[str] = Field(None, description="角色名称")
    permissions: Optional[List[str]] = Field(None, description="权限列表")
    description: Optional[str] = Field(None, description="角色描述")
    parent_id: Optional[int] = Field(None, description="父角色ID")


class RoleResponse(RoleBase):
    """角色响应模型"""
    role_id: int = Field(..., description="角色ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
