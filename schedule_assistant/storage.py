"""JSON 本地持久化。

存储路径默认为 ``~/.schedule_assistant/schedules.json``，
文件格式为 ``{"next_id": <int>, "items": [Schedule...]}``。
写入采用「临时文件 + 原子替换」防止写坏；
读取时 JSON 解析失败则将原文件备份后初始化空数据，不静默丢弃。
"""
import json
import os
import time
from pathlib import Path

DEFAULT_DIR = Path.home() / ".schedule_assistant"
DEFAULT_PATH = DEFAULT_DIR / "schedules.json"


def empty_data() -> dict:
    """返回空数据结构。"""
    return {"next_id": 1, "items": []}


def load(path=None):
    """读取数据。

    返回 ``(data, warning)``：正常时 warning 为 None；
    文件不存在时返回空数据；文件损坏或结构不合法时，
    将原文件重命名为 ``<原名>.bak.<时间戳>`` 备份并返回空数据与提示信息。
    """
    path = Path(path) if path is not None else DEFAULT_PATH
    if not path.exists():
        return empty_data(), None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            raise ValueError("数据结构不合法")
    except (ValueError, OSError):
        backup = path.with_name(path.name + ".bak." + time.strftime("%Y%m%d%H%M%S"))
        warning = "数据文件损坏，已初始化为空数据。"
        try:
            os.replace(path, backup)
            warning = f"数据文件损坏，原文件已备份至 {backup}，已初始化为空数据。"
        except OSError:
            warning = "数据文件损坏（且备份失败），已初始化为空数据。"
        return empty_data(), warning
    data.setdefault("next_id", len(data["items"]) + 1)
    return data, None


def save(data: dict, path=None) -> None:
    """原子写入数据：先写临时文件再替换，避免写盘中断导致损坏。"""
    path = Path(path) if path is not None else DEFAULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
