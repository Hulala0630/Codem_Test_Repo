"""存储读写与损坏文件恢复单元测试。"""
import tempfile
import unittest
from pathlib import Path

from schedule_assistant import storage


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "schedules.json"

    def test_load_missing_returns_empty(self):
        data, warning = storage.load(self.path)
        self.assertEqual(data, {"next_id": 1, "items": []})
        self.assertIsNone(warning)

    def test_save_load_roundtrip(self):
        data = {
            "next_id": 3,
            "items": [
                {
                    "id": 1,
                    "title": "写周报",
                    "due_time": "2024-03-10 18:00",
                    "note": "",
                    "done": False,
                    "created_at": "2024-03-01T10:00:00",
                }
            ],
        }
        storage.save(data, self.path)
        loaded, warning = storage.load(self.path)
        self.assertEqual(loaded, data)
        self.assertIsNone(warning)

    def test_corrupted_file_backed_up(self):
        self.path.write_text("{not json", encoding="utf-8")
        data, warning = storage.load(self.path)
        self.assertEqual(data, {"next_id": 1, "items": []})
        self.assertIsNotNone(warning)
        backups = list(self.path.parent.glob("schedules.json.bak.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "{not json")
        # 原文件已让位，不再存在
        self.assertFalse(self.path.exists())

    def test_invalid_structure_treated_as_corrupted(self):
        self.path.write_text('{"items": "oops"}', encoding="utf-8")
        data, warning = storage.load(self.path)
        self.assertEqual(data, {"next_id": 1, "items": []})
        self.assertIsNotNone(warning)

    def test_next_id_default(self):
        self.path.write_text('{"items": [{"id": 5}]}', encoding="utf-8")
        data, _ = storage.load(self.path)
        self.assertEqual(data["next_id"], 2)

    def test_save_is_atomic_no_tmp_left(self):
        storage.save({"next_id": 1, "items": []}, self.path)
        leftovers = list(self.path.parent.glob("*.tmp"))
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
