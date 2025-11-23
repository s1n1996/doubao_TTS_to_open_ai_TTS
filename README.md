# Doubao TTS to OpenAI TTS Proxy

> 将火山引擎豆包 V3 语音合成能力包装成 **OpenAI 兼容** 的 `/v1/audio/speech` 端点，方便无缝迁移现有客户端。

## 1. 项目概述

### 项目名称与描述
- **项目名称**：doubao_TTS_to_open_ai_TTS（简称 *TTS Proxy*）。
- **定位**：一个基于 FastAPI 的轻量级代理服务，将 OpenAI 风格的 TTS 请求实时转换为豆包 V3 API 参数并返回流式音频。

### 核心功能
- 提供 OpenAI 兼容的 `/v1/audio/speech` POST 接口。
- 自动完成 **参数校验 → 映射转换 → Doubao API 调用 → 音频流返回** 全链路处理。
- 支持 MP3/OPUS/AAC/FLAC/WAV/PCM 多种格式及语速调节。
- 可选 Bearer Token 身份认证、详细日志与错误映射。

### 使用场景与优势
- **平滑迁移**：已有接入 OpenAI TTS 的应用，只需替换基础 URL 即可。
- **成本控制**：沿用 OpenAI 协议但底层使用豆包，降低推理成本。
- **自建安全合规**：部署在私有环境，自行控制 API key、日志与访问策略。

---

## 2. 技术栈
- **语言/运行时**：Python 3.13
- **Web 框架**：FastAPI + Uvicorn
- **网络客户端**：httpx（异步流式请求）
- **配置与数据模型**：pydantic / pydantic-settings
- **日志系统**：loguru

### 架构速览
```
Client (OpenAI-style request)
      │
      ▼
FastAPI Router (/v1/audio/speech)
      │  验证、记录
      ▼
ParameterConverter  ──▶  DoubaoV3TTSRequest
      │
      ▼
DoubaoTTSClient (httpx stream, base64 decode)
      │
      ▼
StreamingResponse → Client (audio bytes)
```
- **ParameterConverter**：完成模型、音色、语速、格式映射。
- **DoubaoTTSClient**：封装 Doubao V3 HTTP 流式协议，拼接音频块。
- **Middleware/Auth**：可选的 Bearer Token 校验。
- **Utils**：统一日志、错误码与 OpenAI 兼容响应。

---

## 3. 前置要求
1. **Python**：3.13 及以上版本。
2. **系统依赖**：建议使用 Linux / macOS；Windows 亦可，但需确保 `uvicorn`, `httpx`, `openssl` 等依赖可用。
3. **必需凭证**（来自火山引擎豆包/声音复刻控制台）：
   - `DOUBAO_APPID`
   - `DOUBAO_ACCESS_TOKEN`
   - 可选 `DOUBAO_RESOURCE_ID`（默认 `seed-tts-2.0`）。
4. **网络**：服务器需能访问 `openspeech.bytedance.com`。

---

## 4. 安装指南
```bash
# 1. 克隆仓库
git clone <your-fork-or-original-repo> doubao-tts-proxy
cd doubao-tts-proxy

# 2. 使用uv虚拟环境
uv sync

# 3. 配置环境变量(必要)
cp .env.example .env
# 根据实际凭证修改 .env
```
---

## 5. 配置说明
项目使用 `pydantic-settings` 从 `.env` 及系统环境变量读取配置。

### 5.1 环境变量速查表
| 变量                      | 描述                               | 必填 | 默认值                                                            |
| ------------------------- | ---------------------------------- | ---- | ----------------------------------------------------------------- |
| `DOUBAO_APPID`            | 豆包应用 ID                        | ✅    | -                                                                 |
| `DOUBAO_ACCESS_TOKEN`     | 豆包访问令牌                       | ✅    | -                                                                 |
| `DOUBAO_RESOURCE_ID`      | V3 资源/模型 ID                    | ⭕    | `seed-tts-2.0`                                                    |
| `DOUBAO_HTTP_URL`         | 豆包 HTTP 流式端点                 | ⭕    | `https://openspeech.bytedance.com/api/v3/tts/unidirectional`      |
| `DOUBAO_WS_URL`           | 豆包 WebSocket 端点（预留）        | ⭕    | `wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream` |
| `SERVER_HOST`             | 服务监听地址                       | ⭕    | `0.0.0.0`                                                         |
| `SERVER_PORT`             | 服务端口                           | ⭕    | `9001`                                                            |
| `LOG_LEVEL`               | 日志级别 (`DEBUG/INFO/...`)        | ⭕    | `INFO`                                                            |
| `MAX_CONCURRENT_REQUESTS` | 最大并发（预留）                   | ⭕    | `10`                                                              |
| `REQUEST_TIMEOUT`         | Doubao HTTP 超时时间（秒）         | ⭕    | `30`                                                              |
| `HTTP_POOL_LIMITS`        | httpx 最大连接数                   | ⭕    | `100`                                                             |
| `ENABLE_REQUEST_LOGGING`  | 是否记录详细请求                   | ⭕    | `true`                                                            |
| `ENABLE_DETAILED_ERRORS`  | 是否暴露详细错误                   | ⭕    | `true`                                                            |
| `DEFAULT_SAMPLE_RATE`     | 默认采样率                         | ⭕    | `24000`                                                           |
| `DEFAULT_BITRATE`         | MP3 比特率 (kbps)                  | ⭕    | `160`                                                             |
| `ENABLE_API_KEY_AUTH`     | 开启 Bearer Token 认证             | ⭕    | `false`                                                           |
| `API_KEYS`                | 逗号分隔的 API key 列表            | ⭕    | `None`                                                            |
| `VOICE_MAPPING_*`         | 自定义 OpenAI voice → 豆包 speaker | ⭕    | `None`（使用默认映射）                                            |

