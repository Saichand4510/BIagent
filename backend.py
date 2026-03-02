from typing import TypedDict, Annotated, List
import os
import aiosqlite

from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
)
from langchain_core.tools import BaseTool

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from tools.bi_tools import (
    get_pipeline_summary,
    get_at_risk_deals,
    get_weighted_forecast,
    get_operational_risks,
)
load_dotenv()

# ============================================================
# 1️⃣ LLM (SECURE)
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    temperature=0.7,
    api_key=GROQ_API_KEY,
)



# ============================================================
# 3️⃣ GLOBAL RUNTIME STATE (initialized at startup)
# ============================================================

tools: List[BaseTool] = []
llm_with_tools = llm
checkpointer: AsyncSqliteSaver | None = None
chatbot = None

# ============================================================
# 4️⃣ STATE
# ============================================================

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ============================================================
# 5️⃣ CHAT NODE
# ============================================================

async def chat_node(state: ChatState):
    messages = state["messages"]

    system_message = SystemMessage(
        content="""
You are a Business Intelligence assistant helping founders
understand sales pipeline, revenue risk, and operational health.

Always use available tools to compute accurate metrics.
Focus on actionable business insights.
"""
    )

    response = await llm_with_tools.ainvoke(
        [system_message] + messages
    )

    return {"messages": [response]}

# ============================================================
# 6️⃣ CHATBOT FACTORY (CALLED BY FASTAPI STARTUP)
# ============================================================

async def create_chatbot():
    """
    Initializes:
    - MCP tools
    - LLM tool binding
    - SQLite checkpointer
    - LangGraph
    """

    global tools, llm_with_tools, checkpointer, chatbot

    # ✅ Load MCP tools
    tools = [
    get_pipeline_summary,
    get_at_risk_deals,
    get_weighted_forecast,
    get_operational_risks,
]
    

    # ✅ Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # ✅ Initialize SQLite checkpointer
    conn = await aiosqlite.connect(database="chatbot.db")
    checkpointer = AsyncSqliteSaver(conn)

    # ✅ Build graph
    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_edge(START, "chat_node")

    if tools:
        tool_node = ToolNode(tools)
        graph.add_node("tools", tool_node)
        graph.add_conditional_edges("chat_node", tools_condition)
        graph.add_edge("tools", "chat_node")
    else:
        graph.add_edge("chat_node", END)

    chatbot = graph.compile(checkpointer=checkpointer)
    return chatbot

# ============================================================
# 7️⃣ THREAD LISTING
# ============================================================

async def _alist_threads():
    if checkpointer is None:
        return []

    all_threads = set()
    async for checkpoint in checkpointer.alist(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


async def retrieve_all_threads():
    return await _alist_threads()