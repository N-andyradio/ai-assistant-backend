import csv

from firebase_client import db

CSV_PATH = "data/usdkrw_clean.csv"
COLLECTION = "data"

col = db.collection(COLLECTION)

# 1) 기존 테스트 데이터 모두 삭제
deleted = 0
for doc in col.stream():
    doc.reference.delete()
    deleted += 1
print(f"기존 데이터 {deleted}개 삭제")

# 2) CSV 읽어서 date, value, memo 형태로 저장 (500개씩 묶어서 업로드)
batch = db.batch()
count = 0
with open(CSV_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        batch.set(
            col.document(),
            {
                "date": row["Date"],
                "value": round(float(row["Close"]), 2),
                "memo": "",
            },
        )
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
batch.commit()
print(f"새 데이터 {count}개 업로드 완료")