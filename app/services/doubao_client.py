"""豆包TTS V3 API客户端模块

封装豆包V3 TTS API的HTTP流式调用
"""
import httpx
import base64
import json
from typing import AsyncIterator, Optional
from app.models.doubao_models import DoubaoV3TTSRequest, DoubaoV3TTSResponse
from app.config import settings
from app.utils.errors import DoubaoAPIError
from app.utils.logger import logger


class DoubaoTTSClient:
    """豆包V3 TTS API客户端
    
    支持HTTP流式调用,逐块解析JSON响应并拼接音频数据
    """
    
    def __init__(self):
        """初始化客户端"""
        self.http_url = settings.DOUBAO_HTTP_URL
        self.ws_url = settings.DOUBAO_WS_URL
        self.timeout = settings.REQUEST_TIMEOUT
        
        # HTTP客户端配置
        self._http_client: Optional[httpx.AsyncClient] = None
    
    @property
    def http_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端(懒加载)"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(
                    max_connections=settings.HTTP_POOL_LIMITS,
                    max_keepalive_connections=20
                )
            )
        return self._http_client
    
    async def synthesize_http(self, request: DoubaoV3TTSRequest) -> bytes:
        """HTTP流式合成
        
        V3 API返回流式JSON响应,需要逐块解析并拼接音频数据
        
        Args:
            request: 豆包V3 TTS请求
            
        Returns:
            完整音频数据(字节流)
            
        Raises:
            DoubaoAPIError: 豆包API调用失败
        """
        # 构建V3请求头
        headers = {
            "X-Api-App-Id": settings.DOUBAO_APPID,
            "X-Api-Access-Key": settings.DOUBAO_ACCESS_TOKEN,
            "X-Api-Resource-Id": settings.DOUBAO_RESOURCE_ID,
            "Content-Type": "application/json"
        }
        
        logger.info(
            f"发起豆包V3 TTS请求: "
            f"speaker={request.req_params.speaker}, "
            f"text_length={len(request.req_params.text)}"
        )
        logger.debug(
            f"请求Headers: X-Api-App-Id={settings.DOUBAO_APPID}, "
            f"X-Api-Resource-Id={settings.DOUBAO_RESOURCE_ID}, "
            f"X-Api-Access-Key={settings.DOUBAO_ACCESS_TOKEN[:10]}..."
        )
        logger.debug(
            f"请求参数: format={request.req_params.audio_params.format}, "
            f"speech_rate={request.req_params.audio_params.speech_rate}"
        )
        logger.debug(f"请求Body: {request.model_dump(exclude_none=True)}")
        
        try:
            # 发起HTTP流式请求
            async with self.http_client.stream(
                "POST",
                self.http_url,
                json=request.model_dump(exclude_none=True),
                headers=headers
            ) as response:
                # 获取并记录logid
                logid = response.headers.get("X-Tt-Logid", "unknown")
                logger.info(
                    f"豆包V3响应: logid={logid}, "
                    f"status={response.status_code}"
                )
                
                # 检查HTTP状态码
                if response.status_code != 200:
                    error_text = await response.aread()
                    try:
                        error_data = json.loads(error_text)
                        error_msg = error_data.get("message", f"HTTP错误: {response.status_code}")
                    except:
                        error_msg = error_text.decode('utf-8', errors='ignore')[:200]
                    logger.error(f"HTTP错误: {response.status_code}, message: {error_msg}")
                    raise DoubaoAPIError(response.status_code, error_msg)
                
                # 流式读取并解析JSON响应
                audio_chunks = []
                buffer = ""
                
                async for chunk in response.aiter_text():
                    buffer += chunk
                    
                    # 尝试解析JSON行
                    while "\n" in buffer or buffer.strip():
                        # 查找完整的JSON行
                        if "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                        else:
                            line = buffer
                            buffer = ""
                        
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            data = json.loads(line)
                            result = DoubaoV3TTSResponse(**data)
                            
                            # 检查错误码
                            if result.code == 0:
                                # 音频数据块
                                if result.data:
                                    audio_bytes = base64.b64decode(result.data)
                                    audio_chunks.append(audio_bytes)
                                    logger.debug(f"收到音频块: {len(audio_bytes)} bytes")
                            elif result.code == 20000000:
                                # 成功结束
                                logger.info("音频合成完成")
                                break
                            else:
                                # 其他错误
                                logger.error(
                                    f"豆包V3 API错误: code={result.code}, "
                                    f"message={result.message}"
                                )
                                raise DoubaoAPIError(result.code, result.message)
                        except json.JSONDecodeError:
                            # 不完整的JSON,放回buffer
                            buffer = line + buffer
                            break
                
                # 拼接所有音频块
                if not audio_chunks:
                    raise DoubaoAPIError(3031, "未返回音频数据")
                
                full_audio = b"".join(audio_chunks)
                logger.info(f"音频合成成功: 总大小={len(full_audio)} bytes, 块数={len(audio_chunks)}")
                
                return full_audio
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP请求失败: {e}")
            raise DoubaoAPIError(3040, f"网络错误: {str(e)}")
    
    async def synthesize_stream(
        self, 
        request: DoubaoV3TTSRequest
    ) -> AsyncIterator[bytes]:
        """WebSocket流式合成
        
        注: 此功能为P1优先级,暂未实现
        
        Args:
            request: 豆包V3 TTS请求
            
        Yields:
            音频数据块
            
        Raises:
            NotImplementedError: 功能未实现
        """
        raise NotImplementedError("WebSocket流式传输暂未实现")
    
    async def close(self):
        """关闭HTTP客户端"""
        if self._http_client is not None:
            await self._http_client.aclose()
            logger.info("豆包HTTP客户端已关闭")


# 全局客户端实例
doubao_client = DoubaoTTSClient()


__all__ = ["DoubaoTTSClient", "doubao_client"]