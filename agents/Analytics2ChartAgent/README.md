# Analytical agent

run locally (with [Ollama](https://ollama.com)) or hosted (OpenAI).  
**Analytical Agent workflow (SQL → Chart → Miro)**:
	•	generate SQL from an analytical question,
	•	run it against any DB
	•	turn results into a PNG chart,
	•	and upload that image to a Miro board via the REST API.

---

## Features

- **Agent loop (ReAct style)**: Plan → Act → Observe → Reflect → Answer.
- **LLM adapters**: works with Ollama (`qwen2.5:3b` by default) or OpenAI (`gpt-4o-mini`, etc.).
- **Built-in tools**:
  - 🔎 `search` → DuckDuckGo search
  - ➗ `calculator` → safe arithmetic
  - 🗄 `sql` → run queries against any `DATABASE_URL`
  - 📊 `chart` → generate PNG from SQL results
  - 🎨 `miro_upload_image` → upload chart to a Miro board
- **Output**: clean Markdown reports + saved CSV/PNG artifacts.

---

## ⚡ Quickstart

### 1. Pick a model backend

**Local (recommended):**
```bash
ollama pull qwen2.5:3b
```

**OpenAI (optional):**
```bash
export OPENAI_API_KEY=sk-...
export MODEL=openai/gpt-4o-mini
```

### 2. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure env for analytics
```bash
export DATABASE_URL='postgresql+psycopg://user:pass@host:5432/dbname'   # Any SQLAlchemy URL
export MIRO_TOKEN='your_miro_oauth_token_with_board_write_scope'
export MIRO_BOARD_ID='your_board_id'
```

### 4. Run an analytical task
```bash
python -m src.agent_llm_starter.main --task "Using the orders schema (orders(order_id, order_date, region, sales)), show total sales by region for 2025-Q2. Write SQL, run it, chart region vs total_sales, and upload the chart to Miro."
```

### 5. Inspect outputs
- Tabular results → `outputs/sql_result.csv`
- Chart → `outputs/chart.png`
- Final Markdown report → `outputs/report-*.md`
- Uploaded chart appears in your Miro board 🎉

---

## 📂 Project Layout

```
agent-llm-starter/
├─ src/agent_llm_starter/
│  ├─ agent.py          # Agent loop (ReAct style)
│  ├─ llm.py            # LLM adapters (Ollama, OpenAI)
│  ├─ tools.py          # Tools: search, calculator, sql, chart, miro
│  ├─ prompts.py        # System + tool prompts
│  └─ main.py           # CLI entrypoint
├─ outputs/             # Reports, CSVs, charts
├─ requirements.txt
├─ pyproject.toml
└─ README.md
```

---
## Security notes

- Keep secrets out of code. Use env vars for keys (DB, Miro, OpenAI).  
- SQL execution is powerful — use least-privilege DB credentials.  
- Miro uploads create artifacts on your board; review before sharing.  


---

## 🧪 Demo mode (no external setup)

If you don’t have a database or Miro account ready, you can still try the agent locally.

A small SQLite database (`demo.sqlite`) with a sample `orders` table is included.

### Run demo analytical task
```bash
export DATABASE_URL='sqlite:///demo.sqlite'
python -m src.agent_llm_starter.main --task "Using the orders schema (orders(order_id, order_date, region, sales)), show total sales by region for 2025-Q2. Write SQL, run it, and chart region vs total_sales."
```

This will:
- Query the included SQLite demo DB
- Save results to `outputs/sql_result.csv`
- Create a bar chart at `outputs/chart.png`
- Write a Markdown summary report

> Miro upload is skipped unless you set `MIRO_TOKEN` + `MIRO_BOARD_ID`.

---

## Zero-Setup Demo

You can run the analytical workflow **with no external services** thanks to a bundled SQLite DB and a Miro uploader **mock**.

```bash
# 1) (Optional) choose your model
ollama pull qwen2.5:3b    # or set MODEL=openai/gpt-4o-mini with OPENAI_API_KEY

# 2) Install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3) Run the demo task (uses data/demo.db automatically)
python -m src.agent_llm_starter.main --task "Using the orders schema (orders(order_id, order_date, region, sales)), show total sales by region for 2025-Q2. Write SQL, run it, chart region vs total_sales, and upload the chart."
```

What happens:
- `sql(...)` **auto-falls back** to `sqlite:///data/demo.db` if `DATABASE_URL` is unset.
- `chart(...)` writes `outputs/chart.png`.
- `miro_upload_image(...)` writes `outputs/miro_mock.json` when `MIRO_TOKEN/MIRO_BOARD_ID` are unset.
- A final Markdown report is saved in `outputs/`.
