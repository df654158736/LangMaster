from sqlalchemy.orm import Session

from app.models import KnowledgePoint

SEED_DATA = [
    # === BASIC: LangChain ===
    {
        "id": 1,
        "title": "ChatPromptTemplate",
        "category": "Prompt",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要构建带变量的提示词模板，将系统消息、用户消息组合成结构化 prompt 发送给 LLM 时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}专家"),
    ("human", "{question}"),
])
messages = prompt.invoke({"role": "Python", "question": "如何使用列表推导式？"})
print(messages)""",
        "key_points": [
            "支持 system/human/ai/placeholder 四种消息类型",
            "变量用 {variable_name} 占位，invoke 时传入字典",
            "是 LCEL 链的标准起点，可用 | 管道符串联后续步骤",
        ],
        "common_mistakes": [
            "混淆 PromptTemplate（生成字符串）和 ChatPromptTemplate（生成消息列表）",
            "忘记 from_messages 中使用 (role, content) 元组格式",
        ],
        "related_point_ids": [2, 3, 4],
        "tags": ["langchain", "prompt", "基础"],
        "sort_order": 1,
    },
    {
        "id": 2,
        "title": "MessagesPlaceholder",
        "category": "Prompt",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要在 prompt 模板中动态插入一段历史对话消息列表时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
messages = prompt.invoke({
    "history": [("human", "你好"), ("ai", "你好！有什么可以帮你的？")],
    "input": "介绍一下 Python",
})""",
        "key_points": [
            "用于在模板中插入动态数量的历史消息",
            "variable_name 对应 invoke 字典中的 key",
            "常与 Memory 配合实现多轮对话",
        ],
        "common_mistakes": [
            "忘记将 history 作为消息列表传入（传了字符串）",
            "optional=False 时不传 history 会报错",
        ],
        "related_point_ids": [1, 12],
        "tags": ["langchain", "prompt", "memory", "基础"],
        "sort_order": 2,
    },
    {
        "id": 3,
        "title": "StrOutputParser",
        "category": "Output",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要从 LLM 的 AIMessage 响应中提取纯文本字符串时",
        "code_example": """from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_template("用一句话解释{concept}")
    | ChatOpenAI()
    | StrOutputParser()
)
result = chain.invoke({"concept": "递归"})
print(result)  # 纯字符串，不再是 AIMessage 对象""",
        "key_points": [
            "将 AIMessage 对象转为纯字符串",
            "是最常用的 OutputParser，几乎每条链都会用到",
            "放在 LCEL 链末尾，用 | 连接",
        ],
        "common_mistakes": [
            "不加 StrOutputParser 直接使用链，拿到的是 AIMessage 对象而非字符串",
            "对需要结构化输出的场景误用 StrOutputParser（应该用 PydanticOutputParser）",
        ],
        "related_point_ids": [1, 4, 5],
        "tags": ["langchain", "output", "LCEL", "基础"],
        "sort_order": 3,
    },
    {
        "id": 4,
        "title": "PydanticOutputParser",
        "category": "Output",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要 LLM 返回结构化数据（如 JSON 对象）并自动校验格式时",
        "code_example": """from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class Joke(BaseModel):
    setup: str = Field(description="笑话的开头")
    punchline: str = Field(description="笑话的结尾")

parser = PydanticOutputParser(pydantic_object=Joke)
prompt = ChatPromptTemplate.from_template(
    "讲一个关于{topic}的笑话。\\n{format_instructions}"
)
# parser.get_format_instructions() 返回 JSON schema 提示
chain = prompt.partial(format_instructions=parser.get_format_instructions()) | model | parser
result = chain.invoke({"topic": "程序员"})
print(result.setup, result.punchline)""",
        "key_points": [
            "用 Pydantic BaseModel 定义输出结构",
            "get_format_instructions() 生成格式说明注入 prompt",
            "自动解析 + 校验 LLM 输出，返回 Pydantic 对象",
        ],
        "common_mistakes": [
            "忘记在 prompt 中注入 format_instructions",
            "Field description 写得不清楚导致 LLM 输出格式不对",
        ],
        "related_point_ids": [3, 1],
        "tags": ["langchain", "output", "structured", "基础"],
        "sort_order": 4,
    },
    {
        "id": 5,
        "title": "RunnableSequence (LCEL管道)",
        "category": "Chain",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要将多个处理步骤（prompt → model → parser）串联为一个可执行管道时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 用 | 管道符构建 RunnableSequence
chain = (
    ChatPromptTemplate.from_template("翻译成英文：{text}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

# 三种调用方式
result = chain.invoke({"text": "你好世界"})        # 同步
result = await chain.ainvoke({"text": "你好世界"})  # 异步
async for chunk in chain.astream({"text": "你好世界"}):  # 流式
    print(chunk, end="")""",
        "key_points": [
            "| 管道符是 LCEL 的核心语法，创建 RunnableSequence",
            "每个组件实现 Runnable 接口（invoke/ainvoke/stream/astream）",
            "前一个组件的输出自动作为下一个组件的输入",
        ],
        "common_mistakes": [
            "管道中组件的输入输出类型不匹配（如 parser 期望 AIMessage 但收到 str）",
            "在需要异步的环境中使用 invoke 而非 ainvoke",
        ],
        "related_point_ids": [1, 3, 6],
        "tags": ["langchain", "LCEL", "chain", "基础"],
        "sort_order": 5,
    },
    {
        "id": 6,
        "title": "ChatModel 调用",
        "category": "Model",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要直接调用 LLM（如 OpenAI、Anthropic）进行对话时",
        "code_example": """from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

# OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Anthropic
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

# 直接调用
response = llm.invoke([
    SystemMessage(content="你是一个翻译助手"),
    HumanMessage(content="翻译：Hello World"),
])
print(response.content)""",
        "key_points": [
            "ChatOpenAI/ChatAnthropic 等是统一的 ChatModel 接口",
            "输入是 Message 列表，输出是 AIMessage",
            "temperature=0 表示确定性输出，适合需要一致结果的场景",
        ],
        "common_mistakes": [
            "忘记设置 API key 环境变量",
            "混淆 ChatOpenAI（Chat Model）和 OpenAI（旧版 LLM 接口）",
        ],
        "related_point_ids": [1, 5],
        "tags": ["langchain", "model", "基础"],
        "sort_order": 6,
    },
    {
        "id": 7,
        "title": "RunnableParallel",
        "category": "Chain",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要将输入同时分发给多个处理链并合并结果时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

model = ChatOpenAI()

chain = RunnableParallel(
    summary=ChatPromptTemplate.from_template("总结：{text}") | model | StrOutputParser(),
    translation=ChatPromptTemplate.from_template("翻译成英文：{text}") | model | StrOutputParser(),
)
result = chain.invoke({"text": "LangChain 是一个用于构建 LLM 应用的框架"})
print(result["summary"])
print(result["translation"])""",
        "key_points": [
            "多个链并行执行，提高效率",
            "结果以字典形式返回，key 对应每个分支的名称",
            "也可用 dict 语法简写：{\"a\": chain_a, \"b\": chain_b}",
        ],
        "common_mistakes": [
            "所有分支必须接受相同的输入格式",
            "并行分支之间不能有依赖关系",
        ],
        "related_point_ids": [5],
        "tags": ["langchain", "LCEL", "chain", "基础"],
        "sort_order": 7,
    },
    {
        "id": 8,
        "title": "RunnableLambda",
        "category": "Chain",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要在 LCEL 链中插入自定义的 Python 函数作为处理步骤时",
        "code_example": """from langchain_core.runnables import RunnableLambda

def add_prefix(text: str) -> str:
    return f"[重要] {text}"

def word_count(text: str) -> dict:
    return {"text": text, "count": len(text.split())}

# 方式1：显式包装
chain = RunnableLambda(add_prefix) | RunnableLambda(word_count)

# 方式2：用 @chain 装饰器（推荐）
from langchain_core.runnables import chain as chain_decorator

@chain_decorator
def my_step(input: str) -> str:
    return input.upper()

result = chain.invoke("hello world")""",
        "key_points": [
            "将普通 Python 函数转为 Runnable，可加入 LCEL 管道",
            "函数签名决定输入输出类型",
            "@chain 装饰器是更优雅的写法",
        ],
        "common_mistakes": [
            "函数返回类型与下一个组件期望的输入类型不匹配",
            "在 Lambda 中做了耗时操作但没有用异步版本",
        ],
        "related_point_ids": [5, 7],
        "tags": ["langchain", "LCEL", "chain", "基础"],
        "sort_order": 8,
    },
    # === BASIC: LangGraph ===
    {
        "id": 9,
        "title": "StateGraph 基本概念",
        "category": "Graph",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要构建有状态的、多步骤的 Agent 工作流时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. 定义状态
class State(TypedDict):
    messages: list[str]
    count: int

# 2. 定义节点（普通函数）
def greet(state: State) -> dict:
    return {
        "messages": state["messages"] + ["Hello!"],
        "count": state["count"] + 1,
    }

# 3. 构建图
graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_edge(START, "greet")
graph.add_edge("greet", END)

# 4. 编译并运行
app = graph.compile()
result = app.invoke({"messages": [], "count": 0})
print(result)  # {"messages": ["Hello!"], "count": 1}""",
        "key_points": [
            "State 用 TypedDict 定义，是贯穿所有节点的共享状态",
            "节点是普通函数，接收 State 返回部分更新",
            "必须 compile() 后才能 invoke()",
        ],
        "common_mistakes": [
            "忘记调用 compile()",
            "节点函数返回完整 State 而非部分更新字典",
            "没有连接 START → 第一个节点",
        ],
        "related_point_ids": [10, 11],
        "tags": ["langgraph", "graph", "state", "基础"],
        "sort_order": 9,
    },
    {
        "id": 10,
        "title": "State 与 Annotation",
        "category": "Graph",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要定义图的状态结构，特别是需要对列表字段做追加操作而非覆盖时",
        "code_example": """from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from operator import add

# 用 Annotated + reducer 定义追加行为
class State(TypedDict):
    messages: Annotated[list[str], add]  # add = 列表追加
    count: int                            # 普通字段 = 覆盖

def node_a(state: State) -> dict:
    return {"messages": ["from A"], "count": 1}  # messages 会追加，count 会覆盖

def node_b(state: State) -> dict:
    return {"messages": ["from B"], "count": 2}

graph = StateGraph(State)
graph.add_node("a", node_a)
graph.add_node("b", node_b)
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_edge("b", END)
app = graph.compile()
result = app.invoke({"messages": [], "count": 0})
print(result)  # {"messages": ["from A", "from B"], "count": 2}""",
        "key_points": [
            "Annotated[type, reducer] 定义字段的合并策略",
            "operator.add 对列表做追加，对数字做累加",
            "没有 Annotation 的字段默认是覆盖行为",
        ],
        "common_mistakes": [
            "对 messages 不加 Annotated[..., add]，导致后面节点覆盖前面的消息",
            "reducer 函数签名不对（需要接收两个参数并返回合并结果）",
        ],
        "related_point_ids": [9, 11],
        "tags": ["langgraph", "state", "annotation", "基础"],
        "sort_order": 10,
    },
    {
        "id": 11,
        "title": "Node 与 Edge",
        "category": "Graph",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要在图中定义多个处理节点并指定它们之间的执行顺序时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    value: str

def step1(state: State) -> dict:
    return {"value": state["value"] + " -> step1"}

def step2(state: State) -> dict:
    return {"value": state["value"] + " -> step2"}

graph = StateGraph(State)
# 添加节点
graph.add_node("step1", step1)
graph.add_node("step2", step2)
# 添加边（定义顺序）
graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", END)

app = graph.compile()
result = app.invoke({"value": "start"})
print(result["value"])  # "start -> step1 -> step2" """,
        "key_points": [
            "add_node(name, func) 注册节点",
            "add_edge(from, to) 定义节点间的固定连接",
            "START 和 END 是内置的特殊节点",
        ],
        "common_mistakes": [
            "节点名称拼写不一致（add_node 和 add_edge 中的名称不匹配）",
            "形成了死循环没有通往 END 的路径",
        ],
        "related_point_ids": [9, 10, 15],
        "tags": ["langgraph", "graph", "基础"],
        "sort_order": 11,
    },
    # === INTERMEDIATE: LangChain ===
    {
        "id": 12,
        "title": "ConversationBufferMemory",
        "category": "Memory",
        "level": "intermediate",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要让 LLM 记住之前的对话内容实现多轮对话时",
        "code_example": """from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

memory = ConversationBufferMemory(return_messages=True)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = (
    RunnablePassthrough.assign(history=lambda _: memory.load_memory_variables({})["history"])
    | prompt
    | ChatOpenAI()
    | StrOutputParser()
)

# 对话
response = chain.invoke({"input": "我叫小明"})
memory.save_context({"input": "我叫小明"}, {"output": response})
response = chain.invoke({"input": "我叫什么？"})  # 能记住""",
        "key_points": [
            "return_messages=True 让 memory 返回消息对象而非字符串",
            "需要手动 save_context 保存每轮对话",
            "在 LangGraph 中推荐用 Checkpointing 替代 Memory",
        ],
        "common_mistakes": [
            "忘记 save_context 导致 LLM '失忆'",
            "在高并发场景使用 BufferMemory（不是线程安全的）",
        ],
        "related_point_ids": [2, 18],
        "tags": ["langchain", "memory", "进阶"],
        "sort_order": 12,
    },
    {
        "id": 13,
        "title": "Document Loaders",
        "category": "Retrieval",
        "level": "intermediate",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要从文件（PDF/TXT/CSV）、网页或数据库中加载文档用于 RAG 时",
        "code_example": """from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    WebBaseLoader,
)

# 加载文本文件
docs = TextLoader("data.txt").load()

# 加载 PDF
docs = PyPDFLoader("report.pdf").load()

# 加载网页
docs = WebBaseLoader("https://example.com").load()

# 每个 Document 有 page_content 和 metadata
for doc in docs:
    print(doc.page_content[:100])
    print(doc.metadata)""",
        "key_points": [
            "所有 Loader 都有统一的 .load() 接口，返回 Document 列表",
            "Document 包含 page_content（文本）和 metadata（来源信息）",
            "是 RAG 管道的第一步：加载 → 切分 → 嵌入 → 检索",
        ],
        "common_mistakes": [
            "忘记安装对应的依赖包（如 pypdf、beautifulsoup4）",
            "对大文件直接 load() 导致内存溢出（应该用 lazy_load()）",
        ],
        "related_point_ids": [14, 15, 16],
        "tags": ["langchain", "RAG", "retrieval", "进阶"],
        "sort_order": 13,
    },
    {
        "id": 14,
        "title": "Text Splitters",
        "category": "Retrieval",
        "level": "intermediate",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要将长文档切分为适合嵌入和检索的小块时",
        "code_example": """from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\\n\\n", "\\n", "。", "，", " ", ""],
)

text = "这是一段很长的文本..." * 100
chunks = splitter.split_text(text)
print(f"切分为 {len(chunks)} 个块")

# 也可以直接对 Document 列表操作
from langchain_community.document_loaders import TextLoader
docs = TextLoader("data.txt").load()
split_docs = splitter.split_documents(docs)""",
        "key_points": [
            "RecursiveCharacterTextSplitter 是最常用的切分器",
            "chunk_size 控制每块大小，chunk_overlap 控制重叠",
            "separators 按优先级尝试，先按段落分，再按句子分",
        ],
        "common_mistakes": [
            "chunk_size 设太大导致检索不精确，设太小丢失上下文",
            "忘记设 chunk_overlap 导致跨块信息丢失",
        ],
        "related_point_ids": [13, 15, 16],
        "tags": ["langchain", "RAG", "retrieval", "进阶"],
        "sort_order": 14,
    },
    {
        "id": 15,
        "title": "Embeddings + Vector Store",
        "category": "Retrieval",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要将文档块转为向量并存储到向量数据库以支持语义检索时",
        "code_example": """from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. 准备嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. 从文档创建向量库
from langchain_text_splitters import RecursiveCharacterTextSplitter
texts = ["LangChain 是一个框架", "LangGraph 用于构建 Agent", "RAG 是检索增强生成"]
vectorstore = FAISS.from_texts(texts, embeddings)

# 3. 相似性搜索
results = vectorstore.similarity_search("什么是 Agent？", k=2)
for doc in results:
    print(doc.page_content)

# 4. 转为 Retriever 用于链
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})""",
        "key_points": [
            "Embeddings 将文本转为向量，VectorStore 存储和检索向量",
            "FAISS 适合本地开发，生产可用 Pinecone/Chroma/Weaviate",
            "as_retriever() 将向量库转为 Retriever 接口，可加入 LCEL 链",
        ],
        "common_mistakes": [
            "嵌入模型和查询用了不同的模型导致检索效果差",
            "k 值设太大导致上下文过长超出 LLM 窗口",
        ],
        "related_point_ids": [13, 14, 16],
        "tags": ["langchain", "RAG", "embeddings", "vector", "进阶"],
        "sort_order": 15,
    },
    {
        "id": 16,
        "title": "RAG 完整链",
        "category": "Retrieval",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要构建完整的检索增强生成管道，让 LLM 基于你的文档回答问题时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 假设 vectorstore 已创建
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template(
    \"\"\"基于以下上下文回答问题。如果上下文中没有相关信息，说"我不确定"。

上下文：{context}

问题：{question}\"\"\"
)

def format_docs(docs):
    return "\\n\\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | ChatOpenAI()
    | StrOutputParser()
)

answer = rag_chain.invoke("LangGraph 是什么？")""",
        "key_points": [
            "RAG = Retriever + Prompt + LLM，是最常见的 LLM 应用模式",
            "RunnablePassthrough() 将用户输入直接传递到 question",
            "retriever | format_docs 将检索结果格式化为上下文字符串",
        ],
        "common_mistakes": [
            "prompt 中没有明确告诉 LLM '基于上下文回答'导致幻觉",
            "format_docs 中没有分隔文档导致上下文混乱",
        ],
        "related_point_ids": [13, 14, 15, 5],
        "tags": ["langchain", "RAG", "进阶"],
        "sort_order": 16,
    },
    {
        "id": 17,
        "title": "Tools 定义与绑定",
        "category": "Tools",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要让 LLM 调用外部函数（如搜索、计算、API调用）时",
        "code_example": """from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def search(query: str) -> str:
    \"\"\"搜索互联网获取最新信息\"\"\"
    return f"搜索结果：关于 {query} 的最新信息..."

@tool
def calculator(expression: str) -> str:
    \"\"\"计算数学表达式\"\"\"
    return str(eval(expression))

# 将工具绑定到模型
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([search, calculator])

# 模型会决定是否调用工具
response = llm_with_tools.invoke("2024年奥运会在哪里举办？")
print(response.tool_calls)  # [{"name": "search", "args": {...}}]""",
        "key_points": [
            "@tool 装饰器将函数转为 Tool，docstring 作为工具描述",
            "bind_tools() 让 LLM 知道可用工具，但不自动执行",
            "LLM 返回 tool_calls 列表，需要你自己执行并返回结果",
        ],
        "common_mistakes": [
            "tool 的 docstring 写得不清楚导致 LLM 不知道何时调用",
            "以为 bind_tools 会自动执行工具（需要配合 Agent 或手动执行）",
        ],
        "related_point_ids": [18, 19],
        "tags": ["langchain", "tools", "agent", "进阶"],
        "sort_order": 17,
    },
    {
        "id": 18,
        "title": "create_react_agent",
        "category": "Agent",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要快速创建一个能自主决定使用工具的 ReAct Agent 时",
        "code_example": """from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    \"\"\"获取城市天气\"\"\"
    return f"{city}今天晴，25°C"

@tool
def search(query: str) -> str:
    \"\"\"搜索信息\"\"\"
    return f"搜索结果：{query}"

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools=[get_weather, search])

# Agent 自动决定用哪个工具
result = agent.invoke({
    "messages": [("human", "北京今天天气怎么样？")]
})
print(result["messages"][-1].content)""",
        "key_points": [
            "create_react_agent 是 LangGraph 提供的预构建 Agent",
            "Agent 自动循环：思考 → 选择工具 → 执行 → 观察 → 继续/结束",
            "底层是 LangGraph 的 StateGraph，可自定义扩展",
        ],
        "common_mistakes": [
            "tools 列表为空（Agent 没有工具可用）",
            "工具太多导致 LLM 选择混乱（建议 5-10 个以内）",
        ],
        "related_point_ids": [17, 9, 19],
        "tags": ["langchain", "langgraph", "agent", "进阶"],
        "sort_order": 18,
    },
    {
        "id": 19,
        "title": "Callbacks",
        "category": "Chain",
        "level": "intermediate",
        "interview_heat": 1,
        "dev_utility": 2,
        "scenario": "当你需要监控链的执行过程（日志、token计数、延迟追踪）时",
        "code_example": """from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

class MyCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"LLM 开始调用，prompt 长度: {len(prompts[0])}")

    def on_llm_end(self, response, **kwargs):
        print(f"LLM 结束，token 使用: {response.llm_output}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"Chain 开始: {serialized.get('name', 'unknown')}")

llm = ChatOpenAI(callbacks=[MyCallback()])
result = llm.invoke("你好")

# 也可以在 invoke 时传入
result = llm.invoke("你好", config={"callbacks": [MyCallback()]})""",
        "key_points": [
            "继承 BaseCallbackHandler 实现需要的钩子方法",
            "可在构造时或 invoke 时传入 callbacks",
            "常用于日志、监控、token 计费",
        ],
        "common_mistakes": [
            "在 callback 中做耗时操作阻塞主流程",
            "忘记异步场景需要用 AsyncCallbackHandler",
        ],
        "related_point_ids": [5, 6],
        "tags": ["langchain", "callbacks", "monitoring", "进阶"],
        "sort_order": 19,
    },
    # === INTERMEDIATE: LangGraph ===
    {
        "id": 20,
        "title": "Conditional Edges",
        "category": "Graph",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要根据状态动态决定下一步执行哪个节点时（条件分支）",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    input: str
    category: str

def classify(state: State) -> dict:
    if "天气" in state["input"]:
        return {"category": "weather"}
    return {"category": "general"}

def handle_weather(state: State) -> dict:
    return {"input": f"天气查询：{state['input']}"}

def handle_general(state: State) -> dict:
    return {"input": f"通用回答：{state['input']}"}

def route(state: State) -> str:
    if state["category"] == "weather":
        return "weather"
    return "general"

graph = StateGraph(State)
graph.add_node("classify", classify)
graph.add_node("weather", handle_weather)
graph.add_node("general", handle_general)

graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route, {"weather": "weather", "general": "general"})
graph.add_edge("weather", END)
graph.add_edge("general", END)

app = graph.compile()""",
        "key_points": [
            "add_conditional_edges(source, func, mapping) 实现条件路由",
            "路由函数接收 State，返回字符串 key",
            "mapping 字典将返回值映射到目标节点名称",
        ],
        "common_mistakes": [
            "路由函数返回值不在 mapping 字典中导致运行时报错",
            "忘记为所有分支都连接到 END（或下一个节点）",
        ],
        "related_point_ids": [9, 11, 21],
        "tags": ["langgraph", "graph", "routing", "进阶"],
        "sort_order": 20,
    },
    {
        "id": 21,
        "title": "Checkpointing (持久化状态)",
        "category": "Graph",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要保存图的执行状态，支持暂停/恢复、多轮对话记忆或故障恢复时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]

def chat(state: State) -> dict:
    last_msg = state["messages"][-1]
    return {"messages": [f"回复：{last_msg}"]}

graph = StateGraph(State)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

# 添加 checkpointer
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# 用 thread_id 区分不同对话
config = {"configurable": {"thread_id": "user-123"}}

result = app.invoke({"messages": ["你好"]}, config=config)
result = app.invoke({"messages": ["我叫小明"]}, config=config)
# messages 会累积：["你好", "回复：你好", "我叫小明", "回复：我叫小明"]""",
        "key_points": [
            "compile(checkpointer=...) 启用状态持久化",
            "MemorySaver 存内存（开发用），SqliteSaver/PostgresSaver 存数据库（生产用）",
            "thread_id 区分不同会话/用户的状态",
        ],
        "common_mistakes": [
            "忘记传 config 中的 thread_id 导致所有用户共享状态",
            "开发用 MemorySaver 但部署到生产（重启后状态丢失）",
        ],
        "related_point_ids": [9, 10, 22],
        "tags": ["langgraph", "checkpoint", "memory", "进阶"],
        "sort_order": 21,
    },
    {
        "id": 22,
        "title": "Human-in-the-loop",
        "category": "Graph",
        "level": "intermediate",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要在 Agent 执行过程中暂停等待人工审批或输入时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

class State(TypedDict):
    query: str
    plan: str
    approved: bool
    result: str

def make_plan(state: State) -> dict:
    return {"plan": f"计划处理: {state['query']}"}

def execute(state: State) -> dict:
    return {"result": f"执行完成: {state['plan']}"}

graph = StateGraph(State)
graph.add_node("plan", make_plan)
graph.add_node("execute", execute)
graph.add_edge(START, "plan")
graph.add_edge("plan", "execute")  # interrupt_before 会在这里暂停
graph.add_edge("execute", END)

app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["execute"],  # 在 execute 前暂停
)

