# capsule.py

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
    load_capsules,
    save_capsules
)

from diary import get_diaries_by_date

from date_manager import (
    get_today_string,
    get_current_datetime,
    days_until,
    can_open_capsule,
    get_past_today,
    set_demo_date,
    reset_demo_date
)


# 새로운 타임캡슐 ID 생성
def create_capsule_id(capsules):
    if not capsules:
        return 1

    return max(
        capsule["id"]
        for capsule in capsules
    ) + 1


# 암호화 방식과 Key 검사
def validate_capsule_encryption(
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


# 타임캡슐 생성
def create_capsule(
    title,
    content,
    open_date,
    method=SHIFT,
    key=3
):
    capsules = load_capsules()

    if not title.strip():
        raise ValueError(
            "타임캡슐 제목을 입력해주세요."
        )

    if not content.strip():
        raise ValueError(
            "타임캡슐 내용을 입력해주세요."
        )

    method = method.upper()

    validate_capsule_encryption(
        method,
        key
    )

    # 공개일은 작성일보다 미래여야 함
    remaining_days = days_until(
        open_date
    )

    if remaining_days <= 0:
        raise ValueError(
            "공개 날짜는 오늘 이후로 설정해주세요."
        )

    # 암호화 후 정상 복원되는지 확인
    if not verify_restoration(
        content,
        method,
        key
    ):
        raise ValueError(
            "암호화 복원 검증에 실패했습니다."
        )

    encrypted_content = encrypt(
        content,
        method,
        key
    )

    content_hash = create_content_hash(
        content
    )

    capsule = {
        "id": create_capsule_id(
            capsules
        ),
        "title": title.strip(),
        "content": encrypted_content,
        "content_hash": content_hash,
        "created_date": get_today_string(),
        "open_date": open_date,
        "encryption_method": method,
        "is_opened": False,
        "created_at": (
            get_current_datetime()
            .isoformat(
                timespec="seconds"
            )
        ),
        "opened_at": None
    }

    capsules.append(capsule)

    if not save_capsules(capsules):
        raise OSError(
            "타임캡슐 저장에 실패했습니다."
        )

    return capsule


# 전체 타임캡슐 조회
def get_all_capsules():
    return load_capsules()


# ID로 타임캡슐 찾기
def get_capsule_by_id(
    capsule_id
):
    capsules = load_capsules()

    for capsule in capsules:
        if capsule["id"] == capsule_id:
            return capsule

    return None


# 타임캡슐 남은 날짜 계산
def get_capsule_remaining_days(
    capsule_id
):
    capsule = get_capsule_by_id(
        capsule_id
    )

    if capsule is None:
        raise ValueError(
            "타임캡슐을 찾을 수 없습니다."
        )

    return days_until(
        capsule["open_date"]
    )


# 타임캡슐 상태 반환
def get_capsule_status(
    capsule_id
):
    capsule = get_capsule_by_id(
        capsule_id
    )

    if capsule is None:
        raise ValueError(
            "타임캡슐을 찾을 수 없습니다."
        )

    remaining_days = days_until(
        capsule["open_date"]
    )

    if remaining_days > 0:
        return f"D-{remaining_days}"

    if capsule.get(
        "is_opened",
        False
    ):
        return "열람 완료"

    return "열람 가능"


# 아직 잠긴 타임캡슐 조회
def get_locked_capsules():
    capsules = load_capsules()

    return [
        capsule
        for capsule in capsules
        if not can_open_capsule(
            capsule["open_date"]
        )
    ]


# 공개일이 된 타임캡슐 조회
def get_available_capsules():
    capsules = load_capsules()

    return [
        capsule
        for capsule in capsules
        if can_open_capsule(
            capsule["open_date"]
        )
    ]


# 아직 열어보지 않은 공개 가능 타임캡슐
def get_new_available_capsules():
    capsules = load_capsules()

    return [
        capsule
        for capsule in capsules
        if can_open_capsule(
            capsule["open_date"]
        )
        and not capsule.get(
            "is_opened",
            False
        )
    ]


# 타임캡슐 열기
def open_capsule(
    capsule_id,
    key
):
    capsules = load_capsules()

    for capsule in capsules:

        if capsule["id"] != capsule_id:
            continue

        # 공개일 전에는 Key가 맞아도 열 수 없음
        if not can_open_capsule(
            capsule["open_date"]
        ):
            remaining_days = days_until(
                capsule["open_date"]
            )

            raise ValueError(
                f"아직 열 수 없습니다. D-{remaining_days}"
            )

        validate_capsule_encryption(
            capsule["encryption_method"],
            key
        )

        restored_content = decrypt(
            capsule["content"],
            capsule["encryption_method"],
            key
        )

        saved_hash = capsule.get(
            "content_hash"
        )

        # 입력한 Key가 맞는지 확인
        if saved_hash is not None:
            if not verify_content_hash(
                restored_content,
                saved_hash
            ):
                raise ValueError(
                    "Key가 올바르지 않습니다."
                )

        capsule["is_opened"] = True

        # 처음 열었을 때만 열람 날짜 기록
        if capsule.get(
            "opened_at"
        ) is None:
            capsule["opened_at"] = (
                get_current_datetime()
                .isoformat(
                    timespec="seconds"
                )
            )

        if not save_capsules(
            capsules
        ):
            raise OSError(
                "타임캡슐 상태 저장에 실패했습니다."
            )

        return restored_content

    raise ValueError(
        "타임캡슐을 찾을 수 없습니다."
    )


# 타임캡슐 삭제
def delete_capsule(
    capsule_id
):
    capsules = load_capsules()

    new_capsules = [
        capsule
        for capsule in capsules
        if capsule["id"] != capsule_id
    ]

    if len(new_capsules) == len(
        capsules
    ):
        return False

    if not save_capsules(
        new_capsules
    ):
        raise OSError(
            "타임캡슐 삭제에 실패했습니다."
        )

    return True


# 몇 년 전 오늘의 일기 조회
def get_memories(
    years=1
):
    past_date = get_past_today(
        years
    )

    return get_diaries_by_date(
        past_date.strftime(
            "%Y-%m-%d"
        )
    )


# 1년 전 오늘의 일기 조회
def get_one_year_ago_memories():
    return get_memories(1)


# 1년 전 오늘 일기가 있는지 확인
def has_one_year_ago_memory():
    return (
        len(
            get_one_year_ago_memories()
        )
        > 0
    )


# capsule.py 기능 테스트
if __name__ == "__main__":

    print("타임캡슐 기능 테스트")
    print()

    # 테스트 날짜를 임시로 설정
    set_demo_date(
        "2026-09-22"
    )

    print(
        "작성 날짜 :",
        get_today_string()
    )

    capsule = create_capsule(
        title="1년 뒤의 나에게",
        content=(
            "1년 뒤에는 지금보다 더 성장해 있기를!"
        ),
        open_date="2027-09-22",
        method=KEYWORD,
        key="APPLE"
    )

    print(
        "타임캡슐 ID :",
        capsule["id"]
    )

    print(
        "제목 :",
        capsule["title"]
    )

    print(
        "공개일 :",
        capsule["open_date"]
    )

    print(
        "암호문 :",
        capsule["content"]
    )

    print(
        "상태 :",
        get_capsule_status(
            capsule["id"]
        )
    )

    print()

    print("공개일 전 열람 테스트")

    try:
        open_capsule(
            capsule["id"],
            "APPLE"
        )

    except ValueError as error:
        print(
            "결과 :",
            error
        )

    print()

    # 1년 뒤로 시연 날짜 변경
    set_demo_date(
        "2027-09-22"
    )

    print(
        "시연 날짜 변경 :",
        get_today_string()
    )

    print(
        "상태 :",
        get_capsule_status(
            capsule["id"]
        )
    )

    print()

    print("틀린 Key 테스트")

    try:
        open_capsule(
            capsule["id"],
            "BANANA"
        )

    except ValueError as error:
        print(
            "결과 :",
            error
        )

    print()

    print("정상 Key 테스트")

    restored_content = open_capsule(
        capsule["id"],
        "APPLE"
    )

    print(
        "복호화된 내용 :",
        restored_content
    )

    print(
        "상태 :",
        get_capsule_status(
            capsule["id"]
        )
    )

    print()

    print("1년 전 오늘 테스트")

    memories = (
        get_one_year_ago_memories()
    )

    print(
        "1년 전 오늘 일기 수 :",
        len(memories)
    )

    for diary in memories:
        print(
            diary["date"],
            diary["title"],
            diary["mood"]
        )

    # 테스트가 끝나면 실제 현재 날짜로 복귀
    reset_demo_date()

    print()

    print(
        "실제 날짜로 복귀 :",
        get_today_string()
    )