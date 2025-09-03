# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

logs: List[str] = []  # in-memory log storage

class LogMessage(BaseModel):
    type: str
    message: str

@app.post("/log")
def log_message(log: LogMessage):
    entry = f"[{log.type}] {log.message}"
    logs.append(entry)
    print(entry)  # still visible in Render dashboard
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def get_logs():
    # Show last 100 logs as simple HTML
    html_content = "<h2>Trading Logs</h2><pre style='white-space: pre-wrap;'>"
    html_content += "\n".join(logs[-100:])  # tail of logs
    html_content += "</pre>"
    return HTMLResponse(content=html_content)