### 5.2 声音映射（默认值）
| OpenAI Voice | Doubao Speaker ID                       | 描述             |
| ------------ | --------------------------------------- | ---------------- |
| `alloy`      | `zh_female_cancan_mars_bigtts`          | 中性女声         |
| `ash`        | `zh_male_M392_conversation_wvae_bigtts` | 男声             |
| `ballad`     | `zh_female_shuangkuaisisi_moon_bigtts`  | 女声（双快思思） |
| `coral`      | `zh_female_tianmei_mars_bigtts`         | 甜美女声         |
| `echo`       | `zh_male_M359_conversation_wvae_bigtts` | 男声             |
| `fable`      | `zh_female_qingxin_mars_bigtts`         | 清新女声         |
| `onyx`       | `zh_male_wennuanahu_moon_bigtts`        | 温暖男声         |
| `nova`       | `zh_female_maomao_mars_bigtts`          | 毛毛女声         |
| `sage`       | `zh_male_guangxi_mars_bigtts`           | 广西男声         |
| `shimmer`    | `zh_female_yuewen_mars_bigtts`          | 悦文女声         |
| `verse`      | `zh_male_rap_mars_bigtts`               | 说唱男声         |
> 在 `.env` 中设置 `VOICE_MAPPING_<VOICE>=your_speaker_id` 可覆盖默认值。更多的音色选择可在官方文档和火山引擎的控制台中选查看

### 5.3 API Key 认证
用户可以开启权限认证服务（默认关闭），流程如下：
1. 设置 `ENABLE_API_KEY_AUTH=true`。
2. 指定 `API_KEYS=sk-foo,sk-bar`。
3. 客户端请求需携带 `Authorization: Bearer sk-foo`。
> 若部署在云端建议开启该功能，并使用高强的的密钥，例如UUID
---

## 6. 快速开始

### 6.1 启动服务
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 9001
```
> 若需通过nginx进行反向代理，则需添加root_path参数

### 6.2 健康检查
```bash
curl http://localhost:9001/health
# => {"status":"healthy","service":"TTS Proxy","version":"1.0.0"}
```

### 6.3 基本调用示例
```bash
curl -X POST http://localhost:9001/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-demo" \
  -d '{
    "model": "gpt-4o-mini-tts",
    "input": "你好，欢迎使用豆包语音服务",
    "voice": "alloy",
    "speed": 1.0,
    "response_format": "mp3"
  }' \
  --output speech.mp3
```
> 如未启用 API Key 认证，可删除 `Authorization` 请求头。

**Python 客户端示例**
```python
import requests

url = "http://localhost:9001/v1/audio/speech"
payload = {
    "model": "tts-1",
    "input": "这是一个 OpenAI 兼容接口示例",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1.25
}
headers = {"Authorization": "Bearer sk-demo"}
response = requests.post(url, json=payload, headers=headers, timeout=60)
response.raise_for_status()
with open("speech.wav", "wb") as f:
    f.write(response.content)
