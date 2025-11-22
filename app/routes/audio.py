"""音频API路由模块

实现OpenAI兼容的/v1/audio/speech端点
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models.openai_models import OpenAISpeechRequest
from app.services.converter import converter
from app.services.doubao_client import doubao_client
from app.utils.errors import TTSProxyError, format_error_response
from app.utils.logger import logger
from app.middleware.auth import verify_api_key

router = APIRouter(prefix="/v1/audio", tags=["Audio"])


@router.post(
    "/speech",
    summary="生成语音",
    description="将文本转换为语音音频,完全兼容OpenAI TTS API格式",
    response_description="音频文件流",
    responses={
        200: {
            "description": "成功生成音频",
            "content": {
                "audio/mpeg": {},
                "audio/opus": {},
                "audio/aac": {},
                "audio/flac": {},
                "audio/wav": {},
                "audio/pcm": {}
            }
        },
        401: {
            "description": "认证失败",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "无效的API密钥",
                            "type": "authentication_error",
                            "code": "invalid_api_key"
                        }
                    }
                }
            }
        },
        400: {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "输入文本不能为空",
                            "type": "invalid_request_error",
                            "code": "validation_error"
                        }
                    }
                }
            }
        }
    }
)
async def create_speech(
    request: OpenAISpeechRequest,
    _: None = Depends(verify_api_key)
):
    """OpenAI兼容的TTS端点
    
    将输入文本转换为语音音频,支持多种音色、语速和音频格式。
    
    ## 认证
    
    如果启用了API密钥认证(`ENABLE_API_KEY_AUTH=true`),需要在请求头中提供Bearer token:
    
    ```
    Authorization: Bearer your-api-key
    ```
    
    ## 参数说明
    
    - **model**: TTS模型,支持 `tts-1`, `tts-1-hd`, `gpt-4o-mini-tts`
    - **input**: 待转换的文本(1-4096字符)
    - **voice**: 音色选择,支持11种音色:
      - `alloy` - 中性音色
      - `ash` - 男声
      - `ballad` - 女声(双快思思)
      - `coral` - 女声(甜美)
      - `echo` - 男声
      - `fable` - 女声(清新)
      - `onyx` - 男声(温暖)
      - `nova` - 女声(毛毛)
      - `sage` - 男声(广西)
      - `shimmer` - 女声(悦文)
      - `verse` - 男声(说唱)
    - **response_format**: 音频格式,支持 `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (默认: mp3)
    - **speed**: 语速倍率,范围 0.25-4.0 (默认: 1.0)
    
    ## 示例
    
    ```bash
    curl -X POST http://localhost:9001/v1/audio/speech \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer your-api-key" \\
      -d '{
        "model": "gpt-4o-mini-tts",
        "input": "你好,欢迎使用豆包TTS服务",
        "voice": "alloy",
        "speed": 1.0,
        "response_format": "mp3"
      }' \\
      --output speech.mp3
    ```
    
    Args:
        request: OpenAI格式的TTS请求
        
    Returns:
        StreamingResponse: 音频流响应
        
    Raises:
        HTTPException: 处理失败时抛出HTTP异常
    """
    try:
        logger.info(
            f"收到TTS请求: model={request.model}, "
            f"voice={request.voice}, "
            f"text_length={len(request.input)}, "
            f"format={request.response_format}"
        )
        
        # 1. 转换参数
        doubao_request = converter.convert(request)
        
        # 2. 调用豆包API
        audio_data = await doubao_client.synthesize_http(doubao_request)
        
        # 3. 确定Content-Type
        content_type = converter.get_content_type(
            request.response_format or "mp3"
        )
        
        # 4. 返回音频流
        return StreamingResponse(
            iter([audio_data]),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="speech.{request.response_format or "mp3"}"'
            }
        )
        
    except TTSProxyError as e:
        logger.error(f"TTS处理失败: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=format_error_response(e)
        )
    except Exception as e:
        logger.exception(f"未知错误: {e}")
        error = TTSProxyError(str(e), "internal_error", 500)
        raise HTTPException(
            status_code=500,
            detail=format_error_response(error)
        )


__all__ = ["router"]