# AI Business Intelligence Agent

## Overview
This project implements an AI-powered Business Intelligence agent that answers founder-level questions using live data from monday.com Deals and Work Orders boards.

The agent cleans messy business data, performs analytics via tools, and returns actionable insights conversationally.

---

## Features

- Live monday.com integration (GraphQL API)
- No data caching (fresh on every query)
- Tool-based analytics layer
- Conversational BI assistant
- Async FastAPI backend
- Streamlit frontend
- Persistent chat memory (SQLite)
- Visible tool-call traces

---

## Architecture

User → Streamlit → FastAPI → LangGraph Agent → BI Tools → monday.com API

---

## Setup

### 1. Environment Variables

Create `.env`:

```
MONDAY_API_KEY=your_key
DEALS_BOARD_ID=your_id
WORK_ORDERS_BOARD_ID=your_id
GROQ_API_KEY=your_key
```

---

### 2. Install Dependencies

```
pip install -r requirements.txt
```

---

### 3. Run Backend

```
uvicorn fastapimcp:app --reload
```

---

### 4. Run Frontend

```
streamlit run frontend.py
```

---

## Example Questions

- How is our pipeline looking?
- Show at-risk deals
- What is our weighted forecast?
- Any operational risks?

---

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangGraph
- LangChain
- Groq LLM
- monday.com GraphQL API
- SQLite (checkpointing)

---

## Notes

- Data is fetched live on every query
- Designed for messy real-world business data
- Built within 6-hour assignment constraint

---

**Author:** Saichand Linga
