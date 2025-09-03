from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any, List
import numpy as np

app = FastAPI()

# In-memory log storage
logs: List[str] = []
MAX_LOGS = 1000  # limit memory usage

class LogMessage(BaseModel):
    type: str
    message: Any

# Helper to convert objects to readable strings
def prepare_message(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if hasattr(obj, "tolist"):      # numpy array
        return str(obj.tolist())
    if isinstance(obj, (list, tuple)):
        return str(obj)
    return str(obj)

@app.post("/log")
def log_message(log: LogMessage):
    msg = prepare_message(log.message)
    entry = f"[{log.type}] {msg}"
    logs.append(entry)

    # trim logs to MAX_LOGS
    if len(logs) > MAX_LOGS:
        logs[:] = logs[-MAX_LOGS:]

    print(entry)  # Render dashboard log
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def get_logs():
    html_content = """
    <html>
      <head>
        <title>Trading Logs</title>
        <meta http-equiv="refresh" content="5"> <!-- auto-refresh every 5s -->
        <style>
          body { font-family: monospace; background: #111; color: #eee; padding: 20px; }
          .order { color: #0f0; }
          .candidate_trade { color: #0af; }
          .message { color: #ffa; }
          pre { white-space: pre-wrap; word-wrap: break-word; }
        </style>
      </head>
      <body>
        <h2>Trading Logs (last 100)</h2>
        <pre>
    """

    for line in reversed(logs[-100:]):
        if "[order]" in line:
            html_content += f"<span class='order'>{line}</span>\n"
        elif "[candidate_trade]" in line:
            html_content += f"<span class='candidate_trade'>{line}</span>\n"
        else:
            html_content += f"<span class='message'>{line}</span>\n"

    html_content += "</pre></body></html>"
    return HTMLResponse(content=html_content)
