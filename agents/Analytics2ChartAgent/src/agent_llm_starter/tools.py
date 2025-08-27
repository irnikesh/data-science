from duckduckgo_search import DDGS
import math

def tool_search(query: str, max_results: int = 5):
    with DDGS() as ddgs:
        results = []
        for r in ddgs.text(query, max_results=max_results):
            results.append({"title": r.get("title",""), "url": r.get("href",""), "snippet": r.get("body","")})
        return results

def tool_calculator(expr: str) -> str:
    # Danger-averse eval: only allow digits, operators, parentheses, decimal points, and spaces.
    allowed = set("0123456789.+-*/() %")
    if not set(expr).issubset(allowed):
        return "Error: unsupported characters."
    try:
        return str(eval(expr, {"__builtins__": {}}, {"math": math}))
    except Exception as e:
        return f"Error: {e}"

# --- New tools: SQL, charting, Miro upload ----------------------------------
import os
import pandas as pd
from sqlalchemy import create_engine, text as sql_text
import matplotlib.pyplot as plt
import requests

def tool_sql(query: str, limit: int | None = None):
    """
    Run a SQL query against a database specified by env var DATABASE_URL (SQLAlchemy).
    Returns a dict with 'columns', 'rows', and a CSV preview path in outputs.
    Example DATABASE_URL: postgresql+psycopg://user:pass@host:5432/dbname
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        # Demo fallback to bundled SQLite database
        url = "sqlite:///data/demo.db"
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            res = conn.execute(sql_text(query))
            rows = res.fetchall()
            cols = res.keys()
        df = pd.DataFrame(rows, columns=cols)
        if limit:
            df = df.head(limit)
        out_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(out_dir, exist_ok=True)
        csv_path = os.path.join(out_dir, "sql_result.csv")
        df.to_csv(csv_path, index=False)
        return {"columns": list(df.columns), "rows": df.to_dict(orient="records"), "csv_path": csv_path}
    except Exception as e:
        return {"error": str(e)}

def tool_chart(table: dict, x: str, y: str, kind: str = "bar", title: str = "Chart", filename: str = "chart.png"):
    """
    Create a simple chart from a table dict like {'columns': [...], 'rows': [{...}, ...]}.
    kind: 'bar' | 'line' | 'scatter'
    Saves PNG to outputs/ and returns the image path.
    """
    try:
        import pandas as _pd
        df = _pd.DataFrame(table.get("rows", []))
        if x not in df.columns or y not in df.columns:
            return {"error": f"Columns not found. Have {list(df.columns)}"}
        out_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, filename)
        plt.figure()
        if kind == "line":
            df.plot(x=x, y=y)
        elif kind == "scatter":
            df.plot(kind="scatter", x=x, y=y)
        else:
            df.plot(kind="bar", x=x, y=y)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(path, dpi=160)
        plt.close()
        return {"image_path": path}
    except Exception as e:
        return {"error": str(e)}

def tool_miro_upload_image(image_path: str, board_id: str | None = None):
    """
    Uploads an image to a Miro board as a board item.
    Requires MIRO_TOKEN env var (OAuth token with board write scopes).
    board_id can be provided or read from MIRO_BOARD_ID env var.
    """
    token = os.getenv("MIRO_TOKEN")
    board = board_id or os.getenv("MIRO_BOARD_ID")
    if not token or not board:
        # Demo mock: write a local record instead of calling Miro
        out_dir = os.path.join(os.getcwd(), "outputs"); os.makedirs(out_dir, exist_ok=True)
        mock = os.path.join(out_dir, "miro_mock.json")
        payload = {"mock": True, "image_path": image_path, "note": "Set MIRO_TOKEN and MIRO_BOARD_ID to upload for real."}
        import json as _json
        open(mock, "w").write(_json.dumps(payload, indent=2))
        return {"ok": True, "mock_file": mock}
    try:
        url = f"https://api.miro.com/v2/boards/{board}/images"
        with open(image_path, "rb") as f:
            files = {"image": (os.path.basename(image_path), f, "image/png")}
            data = {"x": 0, "y": 0}
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=90)
        if resp.status_code >= 300:
            return {"error": f"Miro API error {resp.status_code}: {resp.text}"}
        return {"ok": True, "miro_item": resp.json()}
    except Exception as e:
        return {"error": str(e)}
