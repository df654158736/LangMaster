# LangMaster — LangChain/LangGraph 教学网站设计文档

## 1. 项目概述

### 目标
构建一个 LangChain/LangGraph 教学网站，通过场景驱动的知识卡片和模拟面试功能，帮助用户掌握用法并准备面试。

### 核心定位
- **日常参考**：按学习路径浏览知识点，快速查阅用法
- **面试备战**：模拟面试流程，自评打分，追踪薄弱点

### 用户画像
有一定 Python 基础，正在学习或使用 LangChain/LangGraph 的开发者，需要系统掌握知识点并准备相关面试。

---

## 2. 技术架构

### 技术栈
- **前端**：Next.js + Tailwind CSS
- **后端**：Python FastAPI
- **数据库**：SQLite（MVP），后续可切换 PostgreSQL
- **认证**：MVP 阶段用 localStorage 存进度，后续可加登录

### 架构图

```
┌─────────────────────────────────────────────────┐
│                   用户浏览器                      │
│              Next.js (SSG/SSR)                   │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ 日常模式  │  │ 面试模式  │  │ 进度/个人中心  │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└───────────────────┬─────────────────────────────┘
                    │ REST API
┌───────────────────▼─────────────────────────────┐
│              Python FastAPI                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ 知识点    │  │ 面试引擎  │  │ 用户进度      │  │
│  │ CRUD     │  │ 抽题/评分  │  │ 追踪         │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│              SQLite / PostgreSQL                  │
│  知识点数据 │ 用户进度 │ 面试记录                  │
└─────────────────────────────────────────────────┘
```

---

## 3. 数据模型

### 知识点 (KnowledgePoint)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| title | string | 知识点名称，如 "ChatPromptTemplate" |
| category | string | 分类：Prompt / Chain / Agent / Memory / Retrieval / Graph / Tools |
| level | enum | 层级：basic / intermediate / advanced |
| interview_heat | int (1-3) | 面试热度：1=低频，2=中频，3=高频 |
| dev_utility | int (1-3) | 开发实用度：1=冷门，2=常用，3=必会 |
| scenario | text | 场景描述："当你需要...时" |
| code_example | text | 完整可运行的代码示例 |
| key_points | json (string[]) | 核心要点，2-3 条 |
| common_mistakes | json (string[]) | 常见误区 |
| related_point_ids | json (int[]) | 关联知识点 ID |
| tags | json (string[]) | 标签：["langchain", "prompt", "基础"] |
| sort_order | int | 学习路径中的排序位置 |

### 用户进度 (UserProgress)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| user_id | string | 用户标识（MVP 阶段为 localStorage 生成的 UUID） |
| point_id | int | 知识点 ID |
| mastery | enum | 掌握程度：not_started / partial / mastered |
| last_reviewed_at | datetime | 最近复习时间 |
| review_count | int | 复习次数 |
| is_favorite | bool | 是否收藏 |

### 面试记录 (InterviewSession)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| user_id | string | 用户标识 |
| config | json | 面试配置（范围、题数、策略） |
| results | json | 每题结果：[{point_id, self_score}] |
| total_mastered | int | 完全掌握数 |
| total_partial | int | 部分掌握数 |
| total_unfamiliar | int | 不熟悉数 |
| created_at | datetime | 面试时间 |

---

## 4. 学习路径

按能力层级从基础到高级，LangChain 和 LangGraph 融合为一条路径：

### 基础层级
- **LangChain**：ChatPromptTemplate, MessagesPlaceholder, StrOutputParser, PydanticOutputParser, ChatModel 调用, RunnableSequence (LCEL `|` 管道)
- **LangGraph**：Graph 基本概念, State 定义, Node 定义

### 进阶层级
- **LangChain**：ConversationBufferMemory, RAG (Document Loaders → Text Splitters → Embeddings → Vector Stores → Retriever), Tools 定义与绑定, Agent (create_react_agent), Callbacks
- **LangGraph**：Edges & Conditional Routing, Checkpointing (持久化状态), Human-in-the-loop

### 高级层级
- **LangChain**：Custom Runnable, Streaming (astream_events), RunnableParallel, 性能优化 (批处理/缓存)
- **LangGraph**：Multi-agent 协作, Subgraphs, Dynamic Breakpoints, Command 模式

---

## 5. 页面结构

### 站点地图

