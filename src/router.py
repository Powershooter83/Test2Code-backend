# router.py

from fastapi import APIRouter, Request
from logic import CodeExecutionLogic

router = APIRouter()

@router.get("/languages")
async def get_languages(request: Request):
    logger = request.state.logger
    return CodeExecutionLogic.get_supported_languages(logger)

@router.get("/languages/version/{language}")
async def get_language_versions(language: str, request: Request):
    logger = request.state.logger
    return CodeExecutionLogic.get_language_versions(language, logger)

@router.post("/testcases")
async def upload_testcases(testcases: str, language: str, version: str, request: Request):
    logger = request.state.logger
    result = await CodeExecutionLogic.execute_testcases(testcases, language, version, logger)
    return result
