from datetime import datetime, timezone

from firebase_client import db

COLLECTION = "conversations"


def _col():
    return db.collection(COLLECTION)


def _now():
    return datetime.now(timezone.utc).isoformat()


def create_conversation(item):
    doc = {
        "title": item.title,
        "messages": [m.model_dump() for m in item.messages],
        "created_at": _now(),
        "updated_at": _now(),
    }
    _, ref = _col().add(doc)
    return {"id": ref.id, **doc}


def list_conversations():
    """목록에는 messages를 빼고 가볍게 돌려준다. (불러오기는 GET /{id}로)"""
    docs = _col().order_by("updated_at", direction="DESCENDING").stream()
    result = []
    for d in docs:
        data = d.to_dict()
        result.append(
            {
                "id": d.id,
                "title": data.get("title", ""),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "message_count": len(data.get("messages", [])),
            }
        )
    return result


def get_conversation(conv_id):
    doc = _col().document(conv_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def append_messages(conv_id, new_messages):
    """기존 대화에 메시지를 이어 붙인다. 없으면 None."""
    ref = _col().document(conv_id)
    snap = ref.get()
    if not snap.exists:
        return None
    data = snap.to_dict()
    messages = data.get("messages", []) + new_messages
    ref.update({"messages": messages, "updated_at": _now()})
    return {"id": conv_id, **data, "messages": messages}


def delete_conversation(conv_id):
    ref = _col().document(conv_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True