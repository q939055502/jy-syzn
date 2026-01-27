# 链接生成服务
# 用于生成带签名和过期时间的临时下载链接

import os
import hashlib
import hmac
import base64
from urllib.parse import quote, urlencode, urlparse, parse_qs
from datetime import datetime, timedelta
from typing import Dict, Optional


class LinkGeneratorService:
    """链接生成服务，处理所有文件下载链接的生成和验证"""
    
    @staticmethod
    def get_signing_key() -> str:
        """
        获取用于生成签名的密钥
        :return: 签名密钥字符串
        """
        return os.environ.get('SIGNING_KEY', 'default_signing_key_change_in_production')
    
    @staticmethod
    def get_default_expire_seconds() -> int:
        """
        获取默认的链接过期时间（秒）
        :return: 默认过期时间
        """
        return int(os.environ.get('DEFAULT_DOWNLOAD_LINK_EXPIRE', '3600'))
    
    @staticmethod
    def generate_signed_url(file_path: str, expire_seconds: Optional[int] = None, client_ip: Optional[str] = None) -> str:
        """
        生成带签名和过期时间的下载链接
        
        :param file_path: 文件路径，相对于项目根目录
        :param expire_seconds: 链接过期时间（秒），默认使用配置值
        :param client_ip: 可选，限制特定IP访问
        :return: 带签名的下载链接
        """
        # 设置默认过期时间
        if expire_seconds is None:
            expire_seconds = LinkGeneratorService.get_default_expire_seconds()
        
        # 计算过期时间戳
        expire_time = datetime.utcnow() + timedelta(seconds=expire_seconds)
        expire_timestamp = int(expire_time.timestamp())
        
        # 构建签名字符串
        signing_key = LinkGeneratorService.get_signing_key().encode('utf-8')
        
        # 签名内容：file_path + expire_timestamp + client_ip（如果有）
        signature_content = f"{file_path}{expire_timestamp}{client_ip or ''}".encode('utf-8')
        
        # 生成HMAC-SHA256签名
        hmac_signature = hmac.new(signing_key, signature_content, hashlib.sha256).digest()
        
        # Base64编码并URL安全处理
        encoded_signature = base64.urlsafe_b64encode(hmac_signature).decode('utf-8').rstrip('=')
        
        # 从环境变量获取域名或IP配置
        base_url = os.environ.get('BASE_URL', f'http://localhost:{os.environ.get("PORT", "1314")}')
        
        # 构建查询参数，不需要手动quote，urlencode会自动处理
        query_params = {
            'file_path': file_path,
            'expire': str(expire_timestamp),
            'signature': encoded_signature
        }
        
        # 如果提供了客户端IP，添加到查询参数
        if client_ip:
            query_params['ip'] = client_ip
        
        # 构建完整下载链接
        return f"{base_url}/api/public/files/download/signed?{urlencode(query_params)}"
    
    @staticmethod
    def validate_signed_url(params: Dict[str, str], client_ip: Optional[str] = None) -> bool:
        """
        验证链接签名和有效性
        
        :param params: 包含签名信息的查询参数
        :param client_ip: 客户端IP地址，用于验证IP限制
        :return: 验证通过返回True，否则返回False
        """
        # 检查必要参数是否存在
        required_params = ['file_path', 'expire', 'signature']
        for param in required_params:
            if param not in params:
                return False
        
        try:
            # 解析参数
            # 注意：file_path不需要解码，因为FastAPI会自动处理查询参数的解码
            file_path = params['file_path']
            expire_timestamp = int(params['expire'])
            signature = params['signature']
            expected_ip = params.get('ip')
            
            # 检查IP限制
            if expected_ip and client_ip and expected_ip != client_ip:
                return False
            
            # 检查是否过期
            current_timestamp = int(datetime.utcnow().timestamp())
            if current_timestamp > expire_timestamp:
                return False
            
            # 重新生成签名并验证
            signing_key = LinkGeneratorService.get_signing_key().encode('utf-8')
            # 签名时使用原始file_path（未解码），因为生成签名时也是使用原始file_path
            signature_content = f"{file_path}{expire_timestamp}{expected_ip or ''}".encode('utf-8')
            
            expected_signature = hmac.new(signing_key, signature_content, hashlib.sha256).digest()
            expected_encoded_signature = base64.urlsafe_b64encode(expected_signature).decode('utf-8').rstrip('=')
            
            # 使用时间安全比较
            return hmac.compare_digest(signature, expected_encoded_signature)
            
        except Exception as e:
            # 任何异常都视为验证失败
            return False