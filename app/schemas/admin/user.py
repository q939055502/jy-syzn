from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., description="用户名")
    name: str = Field(..., description="真实姓名")


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str = Field(..., description="密码")


class UserUpdate(UserBase):
    """更新用户请求模型"""
    username: Optional[str] = Field(None, description="用户名")
    name: Optional[str] = Field(None, description="真实姓名")
    password: Optional[str] = Field(None, description="密码")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否激活")
    is_admin: bool = Field(..., description="是否管理员")
    is_online: bool = Field(..., description="是否在线")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
