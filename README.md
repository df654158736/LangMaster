# LangMaster

场景驱动的 LangChain & LangGraph 教学 Web 应用，帮你掌握用法并准备面试。

## 特性

- **30 个知识点** 覆盖 LangChain 和 LangGraph 从基础到高级
- **场景驱动** 每个知识点先讲"何时用"，再展示代码示例、核心要点、常见误区
- **双维度标签** 每个知识点标注面试热度（🔥）和开发实用度（⭐）
- **模拟面试** 配置范围 → 出题 → 思考 → 揭晓答案 → 自评打分 → 查看报告
- **智能出题** 优先抽取你不熟悉的知识点
- **进度追踪** localStorage 记录掌握状态、收藏、面试历史

## 技术栈

- **后端**：Python 3.10+ / FastAPI / SQLAlchemy / SQLite
- **前端**：Next.js 16 / TypeScript / Tailwind CSS v4

## 快速开始

### 后端

```bash
cd backend
uv sync --locked
uv run uvicorn app.main:app --reload --port 8000
```

需要先安装 `uv`。后端 Python 版本固定为 3.12，由 `uv` 自动安装并管理。

访问 http://localhost:8000/docs 查看 API 文档。

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

## 页面结构

- `/` 仪表盘 — 学习进度统计 + 薄弱点推荐 + 快捷入口
- `/learn` 学习路径 — 卡片墙，按分类/层级筛选，按热度/实用度排序
- `/learn/[id]` 知识点详情 — 完整场景、代码、要点、误区、关联
- `/interview/setup` 面试配置 — 范围、难度、策略、题数
- `/interview/session` 进行中的面试 — 单题展示 + 思考 + 揭晓 + 自评
- `/interview/report` 面试报告 — 得分统计 + 薄弱点建议
- `/profile` 个人中心 — 统计 + 收藏 + 面试历史

## 测试

```bash
cd backend
uv run pytest tests/ -v
```

27 个后端测试覆盖知识点、进度、面试、统计四个模块。

## 文档

- `docs/superpowers/specs/2026-04-16-langmaster-design.md` — 设计文档
- `docs/superpowers/plans/2026-04-16-langmaster-implementation.md` — 实现计划
