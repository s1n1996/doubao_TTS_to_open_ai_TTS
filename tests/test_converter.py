"""参数转换器测试模块"""
import pytest
import sys
import os

# 设置环境变量供测试使用
os.environ["DOUBAO_APPID"] = "test_appid"
os.environ["DOUBAO_ACCESS_TOKEN"] = "test_token"

from app.services.converter import ParameterConverter, converter
from app.models.openai_models import OpenAISpeechRequest


class TestParameterConverter:
    """参数转换器测试类"""
    
    def setup_method(self):
        """测试初始化"""
        self.converter = ParameterConverter()
    
    def test_voice_mapping_alloy(self):
        """测试alloy音色映射"""
        result = self.converter.map_voice("alloy")
        assert result == "zh_female_cancan_mars_bigtts"
    
    def test_voice_mapping_echo(self):
        """测试echo音色映射"""
        result = self.converter.map_voice("echo")
        assert result == "zh_male_M359_conversation_wvae_bigtts"
    
    def test_voice_mapping_unknown(self):
        """测试未知音色映射到默认值"""
        result = self.converter.map_voice("unknown")
        assert result == "zh_female_cancan_mars_bigtts"  # 默认为alloy
    
    def test_speed_mapping_normal(self):
        """测试正常语速映射"""
        assert self.converter.map_speed(1.0) == 1.0
        assert self.converter.map_speed(0.5) == 0.5
        assert self.converter.map_speed(1.5) == 1.5
    
    def test_speed_mapping_exceed_max(self):
        """测试超过最大值的语速映射"""
        assert self.converter.map_speed(3.0) == 2.0  # 限制为2.0
        assert self.converter.map_speed(4.0) == 2.0
    
    def test_speed_mapping_below_min(self):
        """测试低于最小值的语速映射"""
        assert self.converter.map_speed(0.05) == 0.1  # 限制为0.1
    
    def test_format_mapping(self):
        """测试格式映射"""
        assert self.converter.map_format("mp3") == "mp3"
        assert self.converter.map_format("opus") == "ogg_opus"
        assert self.converter.map_format("wav") == "wav"
        assert self.converter.map_format("unknown") == "mp3"  # 默认mp3
    
    def test_content_type(self):
        """测试Content-Type获取"""
        assert self.converter.get_content_type("mp3") == "audio/mpeg"
        assert self.converter.get_content_type("wav") == "audio/wav"
        assert self.converter.get_content_type("unknown") == "audio/mpeg"
    
    def test_full_conversion(self):
        """测试完整请求转换"""
        openai_req = OpenAISpeechRequest(
            model="gpt-4o-mini-tts",
            input="测试文本",
            voice="alloy",
            speed=1.5,
            response_format="mp3"
        )
        
        doubao_req = self.converter.convert(openai_req)
        
        assert doubao_req.request.text == "测试文本"
        assert doubao_req.audio.voice_type == "zh_female_cancan_mars_bigtts"
        assert doubao_req.audio.speed_ratio == 1.5
        assert doubao_req.audio.encoding == "mp3"
        assert doubao_req.app.appid == "test_appid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])