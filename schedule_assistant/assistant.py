"""终端交互菜单与增删改查逻辑。"""
from datetime import datetime

from . import storage
from .models import (
    Schedule,
    filter_today,
    filter_upcoming,
    is_overdue,
    parse_due_time,
)

MENU = """==== 日程助手 ====
{reminder}
1. 新增日程
2. 查看全部日程
3. 查看今日日程
4. 查看未来日程
5. 编辑日程
6. 删除日程
7. 标记完成/未完成
q. 退出
"""


def build_reminder(items, now=None) -> str:
    """启动提醒：今日到期与已过期的未完成日程数量。"""
    today_items = filter_today(items)
    overdue_items = [i for i in items if is_overdue(i, now)]
    parts = []
    if today_items:
        parts.append(f"{len(today_items)} 条日程今日到期")
    if overdue_items:
        parts.append(f"{len(overdue_items)} 条已过期")
    if not parts:
        return "[今日待办] 今日暂无到期日程"
    return "[今日待办] " + "，".join(parts)


def print_items(items, print_fn=print) -> None:
    """以表格形式输出编号/状态/标题/时间/备注。"""
    if not items:
        print_fn("（暂无日程）")
        return
    print_fn(f"{'编号':<6}{'状态':<8}{'标题':<20}{'时间':<18}备注")
    for it in items:
        status = "已完成" if it.done else "未完成"
        print_fn(f"{it.id:<8}{status:<8}{it.title:<20}{it.due_time:<18}{it.note}")


def prompt_title(input_fn=input, print_fn=print) -> str:
    """录入标题，非空校验。"""
    while True:
        title = input_fn("标题（必填）: ").strip()
        if title:
            return title
        print_fn("标题不能为空，请重新输入。")


def prompt_due_time(input_fn=input, print_fn=print) -> str:
    """录入日期时间，循环校验 ``YYYY-MM-DD HH:MM``。"""
    while True:
        value = input_fn("日期时间（YYYY-MM-DD HH:MM，如 2024-02-29 09:30）: ").strip()
        try:
            parse_due_time(value)
            return value
        except ValueError:
            print_fn("日期格式不正确，请按 YYYY-MM-DD HH:MM 重新输入。")


def prompt_new_schedule(next_id, input_fn=input, print_fn=print) -> Schedule:
    """录入一条新日程。"""
    title = prompt_title(input_fn, print_fn)
    due_time = prompt_due_time(input_fn, print_fn)
    note = input_fn("备注（可留空）: ").strip()
    return Schedule(
        id=next_id,
        title=title,
        due_time=due_time,
        note=note,
        done=False,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )


def pick_item(items, input_fn=input, print_fn=print):
    """按编号选择日程；编号无效时返回 None 并提示。"""
    value = input_fn("请输入日程编号: ").strip()
    number = int(value)
    for it in items:
        if it.id == number:
            return it
    print_fn(f"编号 {value} 不存在。")
    return None


def confirm(message, input_fn=input, print_fn=print) -> bool:
    """y/n 二次确认。"""
    answer = input_fn(f"{message}（y/n）: ").strip().lower()
    return answer in ("y", "yes")


# ---- 菜单动作：返回 True 表示需要落盘 ----


def action_add(state, input_fn, print_fn):
    item = prompt_new_schedule(state["next_id"], input_fn, print_fn)
    state["items"].append(item)
    state["next_id"] += 1
    print_fn(f"已新增日程 #{item.id}：{item.title}")
    return True


def action_list(state, input_fn, print_fn):
    print_items(state["items"], print_fn)
    return False


def action_today(state, input_fn, print_fn):
    print_items(filter_today(state["items"]), print_fn)
    return False


def action_future(state, input_fn, print_fn):
    print_items(filter_upcoming(state["items"]), print_fn)
    return False


def action_edit(state, input_fn, print_fn):
    if not state["items"]:
        print_fn("（暂无日程）")
        return False
    print_items(state["items"], print_fn)
    item = pick_item(state["items"], input_fn, print_fn)
    if item is None:
        return False
    print_fn("以下各项直接回车保留原值。")
    value = input_fn(f"新标题（当前 {item.title}）: ").strip()
    if value:
        item.title = value
    while True:
        value = input_fn(f"新日期时间（当前 {item.due_time}）: ").strip()
        if not value:
            break
        try:
            parse_due_time(value)
        except ValueError:
            print_fn("日期格式不正确，请重新输入。")
            continue
        item.due_time = value
        break
    value = input_fn(f"新备注（当前 {item.note}）: ").strip()
    if value:
        item.note = value
    print_fn(f"已更新日程 #{item.id}。")
    return True


def action_delete(state, input_fn, print_fn):
    if not state["items"]:
        print_fn("（暂无日程）")
        return False
    print_items(state["items"], print_fn)
    item = pick_item(state["items"], input_fn, print_fn)
    if item is None:
        return False
    print_items([item], print_fn)
    if confirm(f"确认删除日程 #{item.id}「{item.title}」", input_fn, print_fn):
        state["items"].remove(item)
        print_fn("已删除。")
        return True
    print_fn("已取消删除。")
    return False


def action_toggle(state, input_fn, print_fn):
    if not state["items"]:
        print_fn("（暂无日程）")
        return False
    print_items(state["items"], print_fn)
    item = pick_item(state["items"], input_fn, print_fn)
    if item is None:
        return False
    item.done = not item.done
    print_fn(f"日程 #{item.id} 已标记为{'已完成' if item.done else '未完成'}。")
    return True


ACTIONS = {
    "1": action_add,
    "2": action_list,
    "3": action_today,
    "4": action_future,
    "5": action_edit,
    "6": action_delete,
    "7": action_toggle,
}


def run(path=None, input_fn=input, print_fn=print) -> None:
    """主菜单循环。非法输入给出提示，主循环不因异常输入退出。"""
    data, warning = storage.load(path)
    if warning:
        print_fn(warning)
    state = {
        "items": [Schedule.from_dict(d) for d in data["items"]],
        "next_id": data.get("next_id", 1),
        "path": path,
    }

    def persist():
        storage.save(
            {"next_id": state["next_id"], "items": [i.to_dict() for i in state["items"]]},
            state["path"],
        )

    while True:
        print_fn(MENU.format(reminder=build_reminder(state["items"])))
        choice = input_fn("请选择: ").strip()
        if choice in ("q", "Q", "quit", "exit"):
            print_fn("再见！")
            return
        action = ACTIONS.get(choice)
        if action is None:
            print_fn("无效输入，请输入菜单中的数字编号或 q 退出。")
            continue
        try:
            if action(state, input_fn, print_fn):
                persist()
        except ValueError as exc:
            print_fn(f"输入有误：{exc}")
        except (EOFError, KeyboardInterrupt):
            print_fn("\n已退出。")
            return


def main() -> None:
    run()


if __name__ == "__main__":
    main()
