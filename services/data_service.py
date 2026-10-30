import time

from firebase_client import db

COLLECTION = "data"
CACHE_SECONDS = 600  # 10분

_cache = {"rows": None, "at": 0.0}


def _col():
    return db.collection(COLLECTION)


def _invalidate():
    _cache["rows"] = None


def create_data(item):
    doc = {"date": item.date.isoformat(), "value": item.value, "memo": item.memo}
    _, ref = _col().add(doc)
    _invalidate()
    return {"id": ref.id, **doc}


def list_data():
    now = time.time()
    if _cache["rows"] is not None and now - _cache["at"] < CACHE_SECONDS:
        return _cache["rows"]
    docs = _col().order_by("date").stream()
    rows = [{"id": d.id, **d.to_dict()} for d in docs]
    _cache["rows"] = rows
    _cache["at"] = now
    return rows


def update_data(data_id, item):
    ref = _col().document(data_id)
    if not ref.get().exists:
        return None
    changes = item.model_dump(exclude_unset=True, exclude_none=True)
    if "date" in changes:
        changes["date"] = changes["date"].isoformat()
    if changes:
        ref.update(changes)
    _invalidate()
    return {"id": data_id, **ref.get().to_dict()}


def delete_data(data_id):
    ref = _col().document(data_id)
    if not ref.get().exists:
        return False
    ref.delete()
    _invalidate()
    return True


def get_summary():
    rows = list_data()
    if not rows:
        return {"period": None, "count": 0, "metrics": {}, "trend": "데이터 없음"}

    values = [r["value"] for r in rows]
    max_row = max(rows, key=lambda r: r["value"])
    min_row = min(rows, key=lambda r: r["value"])

    # 추세: 최근 구간 평균 vs 바로 앞 구간 평균 (최대 30개씩)
    n = min(30, len(rows) // 2)
    if n >= 1:
        recent = sum(values[-n:]) / n
        before = sum(values[-2 * n:-n]) / n
        change = (recent - before) / before * 100 if before else 0
        if change > 1:
            trend = f"상승 (최근 {n}개 평균이 이전 {n}개 대비 {change:+.1f}%)"
        elif change < -1:
            trend = f"하락 (최근 {n}개 평균이 이전 {n}개 대비 {change:+.1f}%)"
        else:
            trend = f"유지 (변화 {change:+.1f}%)"
    else:
        trend = "데이터 부족"

    return {
        "period": f"{rows[0]['date']} ~ {rows[-1]['date']}",
        "count": len(rows),
        "metrics": {
            "average": round(sum(values) / len(values), 2),
            "max": max_row["value"],
            "max_date": max_row["date"],
            "min": min_row["value"],
            "min_date": min_row["date"],
        },
        "trend": trend,
    }