import json
import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

load_dotenv()


def _load_credentials():
    """환경변수에서 서비스 계정 키를 읽는다.

    - 로컬: 파일 경로 (예: ./serviceAccountKey.json)
    - Render 배포: JSON 전체 내용을 한 줄로 넣은 문자열
    """
    value = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    if not value:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON 환경변수가 없습니다.")

    if value.startswith("{"):
        return credentials.Certificate(json.loads(value))
    return credentials.Certificate(value)


if not firebase_admin._apps:
    firebase_admin.initialize_app(_load_credentials())

db = firestore.client()