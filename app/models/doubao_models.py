"""豆包TTS V3 API 请求/响应模型

定义豆包V3 API的数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional

class DoubaoV3User(BaseModel):
    """V3用户信息"""
    uid: str = Field(default="default_user", description="用户ID")


class DoubaoV3AudioParams(BaseModel):
    """V3音频参数"""
    format: str = Field(default="mp3", description="音频格式: mp3/ogg_opus/pcm等")
    sample_rate: int = Field(default=24000, description="采样率")
    bit_rate: Optional[int] = Field(default=None, description="比特率(仅MP3)")
    speech_rate: int = Field(default=0, description="语速[-50,100], 0为正常, 100为2.0倍速, -50为0.5倍速")
    loudness_rate: Optional[int] = Field(default=None, description="音量[-50,100]")
    emotion: Optional[str] = Field(default=None, description="情感")
    emotion_scale: Optional[int] = Field(default=None, description="情绪值[1-5]")


class DoubaoV3ReqParams(BaseModel):
    """V3请求参数"""
    text: str = Field(..., description="待合成文本")
    speaker: str = Field(..., description="音色ID")
    audio_params: DoubaoV3AudioParams = Field(..., description="音频参数")
    model: Optional[str] = Field(default=None, description="模型版本,如seed-tts-1.1")


class DoubaoV3TTSRequest(BaseModel):
    """豆包V3 TTS完整请求"""
    user: DoubaoV3User
    req_params: DoubaoV3ReqParams


class DoubaoV3TTSResponse(BaseModel):
    """豆包V3 TTS响应
    
    V3返回流式JSON块:
    - 音频块: {"code": 0, "message": "", "data": "base64音频"}
    - 结束块: {"code": 20000000, "message": "ok", "data": null}
    """
    code: int = Field(..., description="状态码: 0=数据块, 20000000=结束")
    message: str = Field(..., description="状态消息")
    data: Optional[str] = Field(default=None, description="base64音频数据")
    sentence: Optional[dict] = Field(default=None, description="时间戳数据(可选)")


__all__ = [
    "DoubaoV3User",
    "DoubaoV3AudioParams",
    "DoubaoV3ReqParams",
    "DoubaoV3TTSRequest",
    "DoubaoV3TTSResponse"
]