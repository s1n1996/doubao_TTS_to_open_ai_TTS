"""参数转换器模块

将OpenAI TTS API参数转换为豆包V3 TTS API参数
"""
from typing import Dict
from app.models.openai_models import OpenAISpeechRequest
from app.models.doubao_models import (
    DoubaoV3User,
    DoubaoV3AudioParams,
    DoubaoV3ReqParams,
    DoubaoV3TTSRequest
)
from app.config import settings


class ParameterConverter:
    """OpenAI参数到豆包V3参数的转换器"""
    
    # 默认音色映射表: OpenAI voice -> 豆包 speaker
    DEFAULT_VOICE_MAPPING: Dict[str, str] = {
        "alloy": "zh_female_cancan_mars_bigtts",
        "ash": "zh_male_M392_conversation_wvae_bigtts",
        "ballad": "zh_female_shuangkuaisisi_moon_bigtts",
        "coral": "zh_female_tianmei_mars_bigtts",
        "echo": "zh_male_M359_conversation_wvae_bigtts",
        "fable": "zh_female_qingxin_mars_bigtts",
        "onyx": "zh_male_wennuanahu_moon_bigtts",
        "nova": "zh_female_maomao_mars_bigtts",
        "sage": "zh_male_guangxi_mars_bigtts",
        "shimmer": "zh_female_yuewen_mars_bigtts",
        "verse": "zh_male_rap_mars_bigtts",
    }
    
    def __init__(self):
        """初始化转换器,加载配置的音色映射"""
        self.voice_mapping = self._load_voice_mapping()
    
    def _load_voice_mapping(self) -> Dict[str, str]:
        """从配置加载音色映射,未配置的使用默认值
        
        Returns:
            音色映射字典
        """
        mapping = self.DEFAULT_VOICE_MAPPING.copy()
        
        # 从settings读取用户配置的音色映射
        voice_config = {
            "alloy": settings.VOICE_MAPPING_ALLOY,
            "ash": settings.VOICE_MAPPING_ASH,
            "ballad": settings.VOICE_MAPPING_BALLAD,
            "coral": settings.VOICE_MAPPING_CORAL,
            "echo": settings.VOICE_MAPPING_ECHO,
            "fable": settings.VOICE_MAPPING_FABLE,
            "onyx": settings.VOICE_MAPPING_ONYX,
            "nova": settings.VOICE_MAPPING_NOVA,
            "sage": settings.VOICE_MAPPING_SAGE,
            "shimmer": settings.VOICE_MAPPING_SHIMMER,
            "verse": settings.VOICE_MAPPING_VERSE,
        }
        
        # 用户配置覆盖默认值
        for voice_name, custom_speaker in voice_config.items():
            if custom_speaker:  # 只有当用户配置了才覆盖
                mapping[voice_name] = custom_speaker
        
        return mapping
    
    # 格式映射表: OpenAI format -> 豆包V3 format
    FORMAT_MAPPING: Dict[str, str] = {
        "mp3": "mp3",
        "opus": "ogg_opus",
        "aac": "aac",
        "flac": "flac",
        "wav": "wav",
        "pcm": "pcm",
    }
    
    def convert(self, openai_req: OpenAISpeechRequest) -> DoubaoV3TTSRequest:
        """转换OpenAI请求为豆包V3请求
        
        Args:
            openai_req: OpenAI格式的请求
            
        Returns:
            豆包V3格式的请求
        """
        return DoubaoV3TTSRequest(
            user=DoubaoV3User(),
            req_params=DoubaoV3ReqParams(
                text=openai_req.input,
                speaker=self.map_voice(openai_req.voice),
                audio_params=DoubaoV3AudioParams(
                    format=self.map_format(openai_req.response_format or "mp3"),
                    sample_rate=settings.DEFAULT_SAMPLE_RATE,
                    bit_rate=settings.DEFAULT_BITRATE if (openai_req.response_format or "mp3") == "mp3" else None,
                    speech_rate=self.map_speed_to_v3(openai_req.speed or 1.0)
                )
            )
        )
    
    def map_voice(self, openai_voice: str) -> str:
        """映射音色
        
        支持从.env配置自定义映射,未配置的使用默认值
        
        Args:
            openai_voice: OpenAI音色名称
            
        Returns:
            豆包音色ID
        """
        return self.voice_mapping.get(
            openai_voice,
            self.voice_mapping.get("alloy", "zh_female_cancan_mars_bigtts")  # 默认音色
        )
    
    def map_format(self, openai_format: str) -> str:
        """映射音频格式
        
        Args:
            openai_format: OpenAI格式名称
            
        Returns:
            豆包V3编码格式
        """
        return self.FORMAT_MAPPING.get(openai_format, "mp3")
    
    def map_speed_to_v3(self, openai_speed: float) -> int:
        """映射语速到V3格式
        
        OpenAI语速范围: 0.25-4.0 (1.0为正常)
        豆包V3语速范围: -50~100 (0为正常)
        
        转换公式: v3_speed = (openai_speed - 1.0) * 100
        - 1.0 → 0 (正常)
        - 2.0 → 100 (2倍速)
        - 0.5 → -50 (0.5倍速)
        
        Args:
            openai_speed: OpenAI语速值
            
        Returns:
            豆包V3语速值(限制在-50~100范围内)
        """
        v3_speed = int((openai_speed - 1.0) * 100)
        
        # 限制范围
        if v3_speed > 100:
            return 100
        if v3_speed < -50:
            return -50
        return v3_speed
    
    def get_content_type(self, response_format: str) -> str:
        """获取响应的Content-Type
        
        Args:
            response_format: 音频格式
            
        Returns:
            MIME类型
        """
        content_types = {
            "mp3": "audio/mpeg",
            "opus": "audio/opus",
            "aac": "audio/aac",
            "flac": "audio/flac",
            "wav": "audio/wav",
            "pcm": "audio/pcm"
        }
        return content_types.get(response_format, "audio/mpeg")


# 全局转换器实例
converter = ParameterConverter()


__all__ = ["ParameterConverter", "converter"]