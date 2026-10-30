from datetime import date as date_type
from typing import List, Optional

from pydantic import BaseModel, Field


class DataIn(BaseModel):
    """데이터 추가용 (POST)"""
    date: date_type                      # 예: 2025-01-02 (형식이 틀리면 422 오류)
    value: float                         # 숫자만 허용
    memo: str = Field(default="", max_length=200)


class DataUpdate(BaseModel):
    """데이터 수정용 (PUT) - 바꾸고 싶은 항목만 보내도 됨"""
    date: Optional[date_type] = None
    value: Optional[float] = None
    memo: Optional[str] = Field(default=None, max_length=200)


class Message(BaseModel):
    role: str                            # "user" 또는 "assistant"
    content: str = Field(min_length=1)


class ConversationIn(BaseModel):
    """대화 저장용"""
    title: str = Field(default="새 대화", max_length=100)
    messages: List[Message]


class ChatIn(BaseModel):
    """챗봇 질문용"""
    question: str = Field(min_length=1, max_length=1000)
    conversation_id: Optional[str] = None