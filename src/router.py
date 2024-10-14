# router.py

from fastapi import APIRouter
from logic import CodeExecutionLogic

router = APIRouter()

@router.get("/languages")
async def get_languages():
    return CodeExecutionLogic.get_supported_languages()

@router.get("/languages/version/{language}")
async def get_language_versions(language: str):
    return CodeExecutionLogic.get_language_versions(language)

@router.post("/testcases")
async def upload_testcases(testcases: str, language: str, version: str):
    result = await CodeExecutionLogic.execute_testcases(testcases, language, version)
    return result