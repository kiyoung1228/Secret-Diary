# ui.py

import calendar
from datetime import datetime

import flet as ft

from date_manager import (
    get_today,
    get_today_string,
    get_current_datetime,
    is_demo_mode,
    set_demo_date,
    reset_demo_date
)

from statistics import (
    get_statistics_summary, get_monthly_counts, get_mood_counts,
    get_top_tags, get_weekday_counts
)

from diary import (
    create_diary,
    get_diaries_by_date,
    get_diary_by_id,
    open_diary,
    update_diary,
    delete_diary,
    search_diaries
)

from capsule import (
    create_capsule,
    get_all_capsules,
    get_capsule_status,
    open_capsule,
    get_one_year_ago_memories
)

from crypto import (
    SHIFT, KEYWORD, encrypt, decrypt, verify_restoration
)
from vault import (
    get_all_vault_items, create_vault_item, open_vault_item,
    update_vault_item, delete_vault_item
)

from storage import (
    append_history, load_history, get_recent_history,
    save_history, clear_history, HISTORY_FILE
)


class SecretDiaryApp:

    def __init__(self, page: ft.Page):
        self.page = page
        self.session_history = []

        self.page.title = "Secret Diary"
        self.page.window.width = 1250
        self.page.window.height = 800
        self.page.window.min_width = 1050
        self.page.window.min_height = 700

        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = "#F7F7FA"

        self.content = ft.Container(
            expand=True,
            padding=30
        )

        self.encryption_switch = None
        self.encryption_options = None
        self.method_dropdown = None
        self.key_field = None
        self.key_help_text = None

        today = get_today()

        self.calendar_year = today.year
        self.calendar_month = today.month
        self.selected_calendar_date = get_today_string()

        self.weekday_auto_encryption = False

        self.weekday_rules = {
            0: {"method": SHIFT, "key": "3"},
            1: {"method": KEYWORD, "key": "APPLE"},
            2: {"method": SHIFT, "key": "7"},
            3: {"method": KEYWORD, "key": "SECRET"},
            4: {"method": SHIFT, "key": "12"},
            5: {"method": KEYWORD, "key": "WEEKEND"},
            6: {"method": SHIFT, "key": "20"}
        }

    def start(self):
        self.page.add(
            ft.Row(
                controls=[
                    self.create_sidebar(),
                    self.content
                ],
                spacing=0,
                expand=True
            )
        )

        self.show_home()

    def create_sidebar(self):
        return ft.Container(
            width=220,
            bgcolor="#17171C",
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Container(
                        padding=ft.Padding(
                            left=10,
                            right=10,
                            top=20,
                            bottom=25
                        ),
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "🔐 Secret Diary",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="white"
                                ),
                                ft.Text(
                                    "나만의 비밀 기록",
                                    size=11,
                                    color="#92929A"
                                )
                            ],
                            spacing=4
                        )
                    ),

                    self.menu_button(
                        "🏠",
                        "홈",
                        self.show_home
                    ),

                    self.menu_button(
                        "✏️",
                        "일기 쓰기",
                        self.show_write_diary
                    ),

                    self.menu_button(
                        "📅",
                        "캘린더",
                        self.show_calendar
                    ),

                    self.menu_button(
                        "🔎",
                        "일기 찾기",
                        self.show_search
                    ),

                    self.menu_button(
                        "🔐",
                        "비밀 보관함",
                        self.show_vault
                    ),

                    self.menu_button(
                        "💌",
                        "타임캡슐",
                        self.show_capsule
                    ),

                    self.menu_button(
                        "📊",
                        "나의 기록",
                        self.show_statistics
                    ),

                    self.menu_button(
                        "🔐",
                        "암호 도구",
                        self.show_crypto
                    ),

                    self.menu_button(
                        "🕘",
                        "암호화 기록",
                        self.show_history
                    ),

                    ft.Container(expand=True),

                    ft.Divider(
                        color="#303038"
                    ),

                    self.menu_button(
                        "⚙️",
                        "설정",
                        self.show_settings
                    )
                ],
                expand=True
            )
        )

    def menu_button(self, icon, text, command):
        return ft.Container(
            border_radius=12,
            content=ft.TextButton(
                on_click=lambda e: command(),
                content=ft.Row(
                    controls=[
                        ft.Text(
                            icon,
                            size=17
                        ),
                        ft.Text(
                            text,
                            size=14,
                            color="#E7E7EA"
                        )
                    ],
                    spacing=12
                ),
                style=ft.ButtonStyle(
                    padding=15
                )
            )
        )

    def change_page(self, controls):
        self.content.content = ft.Column(
            controls=controls,
            scroll=ft.ScrollMode.AUTO
        )

        self.content.update()

    def page_header(self, title, description):
        return ft.Container(
            margin=ft.Margin(
                left=0,
                right=0,
                top=0,
                bottom=15
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        title,
                        size=27,
                        weight=ft.FontWeight.BOLD,
                        color="#202026"
                    ),
                    ft.Text(
                        description,
                        size=13,
                        color="#777780"
                    )
                ],
                spacing=4
            )
        )

    def stat_card(self, icon, title, value, subtitle):
        return ft.Container(
            expand=True,
            bgcolor="white",
            border_radius=20,
            padding=20,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"{icon}  {title}",
                        size=12,
                        color="#777780"
                    ),
                    ft.Text(
                        value,
                        size=25,
                        weight=ft.FontWeight.BOLD,
                        color="#202026"
                    ),
                    ft.Text(
                        subtitle,
                        size=11,
                        color="#9999A0"
                    )
                ],
                spacing=6
            )
        )

    def info_row(self, icon, title, value):
        return ft.Container(
            padding=12,
            content=ft.Row(
                controls=[
                    ft.Text(
                        icon,
                        size=20
                    ),
                    ft.Text(
                        title,
                        size=13,
                        color="#66666E",
                        expand=True
                    ),
                    ft.Text(
                        str(value),
                        size=14,
                        weight=ft.FontWeight.BOLD
                    )
                ]
            )
        )

    def parse_tags(self, tag_text):
        tag_text = (
            tag_text
            or ""
        ).strip()

        if not tag_text:
            return []

        tags = []

        for item in tag_text.split():
            item = item.strip()

            if not item.startswith("#"):
                raise ValueError(
                    "태그는 #을 붙여 입력해주세요. "
                    "예: #일상 #친구 #학교"
                )

            tag = item[1:].strip()

            if not tag:
                raise ValueError(
                    "# 뒤에 태그 내용을 입력해주세요."
                )

            if "#" in tag:
                raise ValueError(
                    "태그는 띄어쓰기로 구분해주세요. "
                    "예: #일상 #친구"
                )

            if tag not in tags:
                tags.append(tag)

        return tags

    def validate_key(self, method, key):
        if method == SHIFT:
            try:
                key = int(key)
            except (ValueError, TypeError):
                raise ValueError(
                    "SHIFT Key는 1~25의 정수여야 합니다."
                )

            if key < 1 or key > 25:
                raise ValueError(
                    "SHIFT Key는 1~25의 정수여야 합니다."
                )

            return key

        if method == KEYWORD:
            key = str(key).strip()

            if not key:
                raise ValueError(
                    "Keyword를 입력해주세요."
                )

            if not key.isascii() or not key.isalpha():
                raise ValueError(
                    "Keyword는 영문 알파벳만 입력할 수 있습니다."
                )

            return key

        raise ValueError(
            "지원하지 않는 암호 방식입니다."
        )

    def get_weekday_encryption_rule(self, date_string):
        try:
            selected_date = datetime.strptime(
                date_string,
                "%Y-%m-%d"
            )
        except ValueError:
            raise ValueError(
                "날짜는 YYYY-MM-DD 형식으로 입력해주세요."
            )

        weekday = selected_date.weekday()

        return self.weekday_rules[weekday]

    def add_history(self, category, action, method):
        current_time = get_current_datetime()

        record = (
            current_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            + f" | {category}"
            + f" | {action}"
            + f" | {method}"
            + " | SUCCESS"
        )

        self.session_history.append(record)

    def create_memory_card(self, diary):
        tags = " ".join(
            f"#{tag}"
            for tag in diary.get(
                "tags",
                []
            )
        )

        encrypted = diary.get(
            "is_encrypted",
            False
        )

        return ft.Container(
            bgcolor="#FAFAFC",
            border_radius=16,
            padding=16,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Row(
                controls=[
                    ft.Text(
                        diary.get(
                            "mood",
                            "😊"
                        ),
                        size=27
                    ),

                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    diary.get(
                                        "title",
                                        "제목 없음"
                                    ),
                                    size=15,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    diary.get(
                                        "date",
                                        ""
                                    ),
                                    size=11,
                                    color="#888890"
                                ),

                                ft.Text(
                                    tags or "태그 없음",
                                    size=11,
                                    color="#676B84"
                                ),

                                ft.Text(
                                    (
                                        "🔒 비밀 기록"
                                        if encrypted
                                        else "📖 일반 기록"
                                    ),
                                    size=10,
                                    color="#9999A0"
                                )
                            ],
                            spacing=3
                        )
                    ),

                    ft.FilledButton(
                        (
                            "🔑 열어보기"
                            if encrypted
                            else "다시 보기"
                        ),
                        on_click=lambda e, item=diary:
                        self.open_memory_from_home(
                            item
                        )
                    )
                ],
                spacing=14
            )
        )

    def open_memory_from_home(self, diary):
        self.selected_calendar_date = (
            diary["date"]
        )

        try:
            selected_date = datetime.strptime(
                diary["date"],
                "%Y-%m-%d"
            )

            self.calendar_year = (
                selected_date.year
            )

            self.calendar_month = (
                selected_date.month
            )

        except ValueError:
            self.show_error(
                "일기 날짜 정보가 올바르지 않습니다."
            )
            return

        self.show_diary_detail(
            diary["id"]
        )

    def show_home(self):
        summary = get_statistics_summary()
        today = get_today_string()
        today_text = today

        if is_demo_mode():
            today_text += "  ·  시연 모드"

        today_diaries = get_diaries_by_date(today)
        memories = get_one_year_ago_memories()
        capsules = get_all_capsules()
        available_capsules = []

        for capsule in capsules:
            try:
                if get_capsule_status(capsule["id"]) == "열람 가능":
                    available_capsules.append(capsule)
            except (ValueError, KeyError):
                continue

        cards = ft.Row(
            controls=[
                self.stat_card("📖", "전체 기록", f"{summary['total_diaries']}개", "지금까지 기록한 하루"),
                self.stat_card("🔥", "연속 기록", f"{summary['current_streak']}일", "꾸준히 기록 중"),
                self.stat_card("😊", "대표 기분", summary["most_common_mood"] or "-", "가장 자주 기록한 기분"),
                self.stat_card("🔒", "비밀 기록", f"{summary['encrypted_ratio']}%", "본문 암호화 비율")
            ],
            spacing=15
        )

        alert_controls = []

        if not today_diaries:
            alert_controls.append(
                self.home_alert_card(
                    "✏️", "오늘의 기록이 아직 없어요",
                    "오늘 있었던 일을 남겨보세요.",
                    "일기 쓰기", self.show_write_diary
                )
            )
        else:
            alert_controls.append(
                self.home_alert_card(
                    "✅", "오늘의 기록을 남겼어요",
                    f"오늘 작성한 일기가 {len(today_diaries)}개 있어요.",
                    "캘린더 보기", self.show_calendar
                )
            )

        if available_capsules:
            alert_controls.append(
                self.home_alert_card(
                    "💌", "열어볼 수 있는 타임캡슐이 있어요",
                    f"공개 날짜가 된 타임캡슐이 {len(available_capsules)}개 있어요.",
                    "타임캡슐 보기", self.show_capsule
                )
            )

        if memories:
            alert_controls.append(
                self.home_alert_card(
                    "🕰️", "1년 전 오늘의 기록이 있어요",
                    f"과거의 오늘에 작성한 기록 {len(memories)}개를 다시 만나보세요.",
                    "추억 보기", lambda: self.open_memory_from_home(memories[0])
                )
            )

        notification_card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=22,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[
                    ft.Text("오늘의 알림", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("현재 날짜에 맞춰 필요한 기록을 알려드려요.", size=11, color="#777780"),
                    *alert_controls
                ],
                spacing=10
            )
        )

        write_card = ft.Container(
            bgcolor="white", border_radius=22, padding=25,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Row(
                controls=[
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text("오늘의 이야기", size=19, weight=ft.FontWeight.BOLD),
                                ft.Text("오늘 있었던 일과 감정을 나만의 공간에 기록해보세요.", size=13, color="#777780")
                            ], spacing=5
                        )
                    ),
                    ft.FilledButton("＋ 오늘 일기 쓰기", on_click=lambda e: self.show_write_diary())
                ]
            )
        )

        memory_controls = [
            ft.Row(
                controls=[
                    ft.Text("🕰️", size=25),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text("1년 전 오늘", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text("과거의 오늘에는 어떤 하루를 보냈을까요?", size=11, color="#777780")
                            ], spacing=2
                        )
                    )
                ], spacing=10
            )
        ]

        if memories:
            for diary in memories:
                memory_controls.append(self.create_memory_card(diary))
        else:
            past_year = get_today().year - 1
            memory_controls.append(
                ft.Container(
                    height=85, alignment=ft.Alignment.CENTER,
                    content=ft.Text(f"{past_year}년 오늘의 기록은 아직 없습니다. ☁️", size=12, color="#9999A0")
                )
            )

        memory_card = ft.Container(
            bgcolor="white", border_radius=22, padding=22,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(controls=memory_controls, spacing=12)
        )

        privacy_card = ft.Container(
            bgcolor="#F0F2F8", border_radius=22, padding=22,
            content=ft.Row(
                controls=[
                    ft.Text("🔐", size=27),
                    ft.Column(
                        controls=[
                            ft.Text("나만 볼 수 있는 기록", size=15, weight=ft.FontWeight.BOLD),
                            ft.Text("비밀 일기로 저장하면 날짜, 제목, 기분, 태그는 유지하고 본문만 암호화합니다.", size=12, color="#696973")
                        ], spacing=3
                    )
                ], spacing=15
            )
        )

        self.change_page([
            self.page_header("오늘도 기록해볼까요? ☁️", today_text),
            cards,
            notification_card,
            write_card,
            memory_card,
            privacy_card
        ])

    def home_alert_card(self, icon, title, description, button_text, command):
        return ft.Container(
            bgcolor="#F8F8FB",
            border_radius=14,
            padding=14,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Row(
                controls=[
                    ft.Text(icon, size=22),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text(title, size=13, weight=ft.FontWeight.BOLD),
                                ft.Text(description, size=11, color="#777780")
                            ], spacing=2
                        )
                    ),
                    ft.TextButton(button_text, on_click=lambda e: command())
                ],
                spacing=12
            )
        )

    def show_write_diary(self):
        date_field = ft.TextField(
            label="날짜",
            value=get_today_string(),
            hint_text="YYYY-MM-DD",
            border_radius=14,
            expand=True
        )

        mood_dropdown = ft.Dropdown(
            label="오늘의 기분",
            value="😊",
            options=[
                ft.DropdownOption(
                    key="😊",
                    text="😊  행복해요"
                ),
                ft.DropdownOption(
                    key="😄",
                    text="😄  신나요"
                ),
                ft.DropdownOption(
                    key="😐",
                    text="😐  평범해요"
                ),
                ft.DropdownOption(
                    key="😢",
                    text="😢  슬퍼요"
                ),
                ft.DropdownOption(
                    key="😡",
                    text="😡  화나요"
                ),
                ft.DropdownOption(
                    key="😴",
                    text="😴  피곤해요"
                )
            ],
            border_radius=14,
            expand=True
        )

        title_field = ft.TextField(
            label="제목",
            hint_text="오늘 하루에 제목을 붙여보세요.",
            border_radius=14
        )

        tag_field = ft.TextField(
            label="태그",
            hint_text="#일상 #친구 #학교",
            border_radius=14
        )

        tag_help_text = ft.Text(
            "#을 붙인 태그를 띄어쓰기로 구분해주세요. "
            "예: #일상 #친구 #학교",
            size=11,
            color="#888890"
        )

        content_field = ft.TextField(
            label="오늘의 이야기",
            hint_text="오늘 있었던 일을 자유롭게 기록하세요...",
            multiline=True,
            min_lines=7,
            max_lines=12,
            border_radius=16
        )

        self.method_dropdown = ft.Dropdown(
            label="암호 방식",
            value=SHIFT,
            options=[
                ft.DropdownOption(
                    key=SHIFT,
                    text="SHIFT"
                ),
                ft.DropdownOption(
                    key=KEYWORD,
                    text="KEYWORD"
                )
            ],
            border_radius=14,
            expand=True,
            on_select=self.change_encryption_method
        )

        self.key_field = ft.TextField(
            label="Key",
            value="3",
            password=True,
            can_reveal_password=True,
            border_radius=14,
            expand=True
        )

        self.key_help_text = ft.Text(
            "SHIFT Key는 1~25의 정수를 입력해주세요.",
            size=11,
            color="#888890"
        )

        auto_rule_text = ft.Text(
            "",
            size=11,
            color="#676B84"
        )

        def apply_weekday_rule():
            if not self.weekday_auto_encryption:
                auto_rule_text.value = ""
                return

            date_text = (
                date_field.value
                or ""
            ).strip()

            try:
                selected_date = datetime.strptime(
                    date_text,
                    "%Y-%m-%d"
                )

                rule = self.get_weekday_encryption_rule(
                    date_text
                )

                weekday_names = [
                    "월요일",
                    "화요일",
                    "수요일",
                    "목요일",
                    "금요일",
                    "토요일",
                    "일요일"
                ]

                weekday_name = weekday_names[
                    selected_date.weekday()
                ]

                self.method_dropdown.value = (
                    rule["method"]
                )

                self.key_field.value = str(
                    rule["key"]
                )

                if rule["method"] == SHIFT:
                    self.key_field.label = "Key"

                    self.key_help_text.value = (
                        "SHIFT Key는 1~25의 정수를 입력해주세요."
                    )
                else:
                    self.key_field.label = "Keyword"

                    self.key_help_text.value = (
                        "Keyword는 영문 알파벳만 입력해주세요."
                    )

                auto_rule_text.value = (
                    f"⚙️ {weekday_name} 자동 규칙 적용: "
                    f"{rule['method']} / {rule['key']}"
                )

            except ValueError:
                auto_rule_text.value = (
                    "날짜를 YYYY-MM-DD 형식으로 입력하면 "
                    "요일별 규칙이 적용됩니다."
                )

        def date_changed(e):
            if not self.weekday_auto_encryption:
                return

            apply_weekday_rule()

            self.method_dropdown.update()
            self.key_field.update()
            self.key_help_text.update()
            auto_rule_text.update()

        date_field.on_change = (
            date_changed
        )

        self.encryption_options = ft.Container(
            visible=False,
            margin=ft.Margin(
                left=0,
                right=0,
                top=12,
                bottom=0
            ),
            padding=18,
            border_radius=16,
            bgcolor="#F8F8FB",
            border=ft.Border.all(
                1,
                "#E7E7EC"
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "암호화 설정",
                        size=14,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text(
                        "암호 방식과 Key를 설정해주세요.",
                        size=11,
                        color="#777780"
                    ),

                    ft.Row(
                        controls=[
                            self.method_dropdown,
                            self.key_field
                        ],
                        spacing=12
                    ),

                    self.key_help_text,

                    auto_rule_text,

                    ft.Text(
                        "✓ 저장 시 암호화 → 복호화 "
                        "자동 검증을 수행합니다.",
                        size=11,
                        color="#66666E"
                    )
                ],
                spacing=10
            )
        )

        def encryption_changed(e):
            self.encryption_options.visible = bool(
                self.encryption_switch.value
            )

            if (
                self.encryption_switch.value
                and self.weekday_auto_encryption
            ):
                apply_weekday_rule()

            self.encryption_options.update()

        self.encryption_switch = ft.Switch(
            value=False,
            on_change=encryption_changed
        )

        security_card = ft.Container(
            border_radius=18,
            border=ft.Border.all(
                1,
                "#E7E7EC"
            ),
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "🔒 비밀 일기로 저장",
                                            size=14,
                                            weight=ft.FontWeight.BOLD
                                        ),

                                        ft.Text(
                                            "날짜, 제목, 기분, 태그는 그대로 두고 "
                                            "일기 본문만 암호화합니다.",
                                            size=11,
                                            color="#777780"
                                        )
                                    ],
                                    spacing=3
                                )
                            ),

                            self.encryption_switch
                        ]
                    ),

                    self.encryption_options
                ]
            )
        )

        def save_diary(e):
            date = (
                date_field.value
                or ""
            ).strip()

            title = (
                title_field.value
                or ""
            ).strip()

            content = (
                content_field.value
                or ""
            ).strip()

            mood = (
                mood_dropdown.value
                or "😊"
            )

            try:
                datetime.strptime(
                    date,
                    "%Y-%m-%d"
                )
            except ValueError:
                self.show_error(
                    "날짜는 YYYY-MM-DD 형식으로 입력해주세요."
                )
                return

            try:
                tags = self.parse_tags(
                    tag_field.value
                )
            except ValueError as error:
                self.show_error(
                    str(error)
                )
                return

            if not title:
                self.show_error(
                    "일기 제목을 입력해주세요."
                )
                return

            if not content:
                self.show_error(
                    "일기 내용을 입력해주세요."
                )
                return

            encrypted = bool(
                self.encryption_switch.value
            )

            method = (
                self.method_dropdown.value
                or SHIFT
            )

            key = (
                self.key_field.value
                or ""
            ).strip()

            if encrypted:
                try:
                    key = self.validate_key(
                        method,
                        key
                    )
                except ValueError as error:
                    self.show_error(
                        str(error)
                    )
                    return

            try:
                create_diary(
                    date=date,
                    title=title,
                    content=content,
                    mood=mood,
                    tags=tags,
                    is_encrypted=encrypted,
                    method=method,
                    key=key
                )

                if encrypted:
                    self.add_history(
                        "일기",
                        "암호화",
                        method
                    )

                self.show_success(
                    "오늘의 기록을 안전하게 저장했어요."
                )

                self.show_home()

            except Exception as error:
                self.show_error(
                    str(error)
                )

        form_card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=25,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            date_field,
                            mood_dropdown
                        ],
                        spacing=15
                    ),

                    title_field,

                    ft.Column(
                        controls=[
                            tag_field,
                            tag_help_text
                        ],
                        spacing=4
                    ),

                    content_field,

                    security_card,

                    ft.Row(
                        controls=[
                            ft.TextButton(
                                "취소",
                                on_click=lambda e:
                                self.show_home()
                            ),

                            ft.FilledButton(
                                "기록 저장하기",
                                on_click=save_diary
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10
                    )
                ],
                spacing=15
            )
        )

        if self.weekday_auto_encryption:
            apply_weekday_rule()

        self.change_page(
            [
                self.page_header(
                    "오늘의 이야기 ✏️",
                    "새로운 하루를 기록해보세요."
                ),

                form_card
            ]
        )

    def toggle_encryption(self, e):
        if self.encryption_options is None:
            return

        self.encryption_options.visible = bool(
            self.encryption_switch.value
        )

        self.encryption_options.update()

    def change_encryption_method(self, e):
        if (
            self.method_dropdown is None
            or self.key_field is None
            or self.key_help_text is None
        ):
            return

        method = (
            self.method_dropdown.value
        )

        if method == SHIFT:
            self.key_field.label = "Key"
            self.key_field.value = "3"

            self.key_help_text.value = (
                "SHIFT Key는 1~25의 정수를 입력해주세요."
            )
        else:
            self.key_field.label = "Keyword"
            self.key_field.value = ""

            self.key_help_text.value = (
                "Keyword는 한 글자 이상의 "
                "영문 알파벳만 입력해주세요."
            )

        self.key_field.update()
        self.key_help_text.update()

    def show_calendar(self):
        month_calendar = calendar.monthcalendar(
            self.calendar_year,
            self.calendar_month
        )

        calendar_rows = [
            ft.Row(
                controls=[
                    self.weekday_box(day)
                    for day in [
                        "월",
                        "화",
                        "수",
                        "목",
                        "금",
                        "토",
                        "일"
                    ]
                ],
                spacing=5
            )
        ]

        for week in month_calendar:
            day_controls = []

            for day in week:
                if day == 0:
                    day_controls.append(
                        ft.Container(
                            expand=True,
                            height=90
                        )
                    )
                    continue

                date_string = (
                    f"{self.calendar_year:04d}-"
                    f"{self.calendar_month:02d}-"
                    f"{day:02d}"
                )

                day_controls.append(
                    self.create_calendar_day(
                        day,
                        date_string
                    )
                )

            calendar_rows.append(
                ft.Row(
                    controls=day_controls,
                    spacing=5
                )
            )

        calendar_card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=22,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                "‹ 이전",
                                on_click=self.previous_month
                            ),

                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    f"{self.calendar_year}년 "
                                    f"{self.calendar_month}월",
                                    size=21,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER
                                )
                            ),

                            ft.TextButton(
                                "다음 ›",
                                on_click=self.next_month
                            )
                        ]
                    ),

                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True
                            ),

                            ft.TextButton(
                                "오늘로 이동",
                                on_click=self.go_today_calendar
                            )
                        ]
                    ),

                    ft.Divider(
                        color="#EEEEF2"
                    ),

                    *calendar_rows
                ],
                spacing=8
            )
        )

        self.change_page(
            [
                self.page_header(
                    "캘린더 📅",
                    "기록한 하루를 한눈에 확인합니다."
                ),

                calendar_card,

                ft.Container(
                    height=5
                ),

                self.create_selected_date_panel()
            ]
        )

    def weekday_box(self, text):
        return ft.Container(
            expand=True,
            height=30,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(
                text,
                size=12,
                weight=ft.FontWeight.BOLD,
                color="#777780"
            )
        )

    def create_calendar_day(
        self,
        day,
        date_string
    ):
        diaries = get_diaries_by_date(
            date_string
        )

        is_today = (
            date_string
            == get_today_string()
        )

        is_selected = (
            date_string
            == self.selected_calendar_date
        )

        if is_selected:
            background = "#E9ECF8"
        elif is_today:
            background = "#F1F4FF"
        else:
            background = "white"

        indicators = []

        if diaries:
            moods = []

            for diary in diaries:
                mood = diary.get(
                    "mood",
                    ""
                )

                if (
                    mood
                    and mood not in moods
                ):
                    moods.append(
                        mood
                    )

            if moods:
                indicators.append(
                    ft.Text(
                        "".join(
                            moods[:3]
                        ),
                        size=14
                    )
                )

            status = (
                f"{len(diaries)}개"
            )

            if any(
                diary.get(
                    "is_encrypted",
                    False
                )
                for diary in diaries
            ):
                status += "  🔒"

            indicators.append(
                ft.Text(
                    status,
                    size=10,
                    color="#777780"
                )
            )

        return ft.Container(
            expand=True,
            height=90,
            padding=8,
            border_radius=12,
            bgcolor=background,
            border=ft.Border.all(
                1,
                (
                    "#9098C8"
                    if is_selected
                    else "#ECECF0"
                )
            ),
            on_click=lambda e, selected=date_string:
            self.select_calendar_date(
                selected
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        str(day),
                        size=13,
                        weight=(
                            ft.FontWeight.BOLD
                            if is_today
                            else ft.FontWeight.NORMAL
                        )
                    ),
                    *indicators
                ],
                spacing=4
            )
        )

    def select_calendar_date(
        self,
        date_string
    ):
        self.selected_calendar_date = (
            date_string
        )

        self.show_calendar()

    def previous_month(self, e):
        self.calendar_month -= 1

        if self.calendar_month < 1:
            self.calendar_month = 12
            self.calendar_year -= 1

        self.selected_calendar_date = (
            f"{self.calendar_year:04d}-"
            f"{self.calendar_month:02d}-01"
        )

        self.show_calendar()

    def next_month(self, e):
        self.calendar_month += 1

        if self.calendar_month > 12:
            self.calendar_month = 1
            self.calendar_year += 1

        self.selected_calendar_date = (
            f"{self.calendar_year:04d}-"
            f"{self.calendar_month:02d}-01"
        )

        self.show_calendar()

    def go_today_calendar(self, e):
        today = get_today()

        self.calendar_year = (
            today.year
        )

        self.calendar_month = (
            today.month
        )

        self.selected_calendar_date = (
            get_today_string()
        )

        self.show_calendar()

    def create_selected_date_panel(self):
        diaries = get_diaries_by_date(
            self.selected_calendar_date
        )

        controls = [
            ft.Row(
                controls=[
                    ft.Text(
                        f"📝 {self.selected_calendar_date}",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        expand=True
                    ),

                    ft.Text(
                        f"{len(diaries)}개의 기록",
                        size=12,
                        color="#777780"
                    )
                ]
            )
        ]

        if not diaries:
            controls.append(
                ft.Container(
                    height=100,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        "이날 작성한 일기가 없습니다. ☁️",
                        size=13,
                        color="#888890"
                    )
                )
            )
        else:
            for diary in diaries:
                controls.append(
                    self.create_diary_card(
                        diary
                    )
                )

        return ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=22,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=controls,
                spacing=12
            )
        )

    def create_diary_card(
        self,
        diary
    ):
        tags = " ".join(
            f"#{tag}"
            for tag in diary.get(
                "tags",
                []
            )
        )

        encrypted = diary.get(
            "is_encrypted",
            False
        )

        if encrypted:
            status = (
                "🔒 비밀 일기 · "
                + str(
                    diary.get(
                        "encryption_method",
                        ""
                    )
                )
            )
        else:
            status = (
                "📖 일반 일기"
            )

        return ft.Container(
            padding=18,
            border_radius=16,
            bgcolor="#FAFAFC",
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Row(
                controls=[
                    ft.Text(
                        diary.get(
                            "mood",
                            "😊"
                        ),
                        size=26
                    ),

                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    diary.get(
                                        "title",
                                        "제목 없음"
                                    ),
                                    size=15,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    tags
                                    or "태그 없음",
                                    size=11,
                                    color="#6F7180"
                                ),

                                ft.Text(
                                    status,
                                    size=10,
                                    color="#92929A"
                                )
                            ],
                            spacing=4
                        )
                    ),

                    ft.FilledButton(
                        (
                            "🔑 열기"
                            if encrypted
                            else "내용 보기"
                        ),
                        on_click=lambda e, diary_id=diary["id"]:
                        self.show_diary_detail(
                            diary_id
                        )
                    )
                ],
                spacing=14
            )
        )

    def show_diary_detail(
        self,
        diary_id
    ):
        diaries = get_diaries_by_date(
            self.selected_calendar_date
        )

        diary = next(
            (
                item
                for item in diaries
                if item.get(
                    "id"
                ) == diary_id
            ),
            None
        )

        if diary is None:
            self.show_error(
                "일기를 찾을 수 없습니다."
            )
            return

        if diary.get(
            "is_encrypted",
            False
        ):
            self.show_locked_diary(
                diary
            )
        else:
            self.show_open_diary(
                diary,
                diary.get(
                    "content",
                    ""
                )
            )

    def show_locked_diary(
        self,
        diary
    ):
        method = diary.get(
            "encryption_method",
            SHIFT
        )

        key_field = ft.TextField(
            label=(
                "SHIFT Key"
                if method == SHIFT
                else "Keyword"
            ),
            password=True,
            can_reveal_password=True,
            border_radius=14
        )

        error_text = ft.Text(
            "",
            size=11,
            color="#B54A4A"
        )

        def unlock(e):
            try:
                key = self.validate_key(
                    method,
                    (
                        key_field.value
                        or ""
                    ).strip()
                )

                content = open_diary(
                    diary["id"],
                    key
                )

                self.add_history(
                    "일기",
                    "복호화",
                    method
                )

                self.show_open_diary(
                    diary,
                    content
                )

            except Exception as error:
                error_text.value = (
                    str(error)
                )
                error_text.update()

        tags = " ".join(
            f"#{tag}"
            for tag in diary.get(
                "tags",
                []
            )
        )

        controls = [
            ft.Text(
                "🔐",
                size=45
            ),

            ft.Text(
                "잠긴 일기",
                size=22,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "저장할 때 사용한 Key를 입력하면 "
                "본문을 복호화할 수 있습니다.",
                size=12,
                color="#777780"
            ),

            ft.Divider(
                color="#EEEEF2"
            ),

            self.info_row(
                "📅",
                "날짜",
                diary.get(
                    "date",
                    "-"
                )
            ),

            self.info_row(
                diary.get(
                    "mood",
                    "😊"
                ),
                "제목",
                diary.get(
                    "title",
                    "-"
                )
            ),

            self.info_row(
                "#",
                "태그",
                tags or "-"
            ),

            self.info_row(
                "🔐",
                "암호 방식",
                method
            )
        ]

        if diary.get(
            "content_hash"
        ) is None:
            controls.append(
                ft.Container(
                    bgcolor="#FFF8EB",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(
                        "⚠ 이전 테스트 데이터입니다. "
                        "Key 정확성 검증 정보가 없는 기록입니다.",
                        size=11,
                        color="#75694F"
                    )
                )
            )

        controls.extend(
            [
                key_field,

                error_text,

                ft.Row(
                    controls=[
                        ft.TextButton(
                            "캘린더로 돌아가기",
                            on_click=lambda e:
                            self.show_calendar()
                        ),

                        ft.FilledButton(
                            "🔓 일기 열기",
                            on_click=unlock
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10
                )
            ]
        )

        card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=30,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=controls,
                spacing=12
            )
        )

        self.change_page(
            [
                self.page_header(
                    "비밀 일기 🔐",
                    diary.get(
                        "date",
                        ""
                    )
                ),

                card
            ]
        )

    def show_open_diary(
        self,
        diary,
        content
    ):
        tags = " ".join(
            f"#{tag}"
            for tag in diary.get(
                "tags",
                []
            )
        )

        card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=28,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                diary.get(
                                    "mood",
                                    "😊"
                                ),
                                size=32
                            ),

                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            diary.get(
                                                "title",
                                                "제목 없음"
                                            ),
                                            size=23,
                                            weight=ft.FontWeight.BOLD
                                        ),

                                        ft.Text(
                                            diary.get(
                                                "date",
                                                ""
                                            ),
                                            size=12,
                                            color="#888890"
                                        )
                                    ],
                                    spacing=3
                                )
                            )
                        ]
                    ),

                    ft.Text(
                        tags
                        or "태그 없음",
                        size=12,
                        color="#676B84"
                    ),

                    ft.Divider(
                        color="#EEEEF2"
                    ),

                    ft.Container(
                        padding=15,
                        content=ft.Text(
                            content,
                            size=15,
                            color="#303038"
                        )
                    ),

                    ft.Divider(
                        color="#EEEEF2"
                    ),

                    ft.Row(
                        controls=[
                            ft.TextButton(
                                "← 캘린더로 돌아가기",
                                on_click=lambda e: self.show_calendar()
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                "✏️ 수정",
                                on_click=lambda e: self.start_edit_diary(diary, content)
                            ),
                            ft.TextButton(
                                "🗑️ 삭제",
                                on_click=lambda e: self.show_delete_diary(diary)
                            )
                        ],
                        spacing=8
                    )
                ],
                spacing=12
            )
        )

        self.change_page(
            [
                self.page_header(
                    "나의 기록 📖",
                    "기록해둔 하루를 다시 읽어보세요."
                ),

                card
            ]
        )

    def show_search(self):
        title_field = ft.TextField(label="제목 검색", hint_text="제목에 포함된 단어", border_radius=14, expand=True)
        tag_field = ft.TextField(label="태그", hint_text="예: 학교", border_radius=14, expand=True)
        date_field = ft.TextField(label="날짜", hint_text="YYYY-MM-DD", border_radius=14, expand=True)
        mood_dropdown = ft.Dropdown(
            label="기분",
            value="ALL",
            options=[
                ft.DropdownOption(key="ALL", text="전체"),
                ft.DropdownOption(key="😊", text="😊 행복해요"),
                ft.DropdownOption(key="😄", text="😄 신나요"),
                ft.DropdownOption(key="😐", text="😐 평범해요"),
                ft.DropdownOption(key="😢", text="😢 슬퍼요"),
                ft.DropdownOption(key="😡", text="😡 화나요"),
                ft.DropdownOption(key="😴", text="😴 피곤해요")
            ],
            border_radius=14,
            expand=True
        )
        lock_dropdown = ft.Dropdown(
            label="공개 상태",
            value="ALL",
            options=[
                ft.DropdownOption(key="ALL", text="전체"),
                ft.DropdownOption(key="NORMAL", text="일반 일기"),
                ft.DropdownOption(key="SECRET", text="비밀 일기")
            ],
            border_radius=14,
            expand=True
        )
        result_column = ft.Column(controls=[], spacing=10)
        result_count = ft.Text("", size=11, color="#777780")

        def result_card(diary):
            tags = " ".join(f"#{tag}" for tag in diary.get("tags", [])) or "태그 없음"
            encrypted = diary.get("is_encrypted", False)
            return ft.Container(
                bgcolor="#FAFAFC",
                border_radius=16,
                padding=16,
                border=ft.Border.all(1, "#ECECF0"),
                content=ft.Row(
                    controls=[
                        ft.Text(diary.get("mood", "😊"), size=26),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                controls=[
                                    ft.Text(diary.get("title", "제목 없음"), size=15, weight=ft.FontWeight.BOLD),
                                    ft.Text(diary.get("date", ""), size=11, color="#888890"),
                                    ft.Text(tags, size=11, color="#676B84"),
                                    ft.Text("🔒 비밀 일기" if encrypted else "📖 일반 일기", size=10, color="#9999A0")
                                ],
                                spacing=3
                            )
                        ),
                        ft.FilledButton(
                            "🔑 열기" if encrypted else "내용 보기",
                            on_click=lambda e, item=diary: self.open_search_result(item)
                        )
                    ],
                    spacing=12
                )
            )

        def run_search(e=None):
            date_value = (date_field.value or "").strip()
            if date_value:
                try:
                    datetime.strptime(date_value, "%Y-%m-%d")
                except ValueError:
                    self.show_error("날짜는 YYYY-MM-DD 형식으로 입력해주세요.")
                    return
            tag_value = (tag_field.value or "").strip()
            if tag_value.startswith("#"):
                tag_value = tag_value[1:]
            lock_value = lock_dropdown.value or "ALL"
            encrypted_filter = None
            if lock_value == "NORMAL":
                encrypted_filter = False
            elif lock_value == "SECRET":
                encrypted_filter = True
            results = search_diaries(
                title=(title_field.value or "").strip() or None,
                tag=tag_value or None,
                mood=None if mood_dropdown.value == "ALL" else mood_dropdown.value,
                date=date_value or None,
                is_encrypted=encrypted_filter
            )
            results = sorted(results, key=lambda item: (item.get("date", ""), item.get("id", 0)), reverse=True)
            if results:
                result_column.controls = [result_card(item) for item in results]
            else:
                result_column.controls = [
                    ft.Container(height=150, alignment=ft.Alignment.CENTER, content=ft.Text("조건에 맞는 일기가 없습니다. ☁️", color="#888890"))
                ]
            result_count.value = f"검색 결과 {len(results)}개"
            result_column.update()
            result_count.update()

        def reset_search(e):
            title_field.value = ""
            tag_field.value = ""
            date_field.value = ""
            mood_dropdown.value = "ALL"
            lock_dropdown.value = "ALL"
            title_field.update(); tag_field.update(); date_field.update(); mood_dropdown.update(); lock_dropdown.update()
            run_search()

        filter_card = ft.Container(
            bgcolor="white", border_radius=22, padding=22, border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[
                    ft.Text("검색 조건", size=17, weight=ft.FontWeight.BOLD),
                    ft.Row(controls=[title_field, tag_field, date_field], spacing=12),
                    ft.Row(controls=[mood_dropdown, lock_dropdown], spacing=12),
                    ft.Row(
                        controls=[ft.FilledButton("🔎 검색", on_click=run_search), ft.TextButton("조건 초기화", on_click=reset_search)],
                        alignment=ft.MainAxisAlignment.END, spacing=8
                    ),
                    ft.Text("비밀 일기의 본문은 암호화되어 있으므로 제목·태그·날짜·기분·공개 상태만 검색합니다.", size=11, color="#888890")
                ], spacing=12
            )
        )
        result_card_box = ft.Container(
            bgcolor="white", border_radius=22, padding=22, border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[ft.Row(controls=[ft.Text("일기 목록", size=18, weight=ft.FontWeight.BOLD), ft.Container(expand=True), result_count]), ft.Divider(color="#EEEEF2"), result_column],
                spacing=10
            )
        )
        self.change_page([self.page_header("일기 찾기 🔎", "제목, 태그, 날짜, 기분과 공개 상태로 기록을 찾아보세요."), filter_card, result_card_box])
        run_search()

    def open_search_result(self, diary):
        self.selected_calendar_date = diary.get("date", get_today_string())
        try:
            selected = datetime.strptime(self.selected_calendar_date, "%Y-%m-%d")
            self.calendar_year = selected.year
            self.calendar_month = selected.month
        except ValueError:
            pass
        self.show_diary_detail(diary["id"])

    def start_edit_diary(self, diary, content=None):
        if diary.get("is_encrypted", False) and content is None:
            method = diary.get("encryption_method", SHIFT)
            key_field = ft.TextField(label="SHIFT Key" if method == SHIFT else "Keyword", password=True, can_reveal_password=True, border_radius=14)
            error_text = ft.Text("", size=11, color="#B54A4A")
            def unlock_edit(e):
                try:
                    key = self.validate_key(method, (key_field.value or "").strip())
                    plain = open_diary(diary["id"], key)
                    self.show_edit_diary(diary, plain, key)
                except Exception as error:
                    error_text.value = str(error); error_text.update()
            card = ft.Container(
                bgcolor="white", border_radius=22, padding=28, border=ft.Border.all(1, "#ECECF0"),
                content=ft.Column(controls=[ft.Text("🔐", size=40), ft.Text("수정하려면 먼저 잠금을 해제해주세요.", size=18, weight=ft.FontWeight.BOLD), key_field, error_text, ft.Row(controls=[ft.TextButton("취소", on_click=lambda e: self.show_calendar()), ft.FilledButton("잠금 해제 후 수정", on_click=unlock_edit)], alignment=ft.MainAxisAlignment.END)], spacing=12)
            )
            self.change_page([self.page_header("비밀 일기 수정 ✏️", diary.get("date", "")), card])
            return
        self.show_edit_diary(diary, content if content is not None else diary.get("content", ""), None)

    def show_edit_diary(self, diary, plain_content, original_key=None):
        date_field = ft.TextField(label="날짜", value=diary.get("date", ""), border_radius=14, expand=True)
        mood_dropdown = ft.Dropdown(
            label="기분", value=diary.get("mood", "😊"),
            options=[ft.DropdownOption(key=x, text=x) for x in ["😊", "😄", "😐", "😢", "😡", "😴"]], border_radius=14, expand=True
        )
        title_field = ft.TextField(label="제목", value=diary.get("title", ""), border_radius=14)
        tag_field = ft.TextField(label="태그", value=" ".join(f"#{x}" for x in diary.get("tags", [])), border_radius=14)
        content_field = ft.TextField(label="일기 내용", value=plain_content, multiline=True, min_lines=7, max_lines=12, border_radius=16)
        encrypted_switch = ft.Switch(value=diary.get("is_encrypted", False))
        method_dropdown = ft.Dropdown(
            label="암호 방식", value=diary.get("encryption_method") or SHIFT,
            options=[ft.DropdownOption(key=SHIFT, text="SHIFT"), ft.DropdownOption(key=KEYWORD, text="KEYWORD")], border_radius=14, expand=True
        )
        key_field = ft.TextField(
            label="Key / Keyword", value=str(original_key) if original_key is not None else "3",
            password=True, can_reveal_password=True, border_radius=14, expand=True
        )
        encryption_box = ft.Container(
            visible=bool(encrypted_switch.value), bgcolor="#F8F8FB", border_radius=14, padding=15,
            content=ft.Column(controls=[ft.Row(controls=[method_dropdown, key_field], spacing=12), ft.Text("암호화 상태로 저장하려면 사용할 Key를 입력해주세요.", size=11, color="#888890")], spacing=8)
        )
        def toggle(e):
            encryption_box.visible = bool(encrypted_switch.value); encryption_box.update()
        encrypted_switch.on_change = toggle
        def save(e):
            date_value = (date_field.value or "").strip()
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                self.show_error("날짜는 YYYY-MM-DD 형식으로 입력해주세요."); return
            try:
                tags = self.parse_tags(tag_field.value)
                encrypted = bool(encrypted_switch.value)
                method = method_dropdown.value or SHIFT
                key = (key_field.value or "").strip()
                if encrypted:
                    key = self.validate_key(method, key)
                update_diary(
                    diary["id"], date_value, (title_field.value or "").strip(), (content_field.value or "").strip(),
                    mood_dropdown.value or "😊", tags, encrypted, method, key
                )
                if encrypted:
                    self.add_history("일기", "수정 암호화", method)
                self.selected_calendar_date = date_value
                selected = datetime.strptime(date_value, "%Y-%m-%d")
                self.calendar_year = selected.year; self.calendar_month = selected.month
                self.show_success("일기를 수정했습니다.")
                self.show_diary_detail(diary["id"])
            except Exception as error:
                self.show_error(str(error))
        security_card = ft.Container(
            border=ft.Border.all(1, "#E7E7EC"), border_radius=16, padding=18,
            content=ft.Column(controls=[ft.Row(controls=[ft.Container(expand=True, content=ft.Column(controls=[ft.Text("🔒 비밀 일기로 저장", weight=ft.FontWeight.BOLD), ft.Text("본문만 암호화합니다.", size=11, color="#777780")], spacing=3)), encrypted_switch]), encryption_box], spacing=10)
        )
        form = ft.Container(
            bgcolor="white", border_radius=22, padding=25, border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(controls=[ft.Row(controls=[date_field, mood_dropdown], spacing=12), title_field, tag_field, content_field, security_card, ft.Row(controls=[ft.TextButton("취소", on_click=lambda e: self.open_search_result(diary)), ft.FilledButton("수정 내용 저장", on_click=save)], alignment=ft.MainAxisAlignment.END, spacing=8)], spacing=14)
        )
        self.change_page([self.page_header("일기 수정 ✏️", "기록 내용과 암호화 설정을 수정합니다."), form])

    def show_delete_diary(self, diary):
        def confirm_delete(e):
            try:
                if not delete_diary(diary["id"]):
                    self.show_error("일기를 찾을 수 없습니다."); return
                self.show_success("일기를 삭제했습니다.")
                self.show_calendar()
            except Exception as error:
                self.show_error(str(error))
        card = ft.Container(
            bgcolor="white", border_radius=22, padding=30, border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[ft.Text("🗑️", size=42), ft.Text("이 일기를 삭제할까요?", size=21, weight=ft.FontWeight.BOLD), ft.Text(f"{diary.get('date', '')} · {diary.get('title', '제목 없음')}", color="#777780"), ft.Text("삭제한 기록은 되돌릴 수 없습니다.", size=11, color="#B54A4A"), ft.Row(controls=[ft.TextButton("취소", on_click=lambda e: self.open_search_result(diary)), ft.FilledButton("삭제하기", on_click=confirm_delete)], alignment=ft.MainAxisAlignment.END, spacing=8)],
                spacing=12
            )
        )
        self.change_page([self.page_header("일기 삭제", "삭제 전 기록을 다시 확인해주세요."), card])

    def show_vault(self):
        items = get_all_vault_items()
        icons = {"Wi-Fi": "📶", "계정": "👤", "개인 메모": "📝", "기타": "🔐"}
        controls = [
            self.page_header("비밀 보관함 🔐", "계정 정보와 개인 메모를 암호화하여 보관합니다."),
            ft.Container(
                bgcolor="#F1F2F8", border_radius=20, padding=20,
                content=ft.Row(controls=[
                    ft.Text("🛡️", size=30),
                    ft.Container(expand=True, content=ft.Column(controls=[
                        ft.Text("중요한 정보는 잠가두세요", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("목록에는 종류와 제목만 표시되고 비밀 내용은 암호문으로 저장됩니다.", size=11, color="#6F6F78")
                    ], spacing=3)),
                    ft.FilledButton("＋ 새 비밀 메모", on_click=lambda e: self.show_create_vault())
                ], spacing=14)
            )
        ]
        if not items:
            controls.append(ft.Container(
                height=220, bgcolor="white", border_radius=22, border=ft.Border.all(1, "#ECECF0"),
                alignment=ft.Alignment.CENTER,
                content=ft.Column(controls=[ft.Text("🔒", size=36), ft.Text("아직 저장된 비밀 메모가 없습니다.", color="#777780")],
                                  alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ))
        else:
            for item in reversed(items):
                controls.append(ft.Container(
                    bgcolor="white", border_radius=18, padding=18, border=ft.Border.all(1, "#ECECF0"),
                    content=ft.Row(controls=[
                        ft.Text(icons.get(item.get("category"), "🔐"), size=28),
                        ft.Container(expand=True, content=ft.Column(controls=[
                            ft.Text(item.get("title", "제목 없음"), size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{item.get('category', '기타')} · 🔒 잠김 · {item.get('encryption_method', '-')}", size=11, color="#777780")
                        ], spacing=3)),
                        ft.FilledButton("🔑 열기", on_click=lambda e, x=item: self.show_vault_unlock(x))
                    ], spacing=14)
                ))
        controls.append(ft.Text("※ 교육용 고전 암호를 사용하는 프로젝트 기능이므로 실제 중요한 비밀번호 저장용으로 사용하지 마세요.", size=10, color="#9999A0"))
        self.change_page(controls)

    def show_create_vault(self, item=None, plain_content="", current_key=None):
        editing = item is not None
        category = ft.Dropdown(
            label="종류", value=item.get("category", "Wi-Fi") if item else "Wi-Fi",
            options=[ft.DropdownOption(key=x, text=x) for x in ["Wi-Fi", "계정", "개인 메모", "기타"]],
            border_radius=14, expand=True
        )
        title = ft.TextField(label="제목", value=item.get("title", "") if item else "", hint_text="예: 자취방 Wi-Fi / 학교 포털", border_radius=14, expand=True)
        content = ft.TextField(label="비밀 내용", value=plain_content, hint_text="예: ID, 비밀번호, Wi-Fi 비밀번호, 개인 메모", multiline=True, min_lines=6, max_lines=10, border_radius=16)
        method = ft.Dropdown(
            label="암호 방식", value=item.get("encryption_method", SHIFT) if item else SHIFT,
            options=[ft.DropdownOption(key=SHIFT, text="SHIFT"), ft.DropdownOption(key=KEYWORD, text="KEYWORD")],
            border_radius=14, expand=True
        )
        key = ft.TextField(label="Key / Keyword", value=str(current_key) if current_key is not None else "3", password=True, can_reveal_password=True, border_radius=14, expand=True)
        help_text = ft.Text("SHIFT는 1~25의 정수, KEYWORD는 영문 알파벳만 사용할 수 있습니다.", size=11, color="#888890")

        def save(e):
            try:
                validated = self.validate_key(method.value or SHIFT, (key.value or "").strip())
                if editing:
                    update_vault_item(item["id"], category.value, title.value or "", content.value or "", method.value or SHIFT, validated)
                    self.add_history("비밀 보관함", "수정 암호화", method.value or SHIFT)
                    self.show_success("비밀 메모를 수정했습니다.")
                else:
                    create_vault_item(category.value, title.value or "", content.value or "", method.value or SHIFT, validated)
                    self.add_history("비밀 보관함", "암호화", method.value or SHIFT)
                    self.show_success("비밀 메모를 암호화해 저장했습니다.")
                self.show_vault()
            except Exception as error:
                self.show_error(str(error))

        card = ft.Container(
            bgcolor="white", border_radius=22, padding=25, border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(controls=[
                ft.Row(controls=[category, title], spacing=12), content,
                ft.Text("암호화 설정", size=14, weight=ft.FontWeight.BOLD),
                ft.Row(controls=[method, key], spacing=12), help_text,
                ft.Text("✓ 제목과 종류는 목록 표시용으로 유지하고 비밀 내용만 암호화합니다.", size=11, color="#66666E"),
                ft.Row(controls=[ft.TextButton("취소", on_click=lambda e: self.show_vault()), ft.FilledButton("수정 저장" if editing else "🔒 암호화하여 저장", on_click=save)], alignment=ft.MainAxisAlignment.END, spacing=8)
            ], spacing=14)
        )
        self.change_page([self.page_header("비밀 메모 수정 ✏️" if editing else "새 비밀 메모 🔐", "민감한 내용을 암호화하여 보관합니다."), card])

    def show_vault_unlock(self, item):
        method = item.get("encryption_method", SHIFT)
        key = ft.TextField(label="SHIFT Key" if method == SHIFT else "Keyword", password=True, can_reveal_password=True, border_radius=14)
        error_text = ft.Text("", size=11, color="#B54A4A")

        def unlock(e):
            try:
                validated = self.validate_key(method, (key.value or "").strip())
                plain = open_vault_item(item["id"], validated)
                self.add_history("비밀 보관함", "복호화", method)
                self.show_open_vault(item, plain, validated)
            except Exception as error:
                error_text.value = str(error); error_text.update()

        card = ft.Container(
            bgcolor="white", border_radius=22, padding=30, border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(controls=[
                ft.Text("🔐", size=44), ft.Text(item.get("title", "비밀 메모"), size=22, weight=ft.FontWeight.BOLD),
                ft.Text(f"{item.get('category', '기타')} · {method}", size=12, color="#777780"),
                ft.Divider(color="#EEEEF2"), key, error_text,
                ft.Row(controls=[ft.TextButton("돌아가기", on_click=lambda e: self.show_vault()), ft.FilledButton("🔓 내용 열기", on_click=unlock)], alignment=ft.MainAxisAlignment.END, spacing=8)
            ], spacing=12)
        )
        self.change_page([self.page_header("비밀 보관함 🔐", "Key를 입력해야 비밀 내용을 확인할 수 있습니다."), card])

    def show_open_vault(self, item, plain, key):
        def delete(e):
            try:
                if delete_vault_item(item["id"]):
                    self.show_success("비밀 메모를 삭제했습니다.")
                    self.show_vault()
                else:
                    self.show_error("비밀 메모를 찾을 수 없습니다.")
            except Exception as error:
                self.show_error(str(error))

        card = ft.Container(
            bgcolor="white", border_radius=22, padding=28, border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(controls=[
                ft.Row(controls=[ft.Text("🔓", size=30), ft.Container(expand=True, content=ft.Column(controls=[ft.Text(item.get("title", "비밀 메모"), size=22, weight=ft.FontWeight.BOLD), ft.Text(item.get("category", "기타"), size=11, color="#777780")], spacing=2))]),
                ft.Divider(color="#EEEEF2"),
                ft.Container(bgcolor="#FAFAFC", border_radius=16, padding=20, content=ft.Text(plain, size=15)),
                ft.Divider(color="#EEEEF2"),
                ft.Row(controls=[ft.TextButton("← 목록", on_click=lambda e: self.show_vault()), ft.Container(expand=True), ft.TextButton("✏️ 수정", on_click=lambda e: self.show_create_vault(item, plain, key)), ft.TextButton("🗑️ 삭제", on_click=delete)], spacing=8)
            ], spacing=12)
        )
        self.change_page([self.page_header("비밀 메모 🔓", "잠금을 해제한 내용입니다."), card])

    def show_capsule(self):
        capsules = (
            get_all_capsules()
        )

        intro_card = ft.Container(
            bgcolor="#F1F2F8",
            border_radius=20,
            padding=22,
            content=ft.Row(
                controls=[
                    ft.Text(
                        "💌",
                        size=32
                    ),

                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "미래의 나에게",
                                    size=17,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    "지금의 마음을 암호화해 보관하고 "
                                    "정해진 날 다시 열어보세요.",
                                    size=12,
                                    color="#6F6F78"
                                )
                            ],
                            spacing=4
                        )
                    ),

                    ft.FilledButton(
                        "＋ 새 타임캡슐",
                        on_click=lambda e:
                        self.show_create_capsule()
                    )
                ],
                spacing=15
            )
        )

        controls = [
            self.page_header(
                "타임캡슐 💌",
                "미래의 나에게 비밀 기록을 남겨보세요."
            ),

            intro_card,

            ft.Text(
                "나의 타임캡슐",
                size=18,
                weight=ft.FontWeight.BOLD
            )
        ]

        if not capsules:
            controls.append(
                ft.Container(
                    height=220,
                    bgcolor="white",
                    border_radius=22,
                    border=ft.Border.all(
                        1,
                        "#ECECF0"
                    ),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "📭",
                                size=35
                            ),

                            ft.Text(
                                "아직 만든 타임캡슐이 없습니다.",
                                size=14,
                                color="#777780"
                            ),

                            ft.Text(
                                "미래의 나에게 첫 메시지를 남겨보세요.",
                                size=11,
                                color="#9999A0"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                )
            )
        else:
            for capsule in reversed(
                capsules
            ):
                controls.append(
                    self.create_capsule_card(
                        capsule
                    )
                )

        self.change_page(
            controls
        )

    def create_capsule_card(
        self,
        capsule
    ):
        try:
            status = get_capsule_status(
                capsule["id"]
            )
        except Exception:
            status = "-"

        available = (
            status == "열람 가능"
            or status == "열람 완료"
        )

        if status.startswith(
            "D-"
        ):
            icon = "🔒"
            description = (
                f"{status} · 아직 열 수 없어요"
            )

        elif status == "열람 완료":
            icon = "📬"
            description = (
                "열람 완료"
            )

        else:
            icon = "💌"
            description = (
                "지금 열어볼 수 있어요"
            )

        return ft.Container(
            bgcolor="white",
            border_radius=18,
            padding=20,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Row(
                controls=[
                    ft.Text(
                        icon,
                        size=30
                    ),

                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    capsule.get(
                                        "title",
                                        "제목 없음"
                                    ),
                                    size=16,
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    "공개일  "
                                    + capsule.get(
                                        "open_date",
                                        "-"
                                    ),
                                    size=11,
                                    color="#777780"
                                ),

                                ft.Text(
                                    description,
                                    size=11,
                                    color="#777780"
                                ),

                                ft.Text(
                                    "🔐 "
                                    + capsule.get(
                                        "encryption_method",
                                        "-"
                                    ),
                                    size=10,
                                    color="#9999A0"
                                )
                            ],
                            spacing=4
                        )
                    ),

                    ft.FilledButton(
                        (
                            "열어보기"
                            if available
                            else status
                        ),
                        disabled=not available,
                        on_click=lambda e, item=capsule:
                        self.show_capsule_unlock(
                            item
                        )
                    )
                ],
                spacing=15
            )
        )

    def show_create_capsule(self):
        title_field = ft.TextField(
            label="타임캡슐 제목",
            hint_text="미래의 나에게",
            border_radius=14
        )

        open_date_field = ft.TextField(
            label="공개 날짜",
            hint_text="YYYY-MM-DD",
            border_radius=14
        )

        content_field = ft.TextField(
            label="미래의 나에게 남길 이야기",
            hint_text=(
                "지금의 마음과 미래의 나에게 "
                "하고 싶은 말을 적어보세요..."
            ),
            multiline=True,
            min_lines=7,
            max_lines=12,
            border_radius=16
        )

        method_dropdown = ft.Dropdown(
            label="암호 방식",
            value=SHIFT,
            options=[
                ft.DropdownOption(
                    key=SHIFT,
                    text="SHIFT"
                ),

                ft.DropdownOption(
                    key=KEYWORD,
                    text="KEYWORD"
                )
            ],
            border_radius=14,
            expand=True
        )

        key_field = ft.TextField(
            label="Key",
            value="3",
            password=True,
            can_reveal_password=True,
            border_radius=14,
            expand=True
        )

        key_help = ft.Text(
            "SHIFT Key는 1~25의 정수를 입력해주세요.",
            size=11,
            color="#888890"
        )

        def change_method(e):
            if method_dropdown.value == SHIFT:
                key_field.label = "Key"
                key_field.value = "3"

                key_help.value = (
                    "SHIFT Key는 1~25의 정수를 입력해주세요."
                )
            else:
                key_field.label = "Keyword"
                key_field.value = ""

                key_help.value = (
                    "Keyword는 영문 알파벳만 입력해주세요."
                )

            key_field.update()
            key_help.update()

        method_dropdown.on_select = (
            change_method
        )

        def save(e):
            title = (
                title_field.value
                or ""
            ).strip()

            content = (
                content_field.value
                or ""
            ).strip()

            open_date = (
                open_date_field.value
                or ""
            ).strip()

            method = (
                method_dropdown.value
                or SHIFT
            )

            key = (
                key_field.value
                or ""
            ).strip()

            if not title:
                self.show_error(
                    "타임캡슐 제목을 입력해주세요."
                )
                return

            if not content:
                self.show_error(
                    "타임캡슐 내용을 입력해주세요."
                )
                return

            try:
                datetime.strptime(
                    open_date,
                    "%Y-%m-%d"
                )
            except ValueError:
                self.show_error(
                    "공개 날짜는 YYYY-MM-DD 형식으로 입력해주세요."
                )
                return

            try:
                key = self.validate_key(
                    method,
                    key
                )

                create_capsule(
                    title=title,
                    content=content,
                    open_date=open_date,
                    method=method,
                    key=key
                )

                self.add_history(
                    "타임캡슐",
                    "암호화",
                    method
                )

                self.show_success(
                    "미래의 나에게 타임캡슐을 보관했어요."
                )

                self.show_capsule()

            except Exception as error:
                self.show_error(
                    str(error)
                )

        warning_card = ft.Container(
            bgcolor="#FFF8EB",
            border_radius=14,
            padding=15,
            content=ft.Row(
                controls=[
                    ft.Text(
                        "💡",
                        size=20
                    ),

                    ft.Text(
                        "공개일이 되기 전에는 타임캡슐을 열 수 없습니다. "
                        "사용한 Key도 기억해주세요.",
                        size=11,
                        color="#75694F",
                        expand=True
                    )
                ]
            )
        )

        card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=25,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    title_field,

                    open_date_field,

                    content_field,

                    ft.Text(
                        "암호화 설정",
                        size=14,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Row(
                        controls=[
                            method_dropdown,
                            key_field
                        ],
                        spacing=12
                    ),

                    key_help,

                    warning_card,

                    ft.Row(
                        controls=[
                            ft.TextButton(
                                "취소",
                                on_click=lambda e:
                                self.show_capsule()
                            ),

                            ft.FilledButton(
                                "💌 타임캡슐 보관하기",
                                on_click=save
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10
                    )
                ],
                spacing=15
            )
        )

        self.change_page(
            [
                self.page_header(
                    "새 타임캡슐 💌",
                    "미래의 내가 읽을 비밀 메시지를 남겨보세요."
                ),

                card
            ]
        )

    def show_capsule_unlock(
        self,
        capsule
    ):
        try:
            status = get_capsule_status(
                capsule["id"]
            )
        except Exception as error:
            self.show_error(
                str(error)
            )
            return

        if status.startswith(
            "D-"
        ):
            self.show_error(
                f"아직 열 수 없습니다. {status}"
            )
            return

        method = capsule.get(
            "encryption_method",
            SHIFT
        )

        key_field = ft.TextField(
            label=(
                "SHIFT Key"
                if method == SHIFT
                else "Keyword"
            ),
            password=True,
            can_reveal_password=True,
            border_radius=14
        )

        error_text = ft.Text(
            "",
            size=11,
            color="#B54A4A"
        )

        def unlock(e):
            try:
                key = self.validate_key(
                    method,
                    (
                        key_field.value
                        or ""
                    ).strip()
                )

                content = open_capsule(
                    capsule["id"],
                    key
                )

                self.add_history(
                    "타임캡슐",
                    "복호화",
                    method
                )

                self.show_open_capsule(
                    capsule,
                    content
                )

            except Exception as error:
                error_text.value = (
                    str(error)
                )
                error_text.update()

        card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=30,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "💌",
                        size=45
                    ),

                    ft.Text(
                        capsule.get(
                            "title",
                            "타임캡슐"
                        ),
                        size=22,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text(
                        "기다리던 타임캡슐을 열 수 있는 날이 되었어요.",
                        size=12,
                        color="#777780"
                    ),

                    ft.Divider(
                        color="#EEEEF2"
                    ),

                    self.info_row(
                        "📅",
                        "작성일",
                        capsule.get(
                            "created_date",
                            "-"
                        )
                    ),

                    self.info_row(
                        "🎁",
                        "공개일",
                        capsule.get(
                            "open_date",
                            "-"
                        )
                    ),

                    self.info_row(
                        "🔐",
                        "암호 방식",
                        method
                    ),

                    key_field,

                    ft.Text(
                        "보관할 때 사용한 Key를 입력해주세요.",
                        size=11,
                        color="#888890"
                    ),

                    error_text,

                    ft.Row(
                        controls=[
                            ft.TextButton(
                                "돌아가기",
                                on_click=lambda e:
                                self.show_capsule()
                            ),

                            ft.FilledButton(
                                "🔓 타임캡슐 열기",
                                on_click=unlock
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10
                    )
                ],
                spacing=12
            )
        )

        self.change_page(
            [
                self.page_header(
                    "타임캡슐 열기 🔐",
                    capsule.get(
                        "open_date",
                        ""
                    )
                ),

                card
            ]
        )

    def show_open_capsule(
        self,
        capsule,
        content
    ):
        card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=30,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "📬",
                        size=38
                    ),

                    ft.Text(
                        capsule.get(
                            "title",
                            "타임캡슐"
                        ),
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text(
                        "과거의 내가 남긴 이야기",
                        size=12,
                        color="#777780"
                    ),

                    ft.Divider(
                        color="#EEEEF2"
                    ),

                    ft.Container(
                        bgcolor="#FAFAFC",
                        border_radius=16,
                        padding=22,
                        content=ft.Text(
                            content,
                            size=15,
                            color="#303038"
                        )
                    ),

                    ft.Divider(
                        color="#EEEEF2"
                    ),

                    ft.Text(
                        "작성일  "
                        + capsule.get(
                            "created_date",
                            "-"
                        )
                        + "   ·   공개일  "
                        + capsule.get(
                            "open_date",
                            "-"
                        ),
                        size=11,
                        color="#9999A0"
                    ),

                    ft.TextButton(
                        "← 타임캡슐 목록",
                        on_click=lambda e:
                        self.show_capsule()
                    )
                ],
                spacing=12
            )
        )

        self.change_page(
            [
                self.page_header(
                    "과거의 나로부터 💌",
                    "기다림 끝에 도착한 메시지입니다."
                ),

                card
            ]
        )

    def show_statistics(self):
        summary = get_statistics_summary()
        year = get_today().year
        monthly = get_monthly_counts(year)
        moods = get_mood_counts()
        top_tags = get_top_tags(5)
        weekdays = get_weekday_counts()

        cards = ft.Row(
            controls=[
                self.stat_card("📖", "전체 기록", f"{summary['total_diaries']}개", "작성한 모든 일기"),
                self.stat_card("🔥", "현재 연속", f"{summary['current_streak']}일", "현재 기록"),
                self.stat_card("🏆", "최장 연속", f"{summary['longest_streak']}일", "최고 기록"),
                self.stat_card("🔒", "암호화", f"{summary['encrypted_ratio']}%", "비밀 일기 비율")
            ],
            spacing=15
        )

        def bar_row(label, value, maximum, suffix="개"):
            ratio = 0 if maximum <= 0 else value / maximum
            filled = max(0, min(20, round(ratio * 20)))
            bar = "█" * filled + "░" * (20 - filled)
            return ft.Row(
                controls=[
                    ft.Text(label, width=62, size=11, color="#66666E"),
                    ft.Text(bar, expand=True, size=13, color="#676B84"),
                    ft.Text(f"{value}{suffix}", width=55, size=11, text_align=ft.TextAlign.RIGHT)
                ],
                spacing=8
            )

        month_values = []
        for month in range(1, 13):
            value = monthly.get(month, monthly.get(str(month), 0))
            month_values.append((month, value))
        max_month = max([v for _, v in month_values], default=0)
        month_chart = ft.Container(
            expand=True, bgcolor="white", border_radius=22, padding=22,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[
                    ft.Text(f"📅 {year}년 월별 기록량", size=17, weight=ft.FontWeight.BOLD),
                    ft.Text("월별로 작성한 일기 수를 비교합니다.", size=11, color="#888890"),
                    ft.Divider(color="#EEEEF2"),
                    *[bar_row(f"{m}월", v, max_month) for m, v in month_values]
                ], spacing=7
            )
        )

        mood_order = ["😊", "😄", "😐", "😢", "😡", "😴"]
        max_mood = max([moods.get(m, 0) for m in mood_order], default=0)
        mood_chart = ft.Container(
            expand=True, bgcolor="white", border_radius=22, padding=22,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[
                    ft.Text("😊 기분 분포", size=17, weight=ft.FontWeight.BOLD),
                    ft.Text("기록에 남긴 감정의 분포입니다.", size=11, color="#888890"),
                    ft.Divider(color="#EEEEF2"),
                    *[bar_row(m, moods.get(m, 0), max_mood) for m in mood_order]
                ], spacing=9
            )
        )

        if top_tags:
            tag_controls = [
                self.info_row(f"{i}", f"#{tag}", f"{count}회")
                for i, (tag, count) in enumerate(top_tags, start=1)
            ]
        else:
            tag_controls = [ft.Container(height=90, alignment=ft.Alignment.CENTER,
                                         content=ft.Text("아직 사용한 태그가 없습니다.", color="#888890"))]

        tag_card = ft.Container(
            expand=True, bgcolor="white", border_radius=22, padding=22,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[ft.Text("# 자주 사용한 태그 TOP 5", size=17, weight=ft.FontWeight.BOLD),
                          ft.Divider(color="#EEEEF2"), *tag_controls], spacing=5
            )
        )

        normal_count = summary['total_diaries'] - summary['encrypted_count']
        privacy_card = ft.Container(
            expand=True, bgcolor="white", border_radius=22, padding=22,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[
                    ft.Text("🔐 기록 공개 상태", size=17, weight=ft.FontWeight.BOLD),
                    ft.Divider(color="#EEEEF2"),
                    self.info_row("📖", "일반 기록", f"{normal_count}개"),
                    self.info_row("🔒", "비밀 기록", f"{summary['encrypted_count']}개"),
                    self.info_row("%", "비밀 기록 비율", f"{summary['encrypted_ratio']}%"),
                    ft.Text("날짜·제목·기분·태그는 통계에 사용하고 비밀 일기의 본문은 분석하지 않습니다.", size=10, color="#888890")
                ], spacing=7
            )
        )

        most_common_tag = summary["most_common_tag"]
        most_common_tag = "#" + most_common_tag if most_common_tag else "-"
        weekday = summary["most_active_weekday"]
        weekday = weekday + "요일" if weekday else "-"
        detail_card = ft.Container(
            bgcolor="white", border_radius=22, padding=22,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[
                    ft.Text("기록 분석 요약", size=17, weight=ft.FontWeight.BOLD),
                    ft.Divider(color="#EEEEF2"),
                    self.info_row("😊", "가장 많이 기록한 기분", summary["most_common_mood"] or "-"),
                    self.info_row("#", "가장 많이 사용한 태그", most_common_tag),
                    self.info_row("📅", "가장 자주 작성한 요일", weekday),
                    self.info_row("📝", "이번 달 작성량", f"{summary['current_month']}개")
                ], spacing=8
            )
        )

        self.change_page([
            self.page_header("나의 기록 📊", "나의 일기 습관과 감정을 한눈에 확인합니다."),
            cards,
            ft.Row(controls=[month_chart, mood_chart], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row(controls=[tag_card, privacy_card], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START),
            detail_card
        ])

    def show_settings(self):
        demo_date_field = ft.TextField(
            label="시연 날짜",
            value=get_today_string(),
            hint_text="YYYY-MM-DD",
            border_radius=14
        )

        def apply_demo_date(e):
            date_text = (
                demo_date_field.value
                or ""
            ).strip()

            try:
                set_demo_date(
                    date_text
                )

                today = get_today()

                self.calendar_year = (
                    today.year
                )

                self.calendar_month = (
                    today.month
                )

                self.selected_calendar_date = (
                    get_today_string()
                )

                self.show_success(
                    f"시연 날짜를 {get_today_string()}로 적용했습니다."
                )

                self.show_settings()

            except ValueError as error:
                self.show_error(
                    str(error)
                )

        def restore_real_date(e):
            reset_demo_date()

            today = get_today()

            self.calendar_year = (
                today.year
            )

            self.calendar_month = (
                today.month
            )

            self.selected_calendar_date = (
                get_today_string()
            )

            self.show_success(
                "실제 날짜로 돌아왔습니다."
            )

            self.show_settings()

        date_card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=25,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "📅 프로그램 날짜",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text(
                        "타임캡슐과 날짜 기반 기능에서 "
                        "사용할 프로그램 날짜입니다.",
                        size=12,
                        color="#777780"
                    ),

                    ft.Divider(
                        color="#EEEEF2"
                    ),

                    self.info_row(
                        "📆",
                        "현재 적용 날짜",
                        get_today_string()
                    ),

                    self.info_row(
                        "🕒",
                        "현재 상태",
                        (
                            "시연 모드"
                            if is_demo_mode()
                            else "실제 날짜"
                        )
                    ),

                    demo_date_field,

                    ft.Row(
                        controls=[
                            ft.FilledButton(
                                "🧪 시연 날짜 적용",
                                on_click=apply_demo_date
                            ),

                            ft.TextButton(
                                "실제 날짜로 돌아가기",
                                on_click=restore_real_date
                            )
                        ],
                        spacing=10
                    ),

                    ft.Text(
                        "시연 날짜는 저장되지 않습니다. "
                        "프로그램을 다시 실행하면 실제 날짜를 사용합니다.",
                        size=11,
                        color="#888890"
                    )
                ],
                spacing=12
            )
        )

        auto_switch = ft.Switch(
            value=self.weekday_auto_encryption
        )

        weekday_names = [
            "월요일",
            "화요일",
            "수요일",
            "목요일",
            "금요일",
            "토요일",
            "일요일"
        ]

        rule_controls = []
        rule_method_fields = {}
        rule_key_fields = {}

        for index, weekday_name in enumerate(
            weekday_names
        ):
            rule = (
                self.weekday_rules[
                    index
                ]
            )

            method_field = ft.Dropdown(
                value=rule[
                    "method"
                ],
                options=[
                    ft.DropdownOption(
                        key=SHIFT,
                        text="SHIFT"
                    ),

                    ft.DropdownOption(
                        key=KEYWORD,
                        text="KEYWORD"
                    )
                ],
                width=170,
                border_radius=12
            )

            key_field = ft.TextField(
                value=str(
                    rule[
                        "key"
                    ]
                ),
                label="Key",
                width=220,
                border_radius=12
            )

            rule_method_fields[
                index
            ] = method_field

            rule_key_fields[
                index
            ] = key_field

            rule_controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                weekday_name,
                                width=80,
                                size=13,
                                weight=ft.FontWeight.BOLD
                            ),

                            method_field,

                            key_field
                        ],
                        spacing=12
                    )
                )
            )

        def save_weekday_settings(e):
            new_rules = {}

            try:
                for index in range(
                    7
                ):
                    method = (
                        rule_method_fields[
                            index
                        ].value
                    )

                    key = (
                        rule_key_fields[
                            index
                        ].value
                        or ""
                    ).strip()

                    validated_key = (
                        self.validate_key(
                            method,
                            key
                        )
                    )

                    new_rules[
                        index
                    ] = {
                        "method": method,
                        "key": str(
                            validated_key
                        )
                    }

                self.weekday_rules = (
                    new_rules
                )

                self.weekday_auto_encryption = bool(
                    auto_switch.value
                )

                if self.weekday_auto_encryption:
                    self.show_success(
                        "요일별 자동 암호화를 활성화했습니다."
                    )
                else:
                    self.show_success(
                        "요일별 자동 암호화를 비활성화했습니다."
                    )

            except ValueError as error:
                self.show_error(
                    str(error)
                )

        encryption_card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=25,
            border=ft.Border.all(
                1,
                "#ECECF0"
            ),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "🔐 요일별 자동 암호화",
                                            size=18,
                                            weight=ft.FontWeight.BOLD
                                        ),

                                        ft.Text(
                                            "일기를 작성하는 날짜의 요일에 따라 "
                                            "암호 방식과 Key를 자동 적용합니다.",
                                            size=12,
                                            color="#777780"
                                        )
                                    ],
                                    spacing=3
                                )
                            ),

                            auto_switch
                        ]
                    ),

                    ft.Divider(
                        color="#EEEEF2"
                    ),

                    ft.Row(
                        controls=[
                            ft.Text(
                                "요일",
                                width=80,
                                size=11,
                                color="#888890"
                            ),

                            ft.Text(
                                "암호 방식",
                                width=170,
                                size=11,
                                color="#888890"
                            ),

                            ft.Text(
                                "Key / Keyword",
                                width=220,
                                size=11,
                                color="#888890"
                            )
                        ],
                        spacing=12
                    ),

                    *rule_controls,

                    ft.Container(
                        height=5
                    ),

                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True
                            ),

                            ft.FilledButton(
                                "설정 적용",
                                on_click=save_weekday_settings
                            )
                        ]
                    ),

                    ft.Container(
                        bgcolor="#F7F7FA",
                        border_radius=12,
                        padding=14,
                        content=ft.Text(
                            "요일별 규칙은 일기 작성 날짜를 기준으로 적용됩니다. "
                            "자동 적용 후에도 일기 작성 화면에서 암호 방식과 "
                            "Key를 직접 변경할 수 있습니다.",
                            size=11,
                            color="#777780"
                        )
                    )
                ],
                spacing=8
            )
        )

        self.change_page(
            [
                self.page_header(
                    "설정 ⚙️",
                    "날짜 시연과 자동 암호화 방식을 설정합니다."
                ),

                date_card,

                encryption_card
            ]
        )

    def show_crypto(self):
        input_field = ft.TextField(
            label="입력 메시지",
            hint_text="암호화하거나 복호화할 메시지를 입력하세요.",
            multiline=True,
            min_lines=6,
            max_lines=10,
            border_radius=16
        )

        method_dropdown = ft.Dropdown(
            label="암호 방식",
            value=SHIFT,
            options=[
                ft.DropdownOption(key=SHIFT, text="SHIFT"),
                ft.DropdownOption(key=KEYWORD, text="KEYWORD")
            ],
            border_radius=14,
            expand=True
        )

        key_field = ft.TextField(
            label="Key",
            value="3",
            border_radius=14,
            expand=True
        )

        key_help = ft.Text(
            "SHIFT Key는 1~25의 정수를 입력해주세요.",
            size=11,
            color="#888890"
        )

        result_field = ft.TextField(
            label="결과",
            multiline=True,
            min_lines=6,
            max_lines=10,
            read_only=True,
            border_radius=16
        )

        verification_text = ft.Text(
            "아직 복원 검증을 수행하지 않았습니다.",
            size=12,
            color="#888890"
        )

        def change_method(e):
            if method_dropdown.value == SHIFT:
                key_field.label = "Key"
                key_field.value = "3"
                key_help.value = "SHIFT Key는 1~25의 정수를 입력해주세요."
            else:
                key_field.label = "Keyword"
                key_field.value = ""
                key_help.value = "Keyword는 한 글자 이상의 영문 알파벳만 입력해주세요."

            key_field.update()
            key_help.update()

        method_dropdown.on_select = change_method

        def get_values():
            text = input_field.value or ""
            method = method_dropdown.value or SHIFT
            key = (key_field.value or "").strip()

            if not text:
                raise ValueError("메시지를 입력해주세요.")

            key = self.validate_key(method, key)
            return text, method, key

        def run_encrypt(e):
            try:
                text, method, key = get_values()
                result = encrypt(text, method, key)
                verified = verify_restoration(text, method, key)

                result_field.value = result

                if verified:
                    verification_text.value = "✓ 원문 복원 검증 SUCCESS"
                    verification_text.color = "#2F7D59"
                else:
                    verification_text.value = "⚠ 원문 복원 검증 FAIL"
                    verification_text.color = "#B54A4A"

                result_field.update()
                verification_text.update()
                self.add_history("암호 도구", "암호화", method)
                self.show_success("메시지를 암호화했습니다.")

            except Exception as error:
                self.show_error(str(error))

        def run_decrypt(e):
            try:
                text, method, key = get_values()
                result_field.value = decrypt(text, method, key)
                verification_text.value = "복호화를 완료했습니다."
                verification_text.color = "#2F7D59"
                result_field.update()
                verification_text.update()
                self.add_history("암호 도구", "복호화", method)
                self.show_success("메시지를 복호화했습니다.")

            except Exception as error:
                self.show_error(str(error))

        def use_result_as_input(e):
            if not result_field.value:
                self.show_error("먼저 암호화 또는 복호화를 실행해주세요.")
                return

            input_field.value = result_field.value
            result_field.value = ""
            verification_text.value = "결과를 입력 메시지로 옮겼습니다."
            verification_text.color = "#888890"
            input_field.update()
            result_field.update()
            verification_text.update()

        guide_card = ft.Container(
            bgcolor="#F1F2F8",
            border_radius=18,
            padding=18,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "암호 규칙",
                        size=14,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        "영문과 한글은 암호화하고 숫자, 공백, 문장부호는 그대로 유지합니다. "
                        "SHIFT의 기본 Key는 3이며 KEYWORD는 영문 알파벳만 사용할 수 있습니다.",
                        size=11,
                        color="#6F6F78"
                    )
                ],
                spacing=4
            )
        )

        tool_card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=25,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "메시지 입력",
                        size=17,
                        weight=ft.FontWeight.BOLD
                    ),
                    input_field,
                    ft.Row(
                        controls=[method_dropdown, key_field],
                        spacing=12
                    ),
                    key_help,
                    ft.Row(
                        controls=[
                            ft.FilledButton(
                                "🔒 암호화",
                                on_click=run_encrypt
                            ),
                            ft.FilledButton(
                                "🔓 복호화",
                                on_click=run_decrypt
                            ),
                            ft.TextButton(
                                "결과를 입력으로",
                                on_click=use_result_as_input
                            )
                        ],
                        spacing=10
                    ),
                    ft.Divider(color="#EEEEF2"),
                    ft.Text(
                        "처리 결과",
                        size=17,
                        weight=ft.FontWeight.BOLD
                    ),
                    result_field,
                    verification_text
                ],
                spacing=12
            )
        )

        self.change_page(
            [
                self.page_header(
                    "암호 도구 🔐",
                    "SHIFT와 KEYWORD 암호를 직접 암호화하고 복호화해보세요."
                ),
                guide_card,
                tool_card
            ]
        )

    def show_history(self):
        history_controls = []

        recent_history = self.session_history[-30:][::-1]

        if recent_history:
            for index, record in enumerate(recent_history, start=1):
                history_controls.append(
                    ft.Container(
                        bgcolor="#FAFAFC",
                        border_radius=14,
                        padding=14,
                        border=ft.Border.all(1, "#ECECF0"),
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    str(index),
                                    size=11,
                                    color="#9999A0",
                                    width=28
                                ),
                                ft.Text(
                                    record,
                                    size=12,
                                    color="#44444C",
                                    expand=True
                                )
                            ],
                            spacing=8
                        )
                    )
                )
        else:
            history_controls.append(
                ft.Container(
                    height=160,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        controls=[
                            ft.Text("🕘", size=32),
                            ft.Text(
                                "이번 실행에서 수행한 암호화 기록이 없습니다.",
                                size=13,
                                color="#777780"
                            ),
                            ft.Text(
                                "암호화 또는 복호화를 수행하면 최근 기록에 표시됩니다.",
                                size=11,
                                color="#9999A0"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                )
            )

        def load_saved_history(e):
            try:
                loaded = load_history()

                if not loaded:
                    self.show_success(
                        "저장된 암호화 기록 파일이 없거나 기록이 비어 있습니다."
                    )
                    return

                self.session_history = loaded.copy()
                self.show_success(
                    f"저장된 암호화 기록 {len(loaded)}개를 불러왔습니다."
                )
                self.show_history()

            except Exception as error:
                self.show_error(
                    f"기록을 불러오지 못했습니다: {error}"
                )

        def save_current_history(e):
            if not self.session_history:
                self.show_error(
                    "저장할 최근 암호화 기록이 없습니다."
                )
                return

            try:
                if save_history(self.session_history):
                    self.show_success(
                        "암호화 기록을 encryption_history.txt에 저장했습니다."
                    )
                else:
                    self.show_error(
                        "암호화 기록 저장에 실패했습니다."
                    )
            except Exception as error:
                self.show_error(
                    f"기록을 저장하지 못했습니다: {error}"
                )

        def clear_history_records(e):
            try:
                self.session_history.clear()

                if clear_history():
                    self.show_success(
                        "실행 중 기록과 저장된 TXT 기록을 초기화했습니다."
                    )
                    self.show_history()
                else:
                    self.show_error(
                        "TXT 기록 초기화에 실패했습니다."
                    )
            except Exception as error:
                self.show_error(str(error))

        info_card = ft.Container(
            bgcolor="#F1F2F8",
            border_radius=18,
            padding=18,
            content=ft.Row(
                controls=[
                    ft.Text("📄", size=28),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "실행 중 최근 기록 + TXT 저장/불러오기",
                                    size=15,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(
                                    "프로그램 실행 중 수행한 암호화·복호화 기록을 확인하고, "
                                    "필요할 때 TXT 파일에 저장하거나 다시 불러올 수 있습니다.",
                                    size=11,
                                    color="#6F6F78"
                                ),
                                ft.Text(
                                    "저장 위치: data/encryption_history.txt",
                                    size=10,
                                    color="#888890"
                                )
                            ],
                            spacing=3
                        )
                    )
                ],
                spacing=14
            )
        )

        history_card = ft.Container(
            bgcolor="white",
            border_radius=22,
            padding=25,
            border=ft.Border.all(1, "#ECECF0"),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "최근 암호화 기록",
                                            size=18,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        ft.Text(
                                            f"현재 실행 기록 {len(self.session_history)}개 · 최근 30개 표시",
                                            size=11,
                                            color="#888890"
                                        )
                                    ],
                                    spacing=2
                                )
                            ),
                            ft.FilledButton(
                                "💾 암호화 기록 저장",
                                on_click=save_current_history
                            ),
                            ft.TextButton(
                                "📂 저장된 기록 불러오기",
                                on_click=load_saved_history
                            ),
                            ft.TextButton(
                                "🗑 기록 초기화",
                                on_click=clear_history_records
                            )
                        ],
                        spacing=8
                    ),
                    ft.Divider(color="#EEEEF2"),
                    *history_controls
                ],
                spacing=10
            )
        )

        self.change_page(
            [
                self.page_header(
                    "암호화 기록 🕘",
                    "최근 기록 조회 → TXT 저장 → 저장된 기록 불러오기를 직접 확인할 수 있습니다."
                ),
                info_card,
                history_card
            ]
        )

    def show_success(
        self,
        message
    ):
        snack = ft.SnackBar(
            content=ft.Text(
                f"✓  {message}",
                color="white"
            ),
            bgcolor="#2F7D59"
        )

        self.page.overlay.append(
            snack
        )

        snack.open = True

        self.page.update()

    def show_error(
        self,
        message
    ):
        snack = ft.SnackBar(
            content=ft.Text(
                f"⚠  {message}",
                color="white"
            ),
            bgcolor="#B54A4A"
        )

        self.page.overlay.append(
            snack
        )

        snack.open = True

        self.page.update()

    def show_placeholder(
        self,
        title,
        description
    ):
        self.change_page(
            [
                self.page_header(
                    title,
                    description
                ),

                ft.Container(
                    height=350,
                    bgcolor="white",
                    border_radius=22,
                    border=ft.Border.all(
                        1,
                        "#ECECF0"
                    ),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "🚧",
                                size=35
                            ),

                            ft.Text(
                                "기능을 연결하는 중입니다.",
                                size=15,
                                color="#777780"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                )
            ]
        )