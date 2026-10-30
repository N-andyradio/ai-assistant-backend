from fastapi import APIRouter, HTTPException

from schemas import ConversationIn
from services import conversation_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", status_code=201)
def create(item: ConversationIn):
    return conversation_service.create_conversation(item)


@router.get("")
def list_all():
    return conversation_service.list_conversations()


@router.get("/{conv_id}")
def get_one(conv_id: str):
    result = conversation_service.get_conversation(conv_id)
    if result is None:
        raise HTTPException(status_code=404, detail="해당 대화를 찾을 수 없습니다.")
    return result


@router.delete("/{conv_id}")
def delete(conv_id: str):
    if not conversation_service.delete_conversation(conv_id):
        raise HTTPException(status_code=404, detail="해당 대화를 찾을 수 없습니다.")
    return {"message": "삭제되었습니다.", "id": conv_id}