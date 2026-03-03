# Decision Log -- AI Business Intelligence Agent

## 1. Objective

Build an AI-powered Business Intelligence agent that answers
founder-level queries by integrating live with monday.com boards (Deals
& Work Orders). The system must:

-   Handle messy real-world business data\
-   Provide actionable insights\
-   Show visible tool/action traces\
-   Be deployable as a live prototype

------------------------------------------------------------------------

## 2. Key Architecture Decisions

### LangGraph for Agent Orchestration

**Decision:** Used LangGraph with an explicit tool loop and event
streaming.

**Why:** - Supports structured multi-step reasoning\
- Native tool-calling lifecycle events\
- Enables conversation memory with checkpointing\
- Allows streaming tool trace visibility

**Tradeoff:** - Slightly higher setup complexity vs simple LLM agents

------------------------------------------------------------------------

### Visible Tool / Action Tracing

**Decision:** Implemented real-time tool tracing using LangGraph event
streaming (`astream_events`) and surfaced tool lifecycle states in the
UI.

**Implementation:** - Backend emits structured events: - `tool_start` -
`tool_end` - `assistant_stream` - Frontend displays: - 🔧 Tool name
during execution\
- ✅ Tool completion state\
- Assistant tokens stream live alongside tool trace

**Why:** - Meets explicit requirement for visible tool-call trace\
- Improves transparency and trust\
- Helps debugging and observability\
- Makes reasoning process inspectable

**Tradeoff:** - Requires structured streaming logic\
- Slightly more frontend complexity

------------------------------------------------------------------------

### Live monday.com API Fetch (No Caching)

**Decision:** Fetch live data at query time using monday.com GraphQL
API.

**Why:** - Ensures fresh, real-time business insights\
- Matches assignment requirement for live integration\
- Avoids stale analytics

**Tradeoff:** - Higher latency\
- Increased API usage

**Mitigation:** - Efficient column mapping\
- Pagination limit (500 records)\
- Lightweight normalization pipeline

------------------------------------------------------------------------

### Tool-Based BI Layer

**Decision:** Implemented dedicated BI tools:

-   Pipeline summary\
-   At-risk deals\
-   Weighted revenue forecast\
-   Operational risk analysis

**Why:** - Clear separation between reasoning and analytics\
- Deterministic business calculations\
- Improves reliability over pure LLM reasoning\
- Enables traceable tool invocation

**Tradeoff:** - Requires structured upfront design

------------------------------------------------------------------------

### Data Cleaning & Normalization Layer

**Decision:** Centralized cleaning inside loader layer before tool
usage.

**Steps:** - Standardize column names\
- Normalize status casing\
- Coerce numeric fields safely\
- Parse dates\
- Drop invalid/empty rows

**Why:** - monday.com board data is inconsistent\
- Prevents downstream failures\
- Improves BI accuracy

**Data Quality Handling:** - Graceful handling of nulls\
- Safe numeric coercion\
- Defensive filtering logic

------------------------------------------------------------------------

### Async + SQLite Checkpointing

**Decision:** Use `AsyncSqliteSaver` for thread-level memory
persistence.

**Why:** - Enables follow-up conversational analysis\
- Maintains context across sessions\
- Lightweight and sufficient for prototype\
- Works cleanly with FastAPI async runtime

**Tradeoff:** - Not horizontally scalable (acceptable for prototype
scope)

------------------------------------------------------------------------

### FastAPI Backend + Streamlit Frontend

**Decision:** Separated backend (agent + tools) from frontend (UI).

**Why:** - Production-aligned architecture\
- Backend secures API keys\
- Async streaming supported\
- UI remains lightweight\
- Enables independent deployment

**Tradeoff:** - Slight integration overhead

------------------------------------------------------------------------

### LLM Choice (Groq -- openai/gpt-oss-120b)

**Decision:** Used Groq-hosted model for inference.

**Why:** - Very fast streaming responses\
- Good tool-calling performance\
- Cost-efficient for prototype

**Tradeoff:** - Slight prompt sensitivity

------------------------------------------------------------------------

## 3. Error Handling Strategy

Implemented:

-   HTTP error handling for monday.com API\
-   Safe numeric coercion\
-   Null-safe filtering\
-   Defensive missing-column handling\
-   Streaming-safe error fallback

Planned improvements:

-   Retry with exponential backoff\
-   Schema validation layer\
-   Partial board recovery logic

------------------------------------------------------------------------

## 4. Known Limitations

-   Tools support limited parameterization\
-   Cross-board correlation is basic\
-   Pagination beyond 500 items not implemented\
-   SQLite not production-scale\
-   No semantic caching

These tradeoffs were acceptable within the 6-hour time constraint.

------------------------------------------------------------------------

## 5. Future Improvements

If extended beyond prototype:

-   Parameterized BI queries (date filters, owner filters)\
-   Cross-board impact analysis\
-   Redis-based distributed memory\
-   Observability (OpenTelemetry)\
-   Semantic caching\
-   Fine-grained tool output tracing

------------------------------------------------------------------------

## 6. Why This Design Works for Founders

The system:

-   Provides real-time pipeline visibility\
-   Flags revenue risks\
-   Highlights operational bottlenecks\
-   Shows transparent action/tool traces\
-   Works conversationally over live business data

This directly aligns with founder-level decision-making needs described
in the assignment.

------------------------------------------------------------------------

**End of Decision Log**