```

---

## 7. API 文档

### 7.1 `/v1/audio/speech`
- **Method**：`POST`
- **Content-Type**：`application/json`
- **认证**：可选 Bearer Token。

| 字段              | 类型                                       | 必填 | 说明                                         |
| ----------------- | ------------------------------------------ | ---- | -------------------------------------------- |
| `model`           | `tts-1` \| `tts-1-hd` \| `gpt-4o-mini-tts` | ✅    | 全部都会映射至`.env`中用户配置的豆包语音模型 |
| `input`           | `string` (1-4096)                          | ✅    | 待合成文本                                   |
| `voice`           | 详见上表                                   | ✅    | 11 种预设音色，可在`.env`中自行配置修改      |
| `response_format` | `mp3`/`opus`/`aac`/`flac`/`wav`/`pcm`      | ⭕    | 默认 `mp3`                                   |
| `speed`           | `float` (0.25~4.0)                         | ⭕    | 映射到 Doubao -50~100 语速                   |
| `instructions`    | `string`                                   | ⭕    | 预留（暂未生效）                             |
| `stream_format`   | `sse`/`audio`                              | ⭕    | 目前统一走音频流                             |

**响应**：`audio/*` 流（根据 `response_format` 自动设置 `Content-Type`），并携带 `Content-Disposition: attachment; filename="speech.{fmt}"`。

### 7.2 支持模型、音色与格式
- **模型**：`tts-1`, `tts-1-hd`, `gpt-4o-mini-tts`
- **音色**：`alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`, `onyx`, `nova`, `sage`, `shimmer`, `verse`。
- **格式**：`mp3`, `opus` (映射为 `ogg_opus`), `aac`, `flac`, `wav`, `pcm`。

### 7.3 错误映射（关键示例）
| Doubao Code | HTTP 状态 | OpenAI `type`           | 说明                  |
| ----------- | --------- | ----------------------- | --------------------- |
| `3001`      | 400       | `invalid_request_error` | 参数非法/缺失         |
| `3003`      | 429       | `rate_limit_error`      | 并发超限              |
| `3005`      | 503       | `service_unavailable`   | 服务繁忙              |
| `3010/3011` | 400       | `invalid_request_error` | 文本超长/无效         |
| `3030/3032` | 504       | `timeout_error`         | Doubao 处理或等待超时 |
| `3031/3040` | 500       | `api_error`             | 音频为空/连接错误     |
| `3050`      | 400       | `invalid_request_error` | 音色不存在            |
| `20000000`  | 200       | `success`               | 完成信号（内部使用）  |
> 其他错误会回退到 `500 api_error`，并返回 `{"error": {"message": ..., "code": "doubao_<code>"}}`。

---

## 8. 开发和测试

### 8.1 项目结构
```
app/
  config.py         # pydantic Settings
  main.py           # FastAPI 入口
  routes/audio.py   # /v1/audio/speech 路由
  services/
    converter.py    # OpenAI → Doubao 映射
    doubao_client.py# httpx 异步客户端
  middleware/auth.py# Bearer Token 校验
  models/           # OpenAI & Doubao 数据模型
  utils/            # 日志、错误处理
logs/               # 默认日志目录（loguru 自动创建）
tests/test_converter.py
```

### 8.2 运行测试
```bash
uv run pytest tests -q
```
> 当前测试覆盖参数转换逻辑，可据此扩展更多单元/集成测试。

### 8.3 开发建议
- 使用 `uvicorn app.main:app --reload` 以获得热重载。
- 通过调整 `.env` 中的 `LOG_LEVEL=DEBUG` 获取更详细日志。
- 针对 WebSocket/SSE 可在 `DoubaoTTSClient.synthesize_stream` 中扩展。

---

## 9. 常见问题与故障排除
| 症状                                  | 可能原因                                             | 解决方案                                                        |
| ------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| `401 invalid_api_key`                 | 开启认证但未传 Bearer Token 或 token 不在 `API_KEYS` | 确认请求头 `Authorization: Bearer <key>` 与 `.env` 配置一致     |
| `API密钥认证已启用但服务器未正确配置` | 设置了 `ENABLE_API_KEY_AUTH=true` 但 `API_KEYS` 为空 | 在 `.env` 中提供至少一个 key                                    |
| `HTTP 429 / rate_limit_error`         | 豆包并发超限                                         | 降低客户端并发，或调高 `MAX_CONCURRENT_REQUESTS` 并申请更高配额 |
| 请求超时/无音频返回                   | 文本过长、网络阻塞或 `REQUEST_TIMEOUT` 太小          | 缩短文本、提高超时时间、检查网络出口                            |
| `音色不存在`                          | 自定义 voice 映射错误                                | 在火山引擎控制台确认 speaker ID 是否可用                        |
| 日志为空                              | 未创建 `logs/` 目录或无写权限                        | 确保目录可写，或修改 `app/utils/logger.py` 输出设置             |

**性能优化建议**
- 在高并发场景下调大 `HTTP_POOL_LIMITS`，并使用更高性能的机器。
- 关闭 `ENABLE_REQUEST_LOGGING` / `ENABLE_DETAILED_ERRORS` 以降低日志开销。
- 利用前置缓存或队列削峰。
