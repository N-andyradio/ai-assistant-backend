from fastapi import APIRouter, HTTPException

from schemas import ChatIn, ConversationIn, Message
from services import ai_service, conversation_service, data_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
def chat(body: ChatIn):
    # 1) 데이터 요약 조회
    summary = data_service.get_summary()

    # 2) 요약을 시스템 프롬프트에 삽입
    system_prompt = ai_service.build_system_prompt(summary)

    # 이어서 하는 대화라면 이전 메시지를 불러온다
    history = []
    if body.conversation_id:
        conv = conversation_service.get_conversation(body.conversation_id)
        if conv is None:
            raise HTTPException(status_code=404, detail="해당 대화를 찾을 수 없습니다.")
        history = conv.get("messages", [])

    # 3) AI 호출
    try:
        answer = ai_service.ask_ai(system_prompt, history, body.question)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI 호출에 실패했습니다. 잠시 후 다시 시도해 주세요. ({type(e).__name__})",
        )

    # 4) 대화 자동 저장
    new_messages = [
        {"role": "user", "content": body.question},
        {"role": "assistant", "content": answer},
    ]
    if body.conversation_id:
        conversation_service.append_messages(body.conversation_id, new_messages)
        conv_id = body.conversation_id
    else:
        title = body.question[:30]
        saved = conversation_service.create_conversation(
            ConversationIn(title=title, messages=[Message(**m) for m in new_messages])
        )
        conv_id = saved["id"]

    return {"answer": answer, "conversation_id": conv_id}