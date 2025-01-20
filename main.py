from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio

app = FastAPI()

# 定义请求体模型
class TextInput(BaseModel):
    text: str

# 假设这是外部相似度计算 API 的 URL
SIMILARITY_API_URL = "http://example.com/api/calculate_similarity"  # 替换为实际的 API URL
KEY_POINTS_API_URL = "http://example.com/api/get_key_points"  # 替换为获取重点内容的 API URL
SUMMARY_API_URL = "http://example.com/api/get_summary"  # 替换为获取摘要的 API URL

async def get_similarity(text1: str, text2: str) -> float:
    """调用外部 API 计算相似度"""
    async with httpx.AsyncClient() as client:
        response = await client.post(SIMILARITY_API_URL, json={"text1": text1, "text2": text2})
        response.raise_for_status()  # 检查请求是否成功
        result = response.json()
        return result.get("similarity_score", 0.0)

async def get_key_points(text: str) -> str:
    """调用外部 API 获取重点内容"""
    async with httpx.AsyncClient() as client:
        response = await client.post(KEY_POINTS_API_URL, json={"text": text})
        response.raise_for_status()
        result = response.json()
        return result.get("key_points", "")

async def get_summary(text: str) -> str:
    """调用外部 API 获取摘要内容"""
    async with httpx.AsyncClient() as client:
        response = await client.post(SUMMARY_API_URL, json={"text": text})
        response.raise_for_status()
        result = response.json()
        return result.get("summary", "")

async def process_chunk(chunk: str):
    """处理单个文本切片，获取重点和摘要"""
    key_points = await get_key_points(chunk)
    summary = await get_summary(chunk)

    return {
        "text": chunk,
        "key_points": key_points,
        "summary": summary
    }

async def process_text_chunks(sentences, threshold=0.8):
    """根据相似度阈值处理文本切片，并获取每个切片的重点和摘要"""
    chunks = []

    for i in range(len(sentences) - 1):
        similarity_score = await get_similarity(sentences[i], sentences[i + 1])

        if similarity_score >= threshold:  # 如果相似度高于阈值
            if chunks and isinstance(chunks[-1], list):
                chunks[-1].append(sentences[i])
            else:
                chunks.append([sentences[i]])
        else:
            chunks.append([sentences[i]])

    # 添加最后一个句子
    if sentences:
        chunks.append([sentences[-1]])

    # 对每个切片进行处理
    processed_chunks = await asyncio.gather(*(process_chunk(" ".join(chunk)) for chunk in chunks))

    return processed_chunks

@app.post("/api/v1/AiMeeting")
async def ai_meeting(input: TextInput):
    # 获取输入文本
    text = input.text

    # 切分文本为句子
    sentences = text.split('\n\n')  # 假设段落由两个换行符分隔

    # 处理文本切片并获取重点和摘要
    processed_chunks = await process_text_chunks(sentences)

    return {"message": "Text processed successfully!", "chunks": processed_chunks}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
