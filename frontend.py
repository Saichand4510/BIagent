import uuid
import requests
import streamlit as st

# =========================
# Config
# =========================
API_BASE = "https://biagent-820l.onrender.com"

# =========================== Utilities ===========================

def create_thread_api():
    r = requests.post(f"{API_BASE}/threads")
    r.raise_for_status()
    return r.json()["thread_id"]


def fetch_threads_api():
    r = requests.get(f"{API_BASE}/threads")
    r.raise_for_status()
    return r.json()["threads"]


def load_conversation_api(thread_id):
    r = requests.get(f"{API_BASE}/threads/{thread_id}")
    r.raise_for_status()
    return r.json()["messages"]


def stream_chat_api(thread_id, user_input):
    """Stream assistant tokens from FastAPI"""
    with requests.post(
        f"{API_BASE}/chat/stream",
        json={"thread_id": thread_id, "message": user_input},
        stream=True,
    ) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def reset_chat():
    thread_id = create_thread_api()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


# ======================= Session Initialization ===================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = create_thread_api()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = fetch_threads_api()

add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================

st.sidebar.title("LangGraph MCP Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state["chat_threads"][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation_api(thread_id)
        st.session_state["message_history"] = messages

# ============================ Main UI ============================

# Render history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type here")

# ============================ Chat ============================

if user_input:
    # show user message
    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.text(user_input)

    # assistant streaming
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            stream_chat_api(st.session_state["thread_id"], user_input)
        )

    # save assistant response
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )