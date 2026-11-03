# statistics.py

from collections import Counter
from datetime import datetime, timedelta

from storage import load_diaries
from date_manager import get_today


# 전체 일기 수
def get_total_diaries():
    return len(load_diaries())


# 암호화된 일기 수
def get_encrypted_diary_count():
    diaries = load_diaries()

    return sum(
        1
        for diary in diaries
        if diary.get("is_encrypted", False)
    )


# 암호화된 일기 비율
def get_encrypted_ratio():
    diaries = load_diaries()

    if not diaries:
        return 0.0

    encrypted_count = sum(
        1
        for diary in diaries
        if diary.get("is_encrypted", False)
    )

    return round(
        encrypted_count / len(diaries) * 100,
        1
    )


# 이번 달 작성한 일기 수
def get_current_month_count():
    diaries = load_diaries()
    today = get_today()

    count = 0

    for diary in diaries:
        try:
            diary_date = datetime.strptime(
                diary["date"],
                "%Y-%m-%d"
            ).date()

            if (
                diary_date.year == today.year
                and diary_date.month == today.month
            ):
                count += 1

        except (ValueError, KeyError):
            continue

    return count


# 이번 연도 작성한 일기 수
def get_current_year_count():
    diaries = load_diaries()
    today = get_today()

    count = 0

    for diary in diaries:
        try:
            diary_date = datetime.strptime(
                diary["date"],
                "%Y-%m-%d"
            ).date()

            if diary_date.year == today.year:
                count += 1

        except (ValueError, KeyError):
            continue

    return count


# 기분별 일기 개수
def get_mood_counts():
    diaries = load_diaries()

    moods = []

    for diary in diaries:
        mood = diary.get("mood")

        if mood:
            moods.append(mood)

    return dict(Counter(moods))


# 가장 많이 기록한 기분
def get_most_common_mood():
    mood_counts = get_mood_counts()

    if not mood_counts:
        return None

    return max(
        mood_counts,
        key=mood_counts.get
    )


# 태그별 사용 횟수
def get_tag_counts():
    diaries = load_diaries()

    tags = []

    for diary in diaries:
        for tag in diary.get("tags", []):
            if tag:
                tags.append(tag)

    return dict(Counter(tags))


# 가장 많이 사용한 태그
def get_most_common_tag():
    tag_counts = get_tag_counts()

    if not tag_counts:
        return None

    return max(
        tag_counts,
        key=tag_counts.get
    )


# 자주 사용한 태그 순위
def get_top_tags(limit=5):
    tag_counts = get_tag_counts()

    sorted_tags = sorted(
        tag_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return sorted_tags[:limit]


# 월별 작성량
def get_monthly_counts(year=None):
    diaries = load_diaries()

    if year is None:
        year = get_today().year

    monthly_counts = {
        month: 0
        for month in range(1, 13)
    }

    for diary in diaries:
        try:
            diary_date = datetime.strptime(
                diary["date"],
                "%Y-%m-%d"
            ).date()

            if diary_date.year == year:
                monthly_counts[
                    diary_date.month
                ] += 1

        except (ValueError, KeyError):
            continue

    return monthly_counts


# 요일별 작성량
def get_weekday_counts():
    diaries = load_diaries()

    weekday_names = [
        "월",
        "화",
        "수",
        "목",
        "금",
        "토",
        "일"
    ]

    counts = {
        day: 0
        for day in weekday_names
    }

    for diary in diaries:
        try:
            diary_date = datetime.strptime(
                diary["date"],
                "%Y-%m-%d"
            ).date()

            weekday = weekday_names[
                diary_date.weekday()
            ]

            counts[weekday] += 1

        except (ValueError, KeyError):
            continue

    return counts


# 가장 많이 일기를 작성한 요일
def get_most_active_weekday():
    counts = get_weekday_counts()

    if sum(counts.values()) == 0:
        return None

    return max(
        counts,
        key=counts.get
    )


# 일기를 작성한 날짜 목록
def get_written_dates():
    diaries = load_diaries()

    dates = set()

    for diary in diaries:
        try:
            diary_date = datetime.strptime(
                diary["date"],
                "%Y-%m-%d"
            ).date()

            dates.add(diary_date)

        except (ValueError, KeyError):
            continue

    return sorted(dates)


# 최장 연속 작성일 계산
def get_longest_streak():
    dates = get_written_dates()

    if not dates:
        return 0

    longest = 1
    current = 1

    for index in range(
        1,
        len(dates)
    ):
        difference = (
            dates[index]
            - dates[index - 1]
        ).days

        if difference == 1:
            current += 1

            if current > longest:
                longest = current

        else:
            current = 1

    return longest


# 현재 연속 작성일 계산
def get_current_streak():
    dates = get_written_dates()

    if not dates:
        return 0

    today = get_today()

    written_dates = set(dates)

    # 오늘 또는 어제 작성한 기록부터 계산
    if today in written_dates:
        current_date = today

    elif (
        today - timedelta(days=1)
        in written_dates
    ):
        current_date = (
            today - timedelta(days=1)
        )

    else:
        return 0

    streak = 0

    while current_date in written_dates:
        streak += 1

        current_date -= timedelta(
            days=1
        )

    return streak


# 특정 연도의 총 작성량
def get_year_count(year):
    diaries = load_diaries()

    count = 0

    for diary in diaries:
        try:
            diary_date = datetime.strptime(
                diary["date"],
                "%Y-%m-%d"
            ).date()

            if diary_date.year == year:
                count += 1

        except (ValueError, KeyError):
            continue

    return count


# 전체 통계 요약
def get_statistics_summary():
    return {
        "total_diaries":
            get_total_diaries(),

        "current_month":
            get_current_month_count(),

        "current_year":
            get_current_year_count(),

        "current_streak":
            get_current_streak(),

        "longest_streak":
            get_longest_streak(),

        "most_common_mood":
            get_most_common_mood(),

        "most_common_tag":
            get_most_common_tag(),

        "most_active_weekday":
            get_most_active_weekday(),

        "encrypted_count":
            get_encrypted_diary_count(),

        "encrypted_ratio":
            get_encrypted_ratio()
    }


# statistics.py 기능 테스트
if __name__ == "__main__":

    print("일기 통계 테스트")
    print()

    print(
        "전체 일기 :",
        get_total_diaries(),
        "개"
    )

    print(
        "이번 달 :",
        get_current_month_count(),
        "개"
    )

    print(
        "올해 :",
        get_current_year_count(),
        "개"
    )

    print(
        "현재 연속 작성 :",
        get_current_streak(),
        "일"
    )

    print(
        "최장 연속 작성 :",
        get_longest_streak(),
        "일"
    )

    print(
        "가장 많이 기록한 기분 :",
        get_most_common_mood()
    )

    print(
        "가장 많이 사용한 태그 :",
        get_most_common_tag()
    )

    print(
        "가장 많이 작성한 요일 :",
        get_most_active_weekday()
    )

    print(
        "암호화된 일기 :",
        get_encrypted_diary_count(),
        "개"
    )

    print(
        "암호화 비율 :",
        get_encrypted_ratio(),
        "%"
    )

    print()

    print("기분별 통계")
    print(
        get_mood_counts()
    )

    print()

    print("태그 TOP 5")
    print(
        get_top_tags(5)
    )

    print()

    print(
        f"{get_today().year}년 월별 작성량"
    )

    monthly_counts = (
        get_monthly_counts()
    )

    for month, count in (
        monthly_counts.items()
    ):
        print(
            f"{month}월 : {count}개"
        )