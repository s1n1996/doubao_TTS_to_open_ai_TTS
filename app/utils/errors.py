"""错误处理模块

定义自定义异常类和错误响应格式化
"""
from typing import Optional


class TTSProxyError(Exception):
    """TTS Proxy基础异常类"""
    
    def __init__(
        self, 
        message: str, 
        error_type: str = "api_error", 
        status_code: int = 500
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        super().__init__(message)


class DoubaoAPIError(TTSProxyError):
    """豆包API错误"""
    
    def __init__(self, code: int, message: str):
        self.doubao_code = code
        status_code, error_type = self._map_doubao_error(code)
        super().__init__(message, error_type, status_code)
    
    @staticmethod
    def _map_doubao_error(code: int) -> tuple[int, str]:
        """映射豆包错误码到HTTP状态码和错误类型
        
        Args:
            code: 豆包错误码
            
        Returns:
            (HTTP状态码, 错误类型)
        """
        mapping = {
            3000: (200, "success"),  # 成功
            3001: (400, "invalid_request_error"),  # 无效请求
            3003: (429, "rate_limit_error"),  # 并发超限
            3005: (503, "service_unavailable"),  # 服务忙
            3006: (400, "invalid_request_error"),  # 服务中断
            3010: (400, "invalid_request_error"),  # 文本超长
            3011: (400, "invalid_request_error"),  # 无效文本
            3030: (504, "timeout_error"),  # 处理超时
            3031: (500, "api_error"),  # 处理错误
            3032: (504, "timeout_error"),  # 等待超时
            3040: (500, "api_error"),  # 连接错误
            3050: (400, "invalid_request_error"),  # 音色不存在
        }
        return mapping.get(code, (500, "api_error"))


def format_error_response(
    error: TTSProxyError, 
    param: Optional[str] = None
) -> dict:
    """格式化为OpenAI兼容的错误响应
    
    Args:
        error: 错误对象
        param: 错误相关的参数名
        
    Returns:
        OpenAI格式的错误响应
        
    Examples:
        >>> err = DoubaoAPIError(3001, "参数错误")
        >>> format_error_response(err, "voice")
        {
            "error": {
                "message": "参数错误",
                "type": "invalid_request_error",
                "param": "voice",
                "code": "doubao_3001"
            }
        }
    """
    return {
        "error": {
            "message": error.message,
            "type": error.error_type,
            "param": param,
            "code": f"doubao_{getattr(error, 'doubao_code', 'unknown')}"
        }
    }


__all__ = [
    "TTSProxyError",
    "DoubaoAPIError", 
    "format_error_response"
]