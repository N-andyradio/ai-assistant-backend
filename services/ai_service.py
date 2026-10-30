import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

SYSTEM_PROMPT_TEMPLATE = """당신은 원/달러 환율 데이터 분석 비서입니다.

[사용자 데이터 요약]
- 데이터 기간: {period}
- 총 레코드: {count}개
- 주요 지표: {metrics}
- 최근 트렌드: {trend}

위 데이터를 기반으로 맞춤형 답변을 제공하세요.
데이터에 없는 내용은 추측하지 말고, 모른다고 말하세요.
답변은 한국어로, 간결하게 해주세요."""


def build_system_prompt(summary):
    """데이터 요약을 시스템 프롬프트에 끼워 넣는다 (컨텍스트 주입)."""
    return SYSTEM_PROMPT_TEMPLATE.format(
        period=summary.get("period"),
        count=summary.get("count"),
        metrics=summary.get("metrics"),
        trend=summary.get("trend"),
    )


def ask_ai(system_prompt, history, question):
    """history: [{"role": "user"|"assistant", "content": "..."}]"""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=800,
        ),
    )
    return response.text or "답변을 생성하지 못했어요."