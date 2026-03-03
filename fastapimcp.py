import uuid
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, AIMessage

from backend import (
    create_chatbot,
    retrieve_all_threads,
)
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="LangGraph MCP API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
chatbot = None


@app.on_event("startup")
async def startup_event():
    global chatbot
    chatbot = await create_chatbot()
# =========================
# Request / Response Models
# =========================

class ChatRequest(BaseModel):
    thread_id: str
    message: str


class ThreadResponse(BaseModel):
    thread_id: str


# =========================
# Utilities
# =========================

def generate_thread_id() -> str:
    return str(uuid.uuid4())


def get_config(thread_id: str):
    return {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id},
        "run_name": "chat_turn",
    }



# =========================
# 1️⃣ Create new chat
# =========================

@app.post("/threads", response_model=ThreadResponse)
async def create_thread():
    thread_id = generate_thread_id()

    # initialize empty state
    await chatbot.ainvoke(
        {"messages": []},
        config=get_config(thread_id),
    )

    return ThreadResponse(thread_id=thread_id)


# =========================
# 2️⃣ List threads
# =========================

@app.get("/threads")
async def list_threads():
    threads =await retrieve_all_threads()
    return {"threads": threads}


# =========================
# 3️⃣ Get conversation history
# =========================

@app.get("/threads/{thread_id}")
async def get_thread_messages(thread_id: str):
    state =await chatbot.aget_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    messages = state.values.get("messages", [])

    formatted = []
    for msg in messages:
        role = "assistant"
        if isinstance(msg, HumanMessage):
            role = "user"

        formatted.append({
    "role": role,
    "content":msg.content,
})

    return {"messages": formatted}


# =========================
# 4️⃣ Chat (STREAMING) ⭐⭐⭐
# =========================

import json
from langchain_core.messages import HumanMessage


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    CONFIG = get_config(request.thread_id)

    async def event_generator():
        try:
            async for event in chatbot.astream_events(
                {"messages": [HumanMessage(content=request.message)]},
                config=CONFIG,
            ):

                event_type = event["event"]

                # 🔧 Tool started
                if event_type == "on_tool_start":
                    yield json.dumps({
                        "type": "tool_start",
                        "name": event["name"]
                    }) + "\n"

                # ✅ Tool finished
                elif event_type == "on_tool_end":
                    yield json.dumps({
                        "type": "tool_end"
                    }) + "\n"

                # 🤖 Assistant token streaming
                elif event_type == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        yield json.dumps({
                            "type": "assistant",
                            "content": chunk.content
                        }) + "\n"

        except Exception as e:
            yield json.dumps({
                "type": "assistant",
                "content": f"\n[ERROR]: {str(e)}"
            }) + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
    )