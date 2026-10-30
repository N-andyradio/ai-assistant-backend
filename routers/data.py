from fastapi import APIRouter, HTTPException

from schemas import DataIn, DataUpdate
from services import data_service

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("", status_code=201)
def create(item: DataIn):
    return data_service.create_data(item)


@router.get("")
def list_all():
    return data_service.list_data()


# 주의: "/summary"는 "/{data_id}"보다 반드시 먼저 선언해야 해요
@router.get("/summary")
def summary():
    return data_service.get_summary()


@router.put("/{data_id}")
def update(data_id: str, item: DataUpdate):
    result = data_service.update_data(data_id, item)
    if result is None:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    return result


@router.delete("/{data_id}")
def delete(data_id: str):
    if not data_service.delete_data(data_id):
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    return {"message": "삭제되었습니다.", "id": data_id}