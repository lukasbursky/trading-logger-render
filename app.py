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
        <style>
          body { font-family: monospace; background: #111; color: #eee; padding: 20px; }
          .order { color: #0f0; }
          .candidate_trade { color: #0af; }
          .message { color: #ffa; }
          .invis { color: #111; } 
          pre { white-space: pre-wrap; word-wrap: break-word; margin:0; }
        </style>
      </head>
      <body>
        <h2>Trading Logs (last 100)</h2>
        <pre id="logContainer"><span class='candidate_trade'>_____________________</span>
        </pre>

        <script>
          async function fetchLogs() {
            try {
              const res = await fetch("/logs-json");
              const logs = await res.json();
              const container = document.getElementById("logContainer");
              container.innerHTML = "<span class='invis'>--------------------</span>\\n" + logs.map(line => {
                if (line.includes("[order]")) return "<span class='order'>" + line + "</span>";
                if (line.includes("[candidate_trade]")) return "<span class='candidate_trade'>" + line + "</span>";
                return "<span class='message'>" + line + "</span>";
              }).join("\\n");
            } catch(e) {
              console.error(e);
            }
          }

          fetchLogs();
          setInterval(fetchLogs, 15000); // update every 15 seconds
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/logs-json")
def logs_json():
    # last 100 logs, newest first
    return logs[-100:][::-1]
