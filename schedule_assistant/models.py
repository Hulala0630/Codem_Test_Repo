"""日程数据模型与纯逻辑函数。

时间统一以本地时区字符串 ``YYYY-MM-DD HH:MM`` 存储，
展示与比较时通过 :func:`parse_due_time` 解析。
"""
import re
from dataclasses import asdict, dataclass, fields
from datetime import date, datetime

TIME_FORMAT = "%Y-%m-%d %H:%M"
_TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")


@dataclass
class Schedule:
    """一条日程记录。"""

    id: int
    title: str
    due_time: str
    note: str = ""
    done: bool = False
    created_at: str = ""

    def to_dict(self) -> dict:
        """导出为可 JSON 序列化的字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Schedule":
        """从字典构造，忽略未知键，兼容旧数据。"""
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


def parse_due_time(value: str) -> datetime:
    """按 ``YYYY-MM-DD HH:MM`` 严格解析时间，非法时抛出 ``ValueError``。"""
    value = (value or "").strip()
    if not _TIME_RE.match(value):
        raise ValueError(f"日期格式不正确：{value!r}")
    return datetime.strptime(value, TIME_FORMAT)


def is_due_today(item: Schedule, today: date = None) -> bool:
    """未完成且到期日期为今天。"""
    try:
        due = parse_due_time(item.due_time)
    except ValueError:
        return False
    return (today or date.today()) == due.date() and not item.done


def is_overdue(item: Schedule, now: datetime = None) -> bool:
    """未完成且到期时间早于当前时间。"""
    try:
        due = parse_due_time(item.due_time)
    except ValueError:
        return False
    return (now or datetime.now()) > due and not item.done


def is_upcoming(item: Schedule, now: datetime = None) -> bool:
    """到期时间不早于当前时间（用于「查看未来日程」）。"""
    try:
        due = parse_due_time(item.due_time)
    except ValueError:
        return False
    return (now or datetime.now()) <= due


def filter_today(items, today: date = None):
    """筛选今日到期的未完成日程。"""
    return [i for i in items if is_due_today(i, today)]


def filter_upcoming(items, now: datetime = None):
    """筛选未来（含当前时刻之后）到期的日程。"""
    return [i for i in items if is_upcoming(i, now)]
