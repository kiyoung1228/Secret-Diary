import json
import os

from crypto import (
    SHIFT, KEYWORD, encrypt, decrypt, verify_restoration,
    validate_shift_key, validate_keyword, create_content_hash, verify_content_hash
)
from date_manager import get_current_datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
VAULT_FILE = os.path.join(DATA_DIR, "vault.json")


def _load():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(VAULT_FILE):
        return []
    try:
        with open(VAULT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []


def _save(items):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)


def _validate(method, key):
    method = method.upper()
    if method == SHIFT:
        if not validate_shift_key(key):
            raise ValueError("SHIFT Key는 1~25의 정수여야 합니다.")
        return int(key)
    if method == KEYWORD:
        if not validate_keyword(key):
            raise ValueError("Keyword는 한 글자 이상의 영문 알파벳만 가능합니다.")
        return str(key)
    raise ValueError("지원하지 않는 암호 방식입니다.")


def get_all_vault_items():
    return _load()


def create_vault_item(category, title, content, method=SHIFT, key=3):
    if not title.strip():
        raise ValueError("제목을 입력해주세요.")
    if not content.strip():
        raise ValueError("비밀 내용을 입력해주세요.")
    key = _validate(method, key)
    if not verify_restoration(content, method, key):
        raise ValueError("암호화 복원 검증에 실패했습니다.")
    items = _load()
    item = {
        "id": max([x.get("id", 0) for x in items], default=0) + 1,
        "category": category or "기타",
        "title": title.strip(),
        "content": encrypt(content, method, key),
        "content_hash": create_content_hash(content),
        "encryption_method": method.upper(),
        "created_at": get_current_datetime().isoformat(timespec="seconds"),
        "updated_at": get_current_datetime().isoformat(timespec="seconds"),
    }
    items.append(item)
    _save(items)
    return item


def open_vault_item(item_id, key):
    items = _load()
    for item in items:
        if item.get("id") == item_id:
            key = _validate(item.get("encryption_method", SHIFT), key)
            plain = decrypt(item.get("content", ""), item.get("encryption_method", SHIFT), key)
            if not verify_content_hash(plain, item.get("content_hash", "")):
                raise ValueError("Key가 올바르지 않습니다.")
            return plain
    raise ValueError("비밀 메모를 찾을 수 없습니다.")


def update_vault_item(item_id, category, title, content, method, key):
    if not title.strip() or not content.strip():
        raise ValueError("제목과 비밀 내용을 입력해주세요.")
    key = _validate(method, key)
    if not verify_restoration(content, method, key):
        raise ValueError("암호화 복원 검증에 실패했습니다.")
    items = _load()
    for item in items:
        if item.get("id") == item_id:
            item.update({
                "category": category or "기타",
                "title": title.strip(),
                "content": encrypt(content, method, key),
                "content_hash": create_content_hash(content),
                "encryption_method": method.upper(),
                "updated_at": get_current_datetime().isoformat(timespec="seconds"),
            })
            _save(items)
            return item
    raise ValueError("비밀 메모를 찾을 수 없습니다.")


def delete_vault_item(item_id):
    items = _load()
    new_items = [x for x in items if x.get("id") != item_id]
    if len(new_items) == len(items):
        return False
    _save(new_items)
    return True
