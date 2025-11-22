"""日志配置模块

使用loguru提供结构化日志记录,支持敏感信息脱敏
"""
from loguru import logger
import sys
from pathlib import Path

# 延迟导入避免循环依赖
def _get_log_level():
    try:
        from app.config import settings
        return settings.LOG_LEVEL
    except Exception:
        return "INFO"


# 移除默认处理器
logger.remove()

# 添加控制台处理器
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=_get_log_level(),
    colorize=True
)

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 添加文件处理器(可选)
logger.add(
    "logs/tts_proxy_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="7 days",
    level=_get_log_level(),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    encoding="utf-8"
)


def mask_token(token: str, show_chars: int = 6) -> str:
    """脱敏token
    
    Args:
        token: 原始token
        show_chars: 显示的字符数
        
    Returns:
        脱敏后的token
        
    Examples:
        >>> mask_token("abcdefghijklmnop", 4)
        'abcd...mnop'
    """
    if not token:
        return "***"
    if len(token) <= show_chars:
        return "***"
    return f"{token[:show_chars]}...{token[-show_chars:]}"


# 导出logger
__all__ = ["logger", "mask_token"]