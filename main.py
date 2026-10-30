import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, conversations, data
load_dotenv()

app = FastAPI(title="AI 비서 API")

# .env의 ALLOWED_ORIGINS를 리스트로 변환
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)
@app.get("/")
def root():
    return {"message": "AI 비서 서버가 실행 중입니다."}