config = {"configurable": {"thread_id": "t1"}}
result = app.invoke({"query": "删除所有数据", "approved": False, "plan": "", "result": ""}, config=config)
print(result["plan"])  # 展示计划给用户

# 用户审批后，更新状态并继续
app.update_state(config, {"approved": True})
result = app.invoke(None, config=config)  # 从暂停点继续""",
        "key_points": [
            "interrupt_before/interrupt_after 指定暂停点",
            "需要 checkpointer 才能暂停和恢复",
            "update_state() 注入人工输入后 invoke(None) 继续执行",
        ],
        "common_mistakes": [
            "没有配置 checkpointer 就使用 interrupt（会报错）",
            "invoke(None) 时忘记传 config 导致找不到暂停的状态",
        ],
        "related_point_ids": [21, 9],
        "tags": ["langgraph", "human-in-the-loop", "interrupt", "进阶"],
        "sort_order": 22,
    },
    # === ADVANCED: LangChain ===
    {
        "id": 23,
        "title": "Streaming (流式输出)",
        "category": "Chain",
        "level": "advanced",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要让 LLM 的回答逐字逐句显示（打字机效果）而非等待完整响应时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_template("写一首关于{topic}的诗")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

# 方式1：stream（同步流式）
for chunk in chain.stream({"topic": "春天"}):
    print(chunk, end="", flush=True)

# 方式2：astream（异步流式）
async for chunk in chain.astream({"topic": "春天"}):
    print(chunk, end="", flush=True)

# 方式3：astream_events（获取中间步骤事件）
async for event in chain.astream_events({"topic": "春天"}, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")""",
        "key_points": [
            "stream/astream 获取最终输出的流式 chunk",
            "astream_events 可获取链中每个步骤的事件（调试利器）",
            "流式输出对用户体验至关重要，生产环境必备",
        ],
        "common_mistakes": [
            "在 FastAPI 中用 stream 而不是 astream（阻塞事件循环）",
            "流式输出时忘记 flush 导致输出积攒",
        ],
        "related_point_ids": [5, 6],
        "tags": ["langchain", "streaming", "高级"],
        "sort_order": 23,
    },
    {
        "id": 24,
        "title": "Custom Runnable",
        "category": "Chain",
        "level": "advanced",
        "interview_heat": 1,
        "dev_utility": 2,
        "scenario": "当你需要创建一个完全自定义的 Runnable 组件加入 LCEL 链，且需要支持流式/异步时",
        "code_example": """from langchain_core.runnables import RunnableGenerator
from typing import Iterator

# 方式1：RunnableGenerator（最简单）
def streaming_transform(chunks: Iterator[str]) -> Iterator[str]:
    buffer = ""
    for chunk in chunks:
        buffer += chunk
        if "。" in buffer:
            parts = buffer.split("。")
            for part in parts[:-1]:
                yield part + "。\\n"
            buffer = parts[-1]
    if buffer:
        yield buffer

transform = RunnableGenerator(streaming_transform)

# 方式2：继承 Runnable（完全控制）
from langchain_core.runnables import Runnable, RunnableConfig

class MyRunnable(Runnable):
    def invoke(self, input, config: RunnableConfig | None = None):
        return input.upper()

    async def ainvoke(self, input, config: RunnableConfig | None = None):
        return input.upper()

chain = some_chain | transform  # 加入管道""",
        "key_points": [
            "RunnableGenerator 适合流式转换场景",
            "继承 Runnable 需实现 invoke，可选 ainvoke/stream/astream",
            "自定义 Runnable 自动获得 batch/abatch 等能力",
        ],
        "common_mistakes": [
            "只实现 invoke 不实现 ainvoke，在异步环境中阻塞",
            "流式处理时没有正确处理 chunk 边界",
        ],
        "related_point_ids": [5, 8, 23],
        "tags": ["langchain", "LCEL", "custom", "高级"],
        "sort_order": 24,
    },
    {
        "id": 25,
        "title": "Batch 批处理",
        "category": "Chain",
        "level": "advanced",
        "interview_heat": 1,
        "dev_utility": 2,
        "scenario": "当你需要同时处理多个输入以提高吞吐量时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_template("用一句话解释{concept}")
    | ChatOpenAI()
    | StrOutputParser()
)

# 批量调用
results = chain.batch([
    {"concept": "递归"},
    {"concept": "闭包"},
    {"concept": "多态"},
], config={"max_concurrency": 3})

# 异步批量
results = await chain.abatch([
    {"concept": "递归"},
    {"concept": "闭包"},
])

for r in results:
    print(r)""",
        "key_points": [
            "batch/abatch 接受输入列表，返回结果列表",
            "max_concurrency 控制最大并发数",
            "比循环调用 invoke 更高效（并发执行）",
        ],
        "common_mistakes": [
            "不设 max_concurrency 导致触发 API 限流",
            "batch 列表太大导致内存压力",
        ],
        "related_point_ids": [5, 23],
        "tags": ["langchain", "batch", "性能", "高级"],
        "sort_order": 25,
    },
    # === ADVANCED: LangGraph ===
    {
        "id": 26,
        "title": "Multi-Agent 协作",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 3,
        "dev_utility": 2,
        "scenario": "当你需要多个 Agent 协作完成复杂任务（如一个负责研究，一个负责写作）时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]
    task: str

llm = ChatOpenAI()

def researcher(state: State) -> dict:
    # 研究 Agent：收集信息
    response = llm.invoke(f"研究以下主题并列出要点：{state['task']}")
    return {"messages": [f"[研究员] {response.content}"]}

def writer(state: State) -> dict:
    # 写作 Agent：基于研究结果撰写
    context = "\\n".join(state["messages"])
    response = llm.invoke(f"基于以下研究写一篇文章：\\n{context}")
    return {"messages": [f"[写手] {response.content}"]}

def reviewer(state: State) -> dict:
    # 审稿 Agent：检查质量
    context = "\\n".join(state["messages"])
    response = llm.invoke(f"审查以下内容并给出修改建议：\\n{context}")
    return {"messages": [f"[审稿] {response.content}"]}

graph = StateGraph(State)
graph.add_node("researcher", researcher)
graph.add_node("writer", writer)
graph.add_node("reviewer", reviewer)
graph.add_edge(START, "researcher")
graph.add_edge("researcher", "writer")
graph.add_edge("writer", "reviewer")
graph.add_edge("reviewer", END)

app = graph.compile()
result = app.invoke({"messages": [], "task": "AI Agent 的发展趋势"})""",
        "key_points": [
            "每个 Agent 是图中的一个节点，共享 State 通信",
            "Agent 之间通过 State 中的 messages 传递信息",
            "可用条件边实现更复杂的协作模式（如循环审稿直到通过）",
        ],
        "common_mistakes": [
            "Agent 之间信息传递不充分，后续 Agent 缺少上下文",
            "循环协作没有设退出条件导致无限循环",
        ],
        "related_point_ids": [9, 20, 27],
        "tags": ["langgraph", "multi-agent", "高级"],
        "sort_order": 26,
    },
    {
        "id": 27,
        "title": "Subgraphs (子图)",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要将复杂图拆分为可复用的模块，或在图中嵌套另一个图时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 子图：处理订单
class OrderState(TypedDict):
    order_id: str
    status: str

def validate(state: OrderState) -> dict:
    return {"status": "validated"}

def process(state: OrderState) -> dict:
    return {"status": "processed"}

order_graph = StateGraph(OrderState)
order_graph.add_node("validate", validate)
order_graph.add_node("process", process)
order_graph.add_edge(START, "validate")
order_graph.add_edge("validate", "process")
order_graph.add_edge("process", END)
order_subgraph = order_graph.compile()

# 主图
class MainState(TypedDict):
    order_id: str
    status: str
    result: str

def prepare(state: MainState) -> dict:
    return {"result": "准备中"}

def finalize(state: MainState) -> dict:
    return {"result": f"订单 {state['order_id']} 完成，状态: {state['status']}"}

main_graph = StateGraph(MainState)
main_graph.add_node("prepare", prepare)
main_graph.add_node("order", order_subgraph)  # 嵌入子图
main_graph.add_node("finalize", finalize)
main_graph.add_edge(START, "prepare")
main_graph.add_edge("prepare", "order")
main_graph.add_edge("order", "finalize")
main_graph.add_edge("finalize", END)

app = main_graph.compile()""",
        "key_points": [
            "子图是独立的 compiled graph，作为节点嵌入父图",
            "父图和子图通过共享的 State 字段通信",
            "子图内部的节点对父图透明，实现封装",
        ],
        "common_mistakes": [
            "父图和子图的 State 没有重叠字段导致无法通信",
            "子图内部的 checkpointer 和父图冲突",
        ],
        "related_point_ids": [9, 26, 28],
        "tags": ["langgraph", "subgraph", "模块化", "高级"],
        "sort_order": 27,
    },
    {
        "id": 28,
        "title": "Dynamic Breakpoints",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 1,
        "dev_utility": 2,
        "scenario": "当你需要在运行时根据条件动态决定是否暂停执行（而非编译时固定暂停点）时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from typing import TypedDict

class State(TypedDict):
    input: str
    risk_level: str
    result: str

def analyze(state: State) -> dict:
    if "删除" in state["input"] or "drop" in state["input"].lower():
        return {"risk_level": "high"}
    return {"risk_level": "low"}

def execute(state: State) -> dict:
    # 动态中断：高风险操作需要人工确认
    if state["risk_level"] == "high":
        raise NodeInterrupt(
            f"高风险操作检测到: {state['input']}，需要人工确认"
        )
    return {"result": f"已执行: {state['input']}"}

graph = StateGraph(State)
graph.add_node("analyze", analyze)
graph.add_node("execute", execute)
graph.add_edge(START, "analyze")
graph.add_edge("analyze", "execute")
graph.add_edge("execute", END)

app = graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "t1"}}
result = app.invoke({"input": "删除所有用户数据", "risk_level": "", "result": ""}, config=config)
# 高风险 → NodeInterrupt 触发 → 暂停

# 人工确认后继续
app.update_state(config, {"risk_level": "low"})  # 降级风险
result = app.invoke(None, config=config)""",
        "key_points": [
            "raise NodeInterrupt(reason) 在节点内部动态触发暂停",
            "比 interrupt_before/after 更灵活，可基于运行时条件判断",
            "同样需要 checkpointer 支持暂停/恢复",
        ],
        "common_mistakes": [
            "NodeInterrupt 后忘记 update_state 就调用 invoke(None)，会再次触发中断",
            "没有 checkpointer 时 raise NodeInterrupt 会直接报错",
        ],
        "related_point_ids": [22, 21],
        "tags": ["langgraph", "interrupt", "dynamic", "高级"],
        "sort_order": 28,
    },
    {
        "id": 29,
        "title": "Command 模式",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要在节点内部同时更新状态和控制路由（跳转到指定节点）时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict

class State(TypedDict):
    input: str
    stage: str

def router_node(state: State) -> Command:
    if "紧急" in state["input"]:
        return Command(
            update={"stage": "urgent"},
            goto="urgent_handler",  # 直接跳转
        )
    return Command(
        update={"stage": "normal"},
        goto="normal_handler",
    )

def urgent_handler(state: State) -> dict:
    return {"input": f"[紧急处理] {state['input']}"}

def normal_handler(state: State) -> dict:
    return {"input": f"[常规处理] {state['input']}"}

graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("urgent_handler", urgent_handler)
graph.add_node("normal_handler", normal_handler)
graph.add_edge(START, "router")
# 不需要 add_conditional_edges，Command.goto 已处理路由
graph.add_edge("urgent_handler", END)
graph.add_edge("normal_handler", END)

app = graph.compile()""",
        "key_points": [
            "Command(update=..., goto=...) 同时更新状态和控制流转",
            "比 conditional_edges 更灵活，路由逻辑在节点内部",
            "goto 可以是单个节点名或节点名列表（并行分发）",
        ],
        "common_mistakes": [
            "返回 Command 的节点不能同时有 add_conditional_edges",
            "goto 指向不存在的节点名",
        ],
        "related_point_ids": [20, 9],
        "tags": ["langgraph", "command", "routing", "高级"],
        "sort_order": 29,
    },
    {
        "id": 30,
        "title": "LangGraph Streaming",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要实时获取图执行过程中每个节点的状态更新和 LLM 输出流时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]

def node_a(state: State) -> dict:
    return {"messages": ["A done"]}

def node_b(state: State) -> dict:
    return {"messages": ["B done"]}

graph = StateGraph(State)
graph.add_node("a", node_a)
graph.add_node("b", node_b)
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_edge("b", END)
app = graph.compile()

# stream_mode="updates" — 每个节点完成后发送更新
for event in app.stream({"messages": []}, stream_mode="updates"):
    print(event)
    # {"a": {"messages": ["A done"]}}
    # {"b": {"messages": ["B done"]}}

# stream_mode="values" — 每步发送完整状态
for event in app.stream({"messages": []}, stream_mode="values"):
    print(event)

# 多种模式同时使用
for mode, event in app.stream({"messages": []}, stream_mode=["updates", "values"]):
    print(f"[{mode}] {event}")""",
        "key_points": [
            "stream_mode='updates' 只返回每步的增量更新",
            "stream_mode='values' 返回每步后的完整状态",
            "可同时传多个 stream_mode 获取不同粒度的事件",
        ],
        "common_mistakes": [
            "混淆 updates 和 values 模式导致解析错误",
            "在异步环境用 stream 而非 astream",
        ],
        "related_point_ids": [23, 9],
        "tags": ["langgraph", "streaming", "高级"],
        "sort_order": 30,
    },
]


def seed_database(db):
    """Seed database with knowledge points if empty."""
    if db.query(KnowledgePoint).count() > 0:
        return
    for data in SEED_DATA:
        point = KnowledgePoint(**data)
        db.add(point)
    db.commit()
