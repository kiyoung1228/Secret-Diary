# diary.py

from date_manager import get_current_datetime

from crypto import (
    SHIFT,
    KEYWORD,
    encrypt,
    decrypt,
    verify_restoration,
    validate_shift_key,
    validate_keyword,
    create_content_hash,
    verify_content_hash
)

from storage import (
    load_diaries,
    save_diaries
)


# 새로운 일기 ID 생성
def create_diary_id(diaries):
    if not diaries:
        return 1

    return max(
        diary["id"]
        for diary in diaries
    ) + 1


# 암호화 방식과 Key 검사
def validate_encryption(
    method,
    key
):
    method = method.upper()

    if method == SHIFT:

        if not validate_shift_key(key):
            raise ValueError(
                "이동 암호 Key는 1~25의 정수여야 합니다."
            )

    elif method == KEYWORD:

        if not validate_keyword(key):
            raise ValueError(
                "Keyword는 한 글자 이상의 영문 알파벳만 가능합니다."
            )

    else:
        raise ValueError(
            "지원하지 않는 암호화 방식입니다."
        )


# 일기 생성
def create_diary(
    date,
    title,
    content,
    mood,
    tags,
    is_encrypted=False,
    method=SHIFT,
    key=3
):
    diaries = load_diaries()

    if not title.strip():
        raise ValueError(
            "제목을 입력해주세요."
        )

    if not content.strip():
        raise ValueError(
            "일기 내용을 입력해주세요."
        )

    if is_encrypted:

        method = method.upper()

        validate_encryption(
            method,
            key
        )

        # 암호화 후 원문 복원 확인
        if not verify_restoration(
            content,
            method,
            key
        ):
            raise ValueError(
                "암호화 복원 검증에 실패했습니다."
            )

        saved_content = encrypt(
            content,
            method,
            key
        )

        content_hash = (
            create_content_hash(content)
        )

    else:
        saved_content = content
        content_hash = None
        method = None

    current_time = (
        get_current_datetime()
        .isoformat(
            timespec="seconds"
        )
    )

    diary = {
        "id": create_diary_id(diaries),
        "date": date,
        "title": title.strip(),
        "content": saved_content,
        "mood": mood,
        "tags": tags,
        "is_encrypted": is_encrypted,
        "encryption_method": method,
        "content_hash": content_hash,
        "created_at": current_time,
        "updated_at": current_time
    }

    diaries.append(diary)

    if not save_diaries(diaries):
        raise OSError(
            "일기 저장에 실패했습니다."
        )

    return diary


# 전체 일기 조회
def get_all_diaries():
    return load_diaries()


# ID로 일기 찾기
def get_diary_by_id(diary_id):
    diaries = load_diaries()

    for diary in diaries:

        if diary["id"] == diary_id:
            return diary

    return None


# 날짜로 일기 검색
def get_diaries_by_date(date):
    diaries = load_diaries()

    return [
        diary
        for diary in diaries
        if diary["date"] == date
    ]


# 잠긴 일기의 본문 열기
def open_diary(
    diary_id,
    key=None
):
    diary = get_diary_by_id(
        diary_id
    )

    if diary is None:
        raise ValueError(
            "일기를 찾을 수 없습니다."
        )

    # 일반 일기는 바로 반환
    if not diary["is_encrypted"]:
        return diary["content"]

    if key is None:
        raise ValueError(
            "암호화된 일기입니다. Key를 입력해주세요."
        )

    validate_encryption(
        diary["encryption_method"],
        key
    )

    restored_content = decrypt(
        diary["content"],
        diary["encryption_method"],
        key
    )

    saved_hash = diary.get(
        "content_hash"
    )

    # 새 버전의 일기는 Key 검증 수행
    if saved_hash is not None:

        if not verify_content_hash(
            restored_content,
            saved_hash
        ):
            raise ValueError(
                "Key가 올바르지 않습니다."
            )

    return restored_content


