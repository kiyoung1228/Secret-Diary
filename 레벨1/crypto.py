# crypto.py

import hashlib


SHIFT = "SHIFT"
KEYWORD = "KEYWORD"

DEFAULT_METHOD = SHIFT
DEFAULT_SHIFT_KEY = 3


# 영문자인지 확인
def is_english(char):
    return ('A' <= char <= 'Z') or ('a' <= char <= 'z')


# 완성형 한글인지 확인
def is_korean(char):
    return '가' <= char <= '힣'


# 암호화 가능한 문자인지 확인
def is_encryptable(char):
    return is_english(char) or is_korean(char)


# 이동 암호 Key 검사
def validate_shift_key(key):
    try:
        key = int(key)
        return 1 <= key <= 25

    except (ValueError, TypeError):
        return False


# Keyword 검사
def validate_keyword(keyword):
    if not isinstance(keyword, str):
        return False

    if len(keyword) == 0:
        return False

    return all(
        is_english(char)
        for char in keyword
    )


# 영문자 이동
def shift_english(char, amount):
    if 'A' <= char <= 'Z':
        return chr(
            (
                ord(char)
                - ord('A')
                + amount
            ) % 26
            + ord('A')
        )

    if 'a' <= char <= 'z':
        return chr(
            (
                ord(char)
                - ord('a')
                + amount
            ) % 26
            + ord('a')
        )

    return char


# 한글 이동
def shift_korean(char, amount):
    hangul_start = ord('가')
    hangul_end = ord('힣')

    hangul_count = (
        hangul_end
        - hangul_start
        + 1
    )

    if is_korean(char):
        return chr(
            (
                ord(char)
                - hangul_start
                + amount
            ) % hangul_count
            + hangul_start
        )

    return char


# 문자 종류에 맞게 이동
def shift_character(char, amount):
    if is_english(char):
        return shift_english(
            char,
            amount
        )

    if is_korean(char):
        return shift_korean(
            char,
            amount
        )

    return char


# 이동 암호 암호화
def encrypt_shift(text, key):
    if not validate_shift_key(key):
        raise ValueError(
            "이동 암호 Key는 1~25의 정수여야 합니다."
        )

    key = int(key)

    result = ""

    for char in text:
        result += shift_character(
            char,
            key
        )

    return result


# 이동 암호 복호화
def decrypt_shift(text, key):
    if not validate_shift_key(key):
        raise ValueError(
            "이동 암호 Key는 1~25의 정수여야 합니다."
        )

    key = int(key)

    result = ""

    for char in text:
        result += shift_character(
            char,
            -key
        )

    return result


# Keyword를 이동값 목록으로 변환
def keyword_to_shifts(keyword):
    if not validate_keyword(keyword):
        raise ValueError(
            "Keyword는 한 글자 이상의 영문 알파벳만 가능합니다."
        )

    shifts = []

    for char in keyword.upper():
        shifts.append(
            ord(char) - ord('A')
        )

    return shifts


# Keyword 암호화
def encrypt_keyword(text, keyword):
    shifts = keyword_to_shifts(keyword)

    result = ""
    key_index = 0

    for char in text:

        if is_encryptable(char):
            amount = shifts[
                key_index % len(shifts)
            ]

            result += shift_character(
                char,
                amount
            )

            key_index += 1

        else:
            result += char

    return result


# Keyword 복호화
def decrypt_keyword(text, keyword):
    shifts = keyword_to_shifts(keyword)

    result = ""
    key_index = 0

    for char in text:

        if is_encryptable(char):
            amount = shifts[
                key_index % len(shifts)
            ]

            result += shift_character(
                char,
                -amount
            )

            key_index += 1

        else:
            result += char

    return result


# 선택한 방식으로 암호화
def encrypt(
    text,
    method=DEFAULT_METHOD,
    key=DEFAULT_SHIFT_KEY
):
    method = method.upper()

    if method == SHIFT:
        return encrypt_shift(
            text,
            key
        )

    if method == KEYWORD:
        return encrypt_keyword(
            text,
            key
        )

    raise ValueError(
        "지원하지 않는 암호화 방식입니다."
    )


# 선택한 방식으로 복호화
def decrypt(
    text,
    method=DEFAULT_METHOD,
    key=DEFAULT_SHIFT_KEY
):
    method = method.upper()

    if method == SHIFT:
        return decrypt_shift(
            text,
            key
        )

    if method == KEYWORD:
        return decrypt_keyword(
            text,
            key
        )

    raise ValueError(
        "지원하지 않는 암호화 방식입니다."
    )


# 암호화 후 원문 복원 확인
def verify_restoration(
    original,
    method=DEFAULT_METHOD,
    key=DEFAULT_SHIFT_KEY
):
    encrypted = encrypt(
        original,
        method,
        key
    )

    restored = decrypt(
        encrypted,
        method,
        key
    )

    return original == restored


# 원문 검증값 생성
def create_content_hash(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# 복호화 결과 검증
def verify_content_hash(
    text,
    saved_hash
):
    return (
        create_content_hash(text)
        == saved_hash
    )


# crypto.py 기능 테스트
if __name__ == "__main__":

    print("이동 암호 테스트")

    original = (
        "Hello 안녕하세요! 2026."
    )

    encrypted = encrypt(
        original,
        SHIFT,
        3
    )

    restored = decrypt(
        encrypted,
        SHIFT,
        3
    )

    print("원문 :", original)
    print("암호문 :", encrypted)
    print("복호문 :", restored)

    if original == restored:
        print("복원 검증 : SUCCESS")
    else:
        print("복원 검증 : FAIL")

    print()

    print("Keyword 암호 테스트")

    original = (
        "오늘 학교에서 AI 공부했다! Hello 123."
    )

    encrypted = encrypt(
        original,
        KEYWORD,
        "APPLE"
    )

    restored = decrypt(
        encrypted,
        KEYWORD,
        "APPLE"
    )

    print("원문 :", original)
    print("암호문 :", encrypted)
    print("복호문 :", restored)

    if original == restored:
        print("복원 검증 : SUCCESS")
    else:
        print("복원 검증 : FAIL")

    print()

    print("검증값 테스트")

    saved_hash = create_content_hash(
        original
    )

    print(
        "정상 원문 :",
        verify_content_hash(
            original,
            saved_hash
        )
    )

    print(
        "다른 내용 :",
        verify_content_hash(
            "틀린 내용",
            saved_hash
        )
    )