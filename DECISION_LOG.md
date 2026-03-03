
# Decision Log – AI Business Intelligence Agent

## 1. Objective
Build an AI agent that answers founder-level business intelligence queries by integrating live with monday.com boards for Deals and Work Orders. The system must handle messy data, provide actionable insights, and show visible tool traces.

---

## 2. Key Architecture Decisions

### LangGraph for Agent Orchestration
**Decision:** Used LangGraph with tool loop.

**Why:**
- Supports multi-step reasoning
- Native tool-calling support
- Enables conversational memory with checkpointing
- Production-friendly graph architecture

**Tradeoff:**
- Slightly higher setup complexity vs simple agents

---

### Live monday.com API Fetch (No Caching)
**Decision:** Fetch data at query time using GraphQL API.

**Why:**
- Meets assignment requirement for live data
- Ensures fresh business metrics
- Avoids stale analytics

**Tradeoff:**
- Higher latency
- More API calls

**Mitigation:**
- Efficient column mapping
- Limit=500 pagination

---

### Tool-Based BI Layer
**Decision:** Implemented dedicated BI tools:
- Pipeline summary
- At-risk deals
- Weighted forecast
- Operational risks

**Why:**
- Clear separation of concerns
- Improves LLM reliability
- Easier to extend analytics
- Enables visible action traces

**Tradeoff:**
- Requires more upfront design

---

### Data Cleaning Strategy
**Decision:** Normalize and clean data inside loader layer.

**Steps:**
- Strip column names
- Normalize status casing
- Convert numeric fields
- Parse dates
- Drop empty rows

**Why:**
- monday.com data is inconsistent
- Prevents downstream failures
- Improves BI accuracy

**Data Quality Handling:**
- Coerce invalid numerics
- Handle missing values gracefully

---

### Async + SQLite Checkpointing
**Decision:** Use AsyncSqliteSaver for conversation memory.

**Why:**
- Enables thread persistence
- Supports follow-up questions
- Lightweight local storage
- Works well with FastAPI

**Tradeoff:**
- Not horizontally scalable (acceptable for prototype)

---

### FastAPI Backend + Streamlit Frontend
**Decision:** Separate backend and UI.

**Why:**
- Clean production pattern
- Easier future scaling
- FastAPI handles async well
- Streamlit enables rapid prototyping

**Tradeoff:**
- Slight integration overhead

---

### Groq LLM (openai/gpt-oss-120b)
**Decision:** Use Groq-hosted model.

**Why:**
- Very fast inference
- Good tool-calling support
- Cost-effective for prototype

**Tradeoff:**
- Slight prompt sensitivity

---

## 3. Error Handling Strategy

Implemented:

- HTTP error raising for monday API
- Safe numeric coercion
- Null-safe filtering
- Graceful missing column handling

Planned future improvements:

- Retry with exponential backoff
- Partial board fetch recovery
- Schema validation

---

## 4. Known Limitations

- Tools currently support limited filtering
- Cross-board correlation is basic
- Pagination beyond 500 not implemented
- SQLite not suitable for high scale
- No semantic caching

These were acceptable given the 6-hour constraint.

---

## 5. Future Improvements

If extended beyond prototype:

- Parameterized BI tools
- Sector/time filtering
- Cross-board impact analysis
- Better data quality reporting
- Redis-based memory
- Observability (OpenTelemetry)

---

## 6. Why This Design Works for Founders

The system:

- Provides instant pipeline visibility
- Flags revenue risks
- Highlights operational delays
- Works conversationally
- Uses live business data

This directly addresses the founder use case described in the assignment.

---

**End of Decision Log**
