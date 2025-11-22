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


@router.post("/speech")
async def create_speech(
    request: OpenAISpeechRequest,
    _: None = Depends(verify_api_key)
):
    """OpenAI兼容的TTS端点
    
    生成语音音频from输入文本
    
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