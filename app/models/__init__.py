"""数据模型模块"""
from app.models.openai_models import OpenAISpeechRequest
from app.models.doubao_models import (
    DoubaoV3User,
    DoubaoV3AudioParams,
    DoubaoV3ReqParams,
    DoubaoV3TTSRequest,
    DoubaoV3TTSResponse
)

__all__ = [
    "OpenAISpeechRequest",
    "DoubaoV3User",
    "DoubaoV3AudioParams",
    "DoubaoV3ReqParams",
    "DoubaoV3TTSRequest",
    "DoubaoV3TTSResponse"
]