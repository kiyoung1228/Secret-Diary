# storage.py

import json
import os


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DIARY_FILE = os.path.join(
    DATA_DIR,
    "diaries.json"
)

CAPSULE_FILE = os.path.join(
    DATA_DIR,
    "capsules.json"
)

HISTORY_FILE = os.path.join(
    DATA_DIR,
    "encryption_history.txt"
)


# data 폴더 생성
def create_data_directory():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


# JSON 파일 저장
def save_json(
    file_path,
    data
):
    create_data_directory()

    try:
        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

        return True

    except (OSError, TypeError) as error:
        print(
            f"파일 저장 오류: {error}"
        )

        return False


# JSON 파일 불러오기
def load_json(file_path):
    create_data_directory()

    if not os.path.exists(file_path):
        return []

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, list):
            print(
                "올바르지 않은 데이터 형식입니다."
            )

            return []

        return data

    except json.JSONDecodeError:
        print(
            "JSON 파일이 손상되었거나 "
            "형식이 올바르지 않습니다."
        )

        return []

    except (
        OSError,
        UnicodeDecodeError
    ) as error:

        print(
            f"파일 불러오기 오류: {error}"
        )

        return []


# 일기 저장
def save_diaries(diaries):
    return save_json(
        DIARY_FILE,
        diaries
    )


# 일기 불러오기
def load_diaries():
    return load_json(
        DIARY_FILE
    )


# 타임캡슐 저장
def save_capsules(capsules):
    return save_json(
        CAPSULE_FILE,
        capsules
    )


# 타임캡슐 불러오기
def load_capsules():
    return load_json(
        CAPSULE_FILE
    )


# 암호화 기록 한 줄 추가
def append_history(
    record
):
    create_data_directory()

    try:
        with open(
            HISTORY_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                str(record) + "\n"
            )

        return True

    except OSError as error:
        print(
            f"암호화 기록 저장 오류: {error}"
        )

        return False


# 암호화 기록 전체 저장
def save_history(
    history,
    file_path=None
):
    create_data_directory()

    if file_path is None:
        file_path = HISTORY_FILE

    try:
        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            for item in history:
                file.write(
                    str(item) + "\n"
                )

        return True

    except OSError as error:
        print(
            f"암호화 기록 저장 오류: {error}"
        )

        return False


# 암호화 기록 불러오기
def load_history(
    file_path=None
):
    create_data_directory()

    if file_path is None:
        file_path = HISTORY_FILE

    if not os.path.exists(file_path):
        return []

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            history = []

            for line in file:
                line = line.strip()

                if line:
                    history.append(line)

        return history

    except UnicodeDecodeError:
        print(
            "암호화 기록 파일의 "
            "형식이 올바르지 않습니다."
        )

        return []

    except OSError as error:
        print(
            f"암호화 기록 불러오기 오류: {error}"
        )

        return []


# 최근 암호화 기록 조회
def get_recent_history(
    limit=10
):
    history = load_history()

    if limit <= 0:
        return []

    return history[-limit:][::-1]


# 암호화 기록 초기화
def clear_history():
    create_data_directory()

    try:
        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ):
            pass

        return True

    except OSError as error:
        print(
            f"기록 초기화 오류: {error}"
        )

        return False


# storage.py 기능 테스트
if __name__ == "__main__":

    print("저장 기능 테스트")
    print()

    test_diaries = [
        {
            "id": 1,
            "date": "2026-09-22",
            "title": "테스트 일기",
            "mood": "😊",
            "tags": ["테스트"],
            "content": "암호화된 내용",
            "is_encrypted": True,
            "encryption_method": "SHIFT"
        }
    ]

    print(
        "일기 저장 :",
        save_diaries(
            test_diaries
        )
    )

    print(
        "일기 불러오기 :",
        load_diaries()
    )

    print()

    append_history(
        "2026-09-22 15:30:00 | 일기 | 암호화 | SHIFT | SUCCESS"
    )

    append_history(
        "2026-09-22 15:31:00 | 암호 도구 | 암호화 | KEYWORD | SUCCESS"
    )

    append_history(
        "2026-09-22 15:32:00 | 암호 도구 | 복호화 | SHIFT | SUCCESS"
    )

    print(
        "전체 기록 :"
    )

    for record in load_history():
        print(record)

    print()

    print(
        "최근 기록 :"
    )

    for record in get_recent_history(2):
        print(record)