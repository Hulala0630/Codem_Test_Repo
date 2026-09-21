# Codem_Test_Repo

CodeM 演示仓库。当前包含两个独立演示项目：

## 星语村物语 —— 经典 JRPG 风格可交互游戏（rpg/）

Meego 工作项 7378646084「codem交互演示」交付物：零依赖单文件 HTML（Canvas 2D + 原生 JS），浏览器打开即玩。

**入口：直接用浏览器打开 [`rpg/index.html`](rpg/index.html)**（Chrome / Edge / Safari 均可，无需任何构建或安装）。

**操作说明：**

| 按键 | 功能 |
| --- | --- |
| WASD / 方向键 | 四方向移动，长按连续移动、松开即停 |
| E / 回车 | 与面前的 NPC 交互；对话中翻页 |
| 空格 | 跳过当前页打字机动画 |
| Q / M | 打开 / 关闭任务面板 |
| Esc | 关闭面板 |

**功能：** 标题画面（TITLE）→ 自由探索（EXPLORE）→ NPC 对话（DIALOG，日式对话框、打字机逐字显示、翻页/跳过）→ 任务面板（MENU），任务链「接取 → 进行中 → 已完成」全链路实时刷新，含碰撞检测与 localStorage 进度存档。

技术方案：单文件 HTML + 原生 JS + Canvas 2D，无外部依赖、无构建步骤。开发分支 `feature/codem-rpg-7378646084`（基于 main@6518ca8）。
