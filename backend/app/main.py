try:
    from fastapi import FastAPI
except ImportError as exc:
    raise RuntimeError(
        "FastAPI is required to run SprintFlow API. Install it in the active "
        "Python environment with `python -m pip install fastapi`."
    ) from exc

app = FastAPI(title="SprintFlow API")


@app.get("/health")
def health_check():
    return {"status": "ok", "project": "SprintFlow"}