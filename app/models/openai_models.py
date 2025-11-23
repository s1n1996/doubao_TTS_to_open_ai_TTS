"""OpenAI TTS API 请求/响应模型

定义OpenAI兼容的TTS API数据模型
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Optional


class OpenAISpeechRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model": "gpt-4o-mini-tts",
                "input": "你好,我是豆包语音助手",
                "voice": "alloy",
                "speed": 1.0,
                "response_format": "mp3"
            }
        }
    )
    """OpenAI TTS API 请求模型
    
    完全兼容OpenAI /v1/audio/speech API规范
    """
    
    model: Literal["tts-1", "tts-1-hd", "gpt-4o-mini-tts"] = Field(
        ...,
        description="TTS模型"
    )
    
    input: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="待转换文本"
    )
    
    voice: Literal[
        "alloy", "ash", "ballad", "coral", "echo", 
        "fable", "onyx", "nova", "sage", "shimmer", "verse"
    ] = Field(
        ...,
        description="音色"
    )
    
    response_format: Optional[Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]] = Field(
        default="mp3",
        description="音频格式"
    )
    
    speed: Optional[float] = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="语速(0.25-4.0)"
    )
    
    instructions: Optional[str] = Field(
        default=None,
        description="音色控制指令(暂未实现)"
    )
    
    stream_format: Optional[Literal["sse", "audio"]] = Field(
        default="audio",
        description="流式格式"
    )
    
    @field_validator("input")
    @classmethod
    def validate_input(cls, v: str) -> str:
        """验证输入文本
        
        Args:
            v: 输入文本
            
        Returns:
            验证后的文本
            
        Raises:
            ValueError: 文本为空或过长
        """
        if not v.strip():
            raise ValueError("输入文本不能为空")
        
        # V3 API无文本长度限制,移除1024字节检查
        return v
    


__all__ = ["OpenAISpeechRequest"]