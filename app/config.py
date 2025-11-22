"""配置管理模块

使用pydantic-settings从环境变量加载配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # ============================================
    # 豆包TTS配置 (必填)
    # ============================================
    DOUBAO_APPID: str
    DOUBAO_ACCESS_TOKEN: str
    # V3 API配置
    DOUBAO_RESOURCE_ID: str = "seed-tts-2.0"  # 资源ID: seed-tts-1.0, seed-tts-2.0等
    DOUBAO_HTTP_URL: str = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
    DOUBAO_WS_URL: str = "wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream"
    
    # ============================================
    # 服务配置 (可选)
    # ============================================
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 9001
    LOG_LEVEL: str = "INFO"
    
    # ============================================
    # 性能配置 (可选)
    # ============================================
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    HTTP_POOL_LIMITS: int = 100
    
    # ============================================
    # 高级配置 (可选)
    # ============================================
    ENABLE_REQUEST_LOGGING: bool = True
    ENABLE_DETAILED_ERRORS: bool = True
    DEFAULT_SAMPLE_RATE: int = 24000
    DEFAULT_BITRATE: int = 160
    
    # ============================================
    # 音色映射配置 (可选)
    # ============================================
    # 格式: VOICE_MAPPING_<OPENAI_VOICE>=豆包音色ID
    # 例如: VOICE_MAPPING_ALLOY=zh_female_cancan_mars_bigtts
    VOICE_MAPPING_ALLOY: Optional[str] = None
    VOICE_MAPPING_ASH: Optional[str] = None
    VOICE_MAPPING_BALLAD: Optional[str] = None
    VOICE_MAPPING_CORAL: Optional[str] = None
    VOICE_MAPPING_ECHO: Optional[str] = None
    VOICE_MAPPING_FABLE: Optional[str] = None
    VOICE_MAPPING_ONYX: Optional[str] = None
    VOICE_MAPPING_NOVA: Optional[str] = None
    VOICE_MAPPING_SAGE: Optional[str] = None
    VOICE_MAPPING_SHIMMER: Optional[str] = None
    VOICE_MAPPING_VERSE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
settings = Settings()