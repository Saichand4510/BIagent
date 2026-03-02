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

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    CONFIG = get_config(request.thread_id)

    async def event_generator():
        try:
            async for message_chunk, metadata in chatbot.astream(
                {"messages": [HumanMessage(content=request.message)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        except Exception as e:
            yield f"\n[ERROR]: {str(e)}"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
    )