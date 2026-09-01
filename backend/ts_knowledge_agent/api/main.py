from fastapi import FastAPI

app = FastAPI(title="TS Knowledge Agent", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ts-knowledge-agent"}


@app.get("/api/v1/status")
def status() -> dict[str, str]:
    return {"status": "scaffold", "protocol": "ag-ui", "transport": "sse"}
