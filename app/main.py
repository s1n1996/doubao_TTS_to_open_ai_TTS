"""TTS Proxy - FastAPI主应用

豆包TTS转OpenAI兼容API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes.audio import router as audio_router
from app.services.doubao_client import doubao_client
from app.config import settings
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    logger.info("=" * 50)
    logger.info("TTS Proxy 启动中...")
    logger.info(f"服务地址: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    logger.info(f"日志级别: {settings.LOG_LEVEL}")
    logger.info(f"API文档: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/docs")
    logger.info("=" * 50)
    
    yield
    
    logger.info("TTS Proxy 关闭中...")
    await doubao_client.close()
    logger.info("TTS Proxy 已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="TTS Proxy",
    description="豆包TTS转OpenAI兼容API - 将豆包TTS服务转换为OpenAI TTS API格式",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(audio_router)


@app.get("/health", tags=["System"])
async def health_check():
    """健康检查端点
    
    Returns:
        服务健康状态
    """
    return {
        "status": "healthy",
        "service": "TTS Proxy",
        "version": "1.0.0"
    }


@app.get("/", tags=["System"])
async def root():
    """根路径
    
    Returns:
        服务基本信息
    """
    return {
        "message": "TTS Proxy - 豆包TTS转OpenAI兼容API",
        "docs": "/docs",
        "health": "/health",
        "api": "/v1/audio/speech"
    }


# 用于直接运行的入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )