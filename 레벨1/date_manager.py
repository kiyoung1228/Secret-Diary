from datetime import date, datetime


# 시연 모드 상태
_demo_mode = False
_demo_date = None


# 현재 프로그램 날짜 반환
def get_today():
    if _demo_mode and _demo_date is not None:
        return _demo_date

    return date.today()


# 현재 날짜를 문자열로 반환
def get_today_string():
    return get_today().strftime("%Y-%m-%d")


# 현재 날짜와 시간 반환
def get_current_datetime():
    today = get_today()

    now = datetime.now()

    return datetime(
        today.year,
        today.month,
        today.day,
        now.hour,
        now.minute,
        now.second
    )


# 시연 모드 활성화
def set_demo_date(date_string):
    global _demo_mode
    global _demo_date

    try:
        selected_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        raise ValueError(
            "날짜는 YYYY-MM-DD 형식으로 입력해주세요."
        )

    _demo_date = selected_date
    _demo_mode = True

    return _demo_date


# 실제 날짜 모드로 복귀
def reset_demo_date():
    global _demo_mode
    global _demo_date

    _demo_mode = False
    _demo_date = None


# 현재 시연 모드인지 확인
def is_demo_mode():
    return _demo_mode


# 두 날짜 사이의 일수 계산
def days_until(target_date):
    if isinstance(target_date, str):
        try:
            target_date = datetime.strptime(
                target_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            raise ValueError(
                "날짜는 YYYY-MM-DD 형식으로 입력해주세요."
            )

    return (target_date - get_today()).days


# 타임캡슐을 열 수 있는 날짜인지 확인
def can_open_capsule(open_date):
    return days_until(open_date) <= 0


# 몇 년 전 오늘 날짜 계산
def get_past_today(years=1):
    today = get_today()

    if years < 1:
        raise ValueError("1년 이상을 입력해주세요.")

    try:
        return today.replace(
            year=today.year - years
        )

    # 2월 29일인 경우 해당 연도의 2월 28일로 처리
    except ValueError:
        return today.replace(
            year=today.year - years,
            day=28
        )


# date_manager.py 기능 테스트
if __name__ == "__main__":

    print("실제 날짜 :", get_today_string())
    print("시연 모드 :", is_demo_mode())

    print()

    set_demo_date("2026-09-22")

    print("시연 날짜 :", get_today_string())
    print("시연 모드 :", is_demo_mode())

    print(
        "2027-09-22까지 :",
        days_until("2027-09-22"),
        "일"
    )

    print(
        "타임캡슐 열람 가능 :",
        can_open_capsule("2027-09-22")
    )

    print()

    set_demo_date("2027-09-22")

    print("1년 후 시연 날짜 :", get_today_string())
    print(
        "1년 전 오늘 :",
        get_past_today(1)
    )

    print(
        "타임캡슐 열람 가능 :",
        can_open_capsule("2027-09-22")
    )

    print()

    reset_demo_date()

    print("실제 날짜 복귀 :", get_today_string())
    print("시연 모드 :", is_demo_mode())