```
/ .......................... 首页（仪表盘）
/learn ..................... 学习路径
  /learn/basics ............ 基础层级卡片墙
  /learn/intermediate ...... 进阶层级卡片墙
  /learn/advanced .......... 高级层级卡片墙
  /learn/:id ............... 知识点详情页
/interview ................. 面试模式
  /interview/setup ......... 面试配置
  /interview/session ....... 进行中的面试
  /interview/report/:id .... 面试结果报告
/profile ................... 个人中心
```

### 首页（仪表盘）
- **统计卡片**（4 个）：已掌握知识点数 / 模拟面试次数 / 待复习（薄弱）数 / 最近面试得分
- **今日推荐复习**：优先展示"不熟悉"和"部分掌握"的知识点
- **快捷入口**：继续学习路径 / 开始模拟面试 / 查看薄弱知识点

### 学习路径（卡片墙）
- **筛选栏**：按分类筛选（Prompt / Chain / Agent / Graph 等）
- **排序切换**：面试热度 / 开发实用度 / 学习路径顺序
- **卡片展示**：标题 + 场景一句话 + 双维度评级 + 标签 + 掌握状态
- **掌握状态视觉区分**：绿色边框=已掌握，黄色=部分掌握，灰色=未学习

### 知识点详情页
- **顶部**：标题 + 层级标签 + 双维度评级 + 收藏/标记掌握按钮
- **场景区块**（蓝色高亮）：一段话说清"什么时候用"
- **代码示例**：深色代码块 + 复制按钮，完整可运行
- **核心要点**：2-3 条精炼记忆点
- **常见误区**：错误写法红色标注
- **关联知识点**：可跳转标签

---

## 6. 面试模式

### 面试流程（5 步）

1. **选择范围**（/interview/setup）
   - 分类筛选：LangChain 基础 / LangGraph 基础 / RAG / Agent / 全部
   - 筛选条件：面试热度（仅高频/全部）、难度（基础/进阶/高级/全部）
   - 题数：5 / 10 / 15 / 自定义
   - 出题策略：智能优先（优先不熟悉的）/ 随机 / 顺序

2. **出题**（/interview/session）
   - 展示场景问题，隐藏代码和答案
   - 显示当前进度（第 N/M 题）

3. **思考作答**
   - 用户心中组织答案
   - 可选计时器（建议 2 分钟/题）

4. **揭晓答案**
   - 点击展开：代码示例 + 核心要点 + 常见误区
   - 完整展示，与知识点详情页内容一致

5. **自评打分**
   - 三个选项：完全掌握 / 部分掌握 / 不熟悉
   - 自评结果写入 UserProgress，更新 mastery 状态

### 面试报告（/interview/report/:id）
- 掌握度统计（完全掌握 / 部分 / 不熟悉 各多少题）
- 薄弱点高亮提示，建议重点复习方向
- 历史面试记录可在个人中心查看

### 智能出题策略
- 优先抽取 mastery 为 not_started 或 partial 的知识点
- 其次按 last_reviewed_at 排序，优先复习间隔最久的
- 在筛选范围内随机打乱顺序

---

## 7. API 设计

### 知识点相关
- `GET /api/points` — 获取知识点列表（支持 category, level, sort 参数）
- `GET /api/points/:id` — 获取单个知识点详情

### 用户进度相关
- `GET /api/progress` — 获取用户所有进度（通过 user_id header）
- `PUT /api/progress/:point_id` — 更新某知识点的掌握状态
- `PUT /api/progress/:point_id/favorite` — 切换收藏状态

### 面试相关
- `POST /api/interview/start` — 开始面试（传入配置，返回题目列表）
- `POST /api/interview/:id/answer` — 提交单题自评
- `GET /api/interview/:id/report` — 获取面试报告
- `GET /api/interview/history` — 获取面试历史

### 统计相关
- `GET /api/stats/dashboard` — 首页仪表盘数据
- `GET /api/stats/weak-points` — 薄弱知识点列表

---

## 8. MVP 范围

### 第一阶段（MVP）
- 知识点数据预填充（约 30-45 个核心知识点）
- 日常模式：卡片墙 + 详情页 + 筛选排序
- 面试模式：完整 5 步流程
- 进度追踪：localStorage 存储用户 UUID
- 首页仪表盘

### 后续迭代
- 用户登录/注册（进度云端同步）
- 知识点管理后台（增删改）
- 更多知识点补充
- 代码在线运行（集成 sandbox）
- 社区功能（用户贡献知识点）
