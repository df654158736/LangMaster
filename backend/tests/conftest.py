import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import KnowledgePoint

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_points(db):
    points = [
        KnowledgePoint(
            id=1,
            title="ChatPromptTemplate",
            category="Prompt",
            level="basic",
            interview_heat=3,
            dev_utility=3,
            scenario="当你需要构建带变量的提示词模板时",
            code_example='from langchain_core.prompts import ChatPromptTemplate\n\nprompt = ChatPromptTemplate.from_messages([\n    ("system", "你是一个{role}专家"),\n    ("human", "{question}"),\n])\nmessages = prompt.invoke({"role": "Python", "question": "如何使用列表推导式？"})',
            key_points=["支持 system/human/ai 消息类型", "变量用 {name} 占位", "是 LCEL 链的标准起点"],
            common_mistakes=["混淆 PromptTemplate 和 ChatPromptTemplate", "忘记消息类型元组格式"],
            related_point_ids=[2, 3],
            tags=["langchain", "prompt", "基础"],
            sort_order=1,
        ),
        KnowledgePoint(
            id=2,
            title="RunnableSequence",
            category="Chain",
            level="basic",
            interview_heat=3,
            dev_utility=3,
            scenario="当你需要将多个步骤串联为一个处理管道时",
            code_example='from langchain_core.prompts import ChatPromptTemplate\nfrom langchain_openai import ChatOpenAI\nfrom langchain_core.output_parsers import StrOutputParser\n\nchain = ChatPromptTemplate.from_template("讲一个关于{topic}的笑话") | ChatOpenAI() | StrOutputParser()\nresult = chain.invoke({"topic": "程序员"})',
            key_points=["用 | 管道符串联", "每个组件实现 Runnable 接口", "支持 invoke/ainvoke/stream"],
            common_mistakes=["组件输入输出类型不匹配", "忘记最后加 OutputParser"],
            related_point_ids=[1],
            tags=["langchain", "chain", "LCEL", "基础"],
            sort_order=2,
        ),
        KnowledgePoint(
            id=3,
            title="StateGraph",
            category="Graph",
            level="intermediate",
            interview_heat=3,
            dev_utility=3,
            scenario="当你需要构建有状态的多步骤 Agent 工作流时",
            code_example='from langgraph.graph import StateGraph, START, END\nfrom typing import TypedDict\n\nclass State(TypedDict):\n    messages: list[str]\n    count: int\n\ndef node_a(state: State) -> dict:\n    return {"messages": state["messages"] + ["hello from A"], "count": state["count"] + 1}\n\ngraph = StateGraph(State)\ngraph.add_node("a", node_a)\ngraph.add_edge(START, "a")\ngraph.add_edge("a", END)\napp = graph.compile()\nresult = app.invoke({"messages": [], "count": 0})',
            key_points=["State 用 TypedDict 定义", "add_node 注册节点函数", "add_edge 定义流转"],
            common_mistakes=["忘记 compile()", "State 字段类型不一致"],
            related_point_ids=[],
            tags=["langgraph", "graph", "进阶"],
            sort_order=10,
        ),
    ]
    db.add_all(points)
    db.commit()
    return points
