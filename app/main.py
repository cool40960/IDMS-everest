"""FastAPI 入口（设计稿 §四/§八）。

统一异常处理：各驱动只抛自定义异常（app.core.errors），这里集中翻成
{"error": "..."}，按异常类的 http_status 定状态码。Pydantic 校验错 → 400。
前台只认 {"error": ...} 格式，不接触底层 K8s/Everest 报错。
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api import databases
from app.core.errors import IDMSError

app = FastAPI(title="IDMS 后端", description="统一数据库管理接口（7 引擎）", version="0.1.0")

app.include_router(databases.router)


@app.exception_handler(IDMSError)
async def handle_idms_error(request: Request, exc: IDMSError):
    return JSONResponse(status_code=exc.http_status, content={"error": exc.message})


@app.exception_handler(ValidationError)
async def handle_validation_error(request: Request, exc: ValidationError):
    # 取第一条错误信息，给前台一个可读提示
    errs = exc.errors()
    msg = errs[0]["msg"] if errs else "参数校验失败"
    return JSONResponse(status_code=400, content={"error": msg})


@app.exception_handler(ValueError)
async def handle_value_error(request: Request, exc: ValueError):
    # spec_for 对未知 engine_type 抛 ValueError
    return JSONResponse(status_code=400, content={"error": str(exc)})