# 일기 수정
def update_diary(
    diary_id,
    date,
    title,
    content,
    mood,
    tags,
    is_encrypted=False,
    method=SHIFT,
    key=3
):
    diaries = load_diaries()

    if not title.strip():
        raise ValueError(
            "제목을 입력해주세요."
        )

    if not content.strip():
        raise ValueError(
            "일기 내용을 입력해주세요."
        )

    for diary in diaries:

        if diary["id"] != diary_id:
            continue

        if is_encrypted:

            method = method.upper()

            validate_encryption(
                method,
                key
            )

            if not verify_restoration(
                content,
                method,
                key
            ):
                raise ValueError(
                    "암호화 복원 검증에 실패했습니다."
                )

            saved_content = encrypt(
                content,
                method,
                key
            )

            content_hash = (
                create_content_hash(
                    content
                )
            )

        else:
            saved_content = content
            content_hash = None
            method = None

        diary["date"] = date
        diary["title"] = (
            title.strip()
        )
        diary["content"] = (
            saved_content
        )
        diary["mood"] = mood
        diary["tags"] = tags
        diary["is_encrypted"] = (
            is_encrypted
        )
        diary[
            "encryption_method"
        ] = method
        diary[
            "content_hash"
        ] = content_hash

        diary["updated_at"] = (
            get_current_datetime()
            .isoformat(
                timespec="seconds"
            )
        )

        if not save_diaries(
            diaries
        ):
            raise OSError(
                "일기 수정에 실패했습니다."
            )

        return diary

    raise ValueError(
        "일기를 찾을 수 없습니다."
    )


# 일기 삭제
def delete_diary(diary_id):
    diaries = load_diaries()

    new_diaries = [
        diary
        for diary in diaries
        if diary["id"] != diary_id
    ]

    if len(new_diaries) == len(diaries):
        return False

    if not save_diaries(
        new_diaries
    ):
        raise OSError(
            "일기 삭제에 실패했습니다."
        )

    return True


# 제목으로 검색
def search_by_title(keyword):
    diaries = load_diaries()

    keyword = (
        keyword.strip().lower()
    )

    if not keyword:
        return diaries

    return [
        diary
        for diary in diaries
        if keyword
        in diary["title"].lower()
    ]


# 태그로 검색
def search_by_tag(tag):
    diaries = load_diaries()

    tag = tag.strip()

    if not tag:
        return diaries

    return [
        diary
        for diary in diaries
        if tag in diary["tags"]
    ]


# 기분으로 검색
def search_by_mood(mood):
    diaries = load_diaries()

    return [
        diary
        for diary in diaries
        if diary["mood"] == mood
    ]


# 암호화 여부로 검색
def search_by_encryption(
    is_encrypted
):
    diaries = load_diaries()

    return [
        diary
        for diary in diaries
        if diary["is_encrypted"]
        == is_encrypted
    ]


# 여러 조건으로 검색
def search_diaries(
    title=None,
    tag=None,
    mood=None,
    date=None,
    is_encrypted=None
):
    results = load_diaries()

    if title:

        title = (
            title.strip().lower()
        )

        results = [
            diary
            for diary in results
            if title
            in diary["title"].lower()
        ]

    if tag:

        tag = tag.strip()

        results = [
            diary
            for diary in results
            if tag in diary["tags"]
        ]

    if mood:

        results = [
            diary
            for diary in results
            if diary["mood"] == mood
        ]

    if date:

        results = [
            diary
            for diary in results
            if diary["date"] == date
        ]

    if is_encrypted is not None:

        results = [
            diary
            for diary in results
            if diary["is_encrypted"]
            == is_encrypted
        ]

    return results


# diary.py 기능 테스트
if __name__ == "__main__":

    print("일기 생성 테스트")

    diary = create_diary(
        date="2026-09-22",
        title="친구들과 보낸 하루",
        content=(
            "오늘 친구들과 맛있는 저녁을 먹었다. "
            "It was fun!"
        ),
        mood="😊",
        tags=[
            "일상",
            "친구"
        ],
        is_encrypted=True,
        method=KEYWORD,
        key="APPLE"
    )

    print(
        "ID :",
        diary["id"]
    )

    print(
        "날짜 :",
        diary["date"]
    )

    print(
        "제목 :",
        diary["title"]
    )

    print(
        "기분 :",
        diary["mood"]
    )

    print(
        "태그 :",
        diary["tags"]
    )

    print(
        "저장된 본문 :",
        diary["content"]
    )

    print(
        "암호 방식 :",
        diary["encryption_method"]
    )

    print()

    print("정상 Key 테스트")

    restored_content = open_diary(
        diary["id"],
        "APPLE"
    )

    print(
        "복호화된 본문 :",
        restored_content
    )

    print()

    print("틀린 Key 테스트")

    try:
        open_diary(
            diary["id"],
            "BANANA"
        )

    except ValueError as error:
        print(
            "결과 :",
            error
        )

    print()

    print("검색 테스트")

    results = search_diaries(
        tag="친구",
        mood="😊",
        is_encrypted=True
    )

    for item in results:
        print(
            item["date"],
            item["title"],
            item["mood"]
        )