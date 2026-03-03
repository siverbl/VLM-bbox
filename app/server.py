from __future__ import annotations

import logging
import os

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.config import RuntimeConfig, load_config
from app.pipeline import Qwen2VLBBoxEngine

LOG_LEVEL = os.getenv("BBOX_LOG_LEVEL", "WARNING").upper()
logging.basicConfig(level=LOG_LEVEL)

cfg: RuntimeConfig = load_config()
engine = Qwen2VLBBoxEngine(cfg)
app = FastAPI(title="vlm-bbox", docs_url=None, redoc_url=None, openapi_url=None)


@app.on_event("startup")
def warm_model() -> None:
    engine.warmup()


@app.post("/bbox", response_class=JSONResponse)
async def bbox(file: UploadFile = File(...), query: str = Form(...)):
    image_bytes = await file.read()
    try:
        result, _timing = engine.infer(image_bytes, query)
        return JSONResponse(content=result)
    except Exception:
        return JSONResponse(content=[-1, -1, -1, -1])
