"""模型、校验与过滤逻辑单元测试。"""
import unittest
from datetime import date, datetime

from schedule_assistant.models import (
    Schedule,
    filter_today,
    filter_upcoming,
    is_due_today,
    is_overdue,
    parse_due_time,
)


class ParseDueTimeTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(
            parse_due_time("2024-02-29 09:30"), datetime(2024, 2, 29, 9, 30)
        )

    def test_invalid_format(self):
        for bad in ("", "2024/02/29 09:30", "2024-2-9 9:30", "2024-13-01 00:00", "abc"):
            with self.assertRaises(ValueError):
                parse_due_time(bad)

    def test_leap_year(self):
        # 闰年 2 月 29 日合法
        parse_due_time("2024-02-29 00:00")
        # 平年 2 月 29 日非法
        with self.assertRaises(ValueError):
            parse_due_time("2023-02-29 00:00")


class ScheduleTest(unittest.TestCase):
    def test_roundtrip(self):
        item = Schedule(
            id=1,
            title="写周报",
            due_time="2024-02-29 09:30",
            note="周五前",
            done=False,
            created_at="2024-02-20T10:00:00",
        )
        self.assertEqual(Schedule.from_dict(item.to_dict()), item)

    def test_from_dict_ignores_unknown_keys(self):
        item = Schedule.from_dict(
            {"id": 1, "title": "t", "due_time": "2024-01-01 00:00", "extra": "x"}
        )
        self.assertEqual(item.id, 1)
        self.assertEqual(item.note, "")


class FilterTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2024, 3, 10, 12, 0)
        self.today_later = Schedule(1, "今日晚些", "2024-03-10 18:00")
        self.today_earlier = Schedule(2, "今日已过", "2024-03-10 08:00")
        self.yesterday = Schedule(3, "昨日", "2024-03-09 18:00")
        self.tomorrow = Schedule(4, "明日", "2024-03-11 09:00")
        self.done_today = Schedule(5, "已完成", "2024-03-10 18:00", done=True)
        self.items = [
            self.today_later,
            self.today_earlier,
            self.yesterday,
            self.tomorrow,
            self.done_today,
        ]

    def test_filter_today(self):
        ids = [i.id for i in filter_today(self.items, today=date(2024, 3, 10))]
        self.assertEqual(ids, [1, 2])

    def test_overdue(self):
        ids = [i.id for i in self.items if is_overdue(i, self.now)]
        self.assertEqual(ids, [2, 3])

    def test_filter_upcoming(self):
        ids = [i.id for i in filter_upcoming(self.items, self.now)]
        self.assertEqual(ids, [1, 4, 5])

    def test_done_not_reminded(self):
        self.assertFalse(is_due_today(self.done_today, today=date(2024, 3, 10)))
        self.assertFalse(is_overdue(self.done_today, self.now))

    def test_invalid_due_time_not_reminded(self):
        bad = Schedule(9, "坏时间", "not-a-time")
        self.assertFalse(is_due_today(bad, today=date(2024, 3, 10)))
        self.assertFalse(is_overdue(bad, self.now))


if __name__ == "__main__":
    unittest.main()
