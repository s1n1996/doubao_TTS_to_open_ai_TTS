"""API密钥认证中间件

实现基于Bearer Token的API密钥认证
"""
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.utils.logger import logger

# 定义HTTPBearer安全方案
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(security)
) -> None:
    """验证API密钥
    
    Args:
        credentials: HTTP Authorization凭证
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    # 如果未启用API密钥认证,直接放行
    if not settings.ENABLE_API_KEY_AUTH:
        return
    
    # 获取配置的API密钥集合
    valid_keys = settings.get_api_keys()
    
    # 如果启用了认证但未配置任何密钥,拒绝所有请求
    if not valid_keys:
        logger.warning("API密钥认证已启用但未配置任何密钥")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "API密钥认证已启用但服务器未正确配置",
                    "type": "authentication_error",
                    "code": "server_misconfigured"
                }
            }
        )
    
    # 检查是否提供了凭证
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "缺少API密钥。请在Authorization header中提供Bearer token",
                    "type": "authentication_error",
                    "code": "missing_api_key"
                }
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 验证密钥
    provided_key = credentials.credentials
    if provided_key not in valid_keys:
        logger.warning(f"无效的API密钥: {provided_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "无效的API密钥",
                    "type": "authentication_error",
                    "code": "invalid_api_key"
                }
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    logger.debug(f"API密钥验证成功: {provided_key[:10]}...")


__all__ = ["verify_api_key"]