from fastapi import APIRouter
from logic import CodeExecutionLogic

router = APIRouter()

@router.get("/languages")
async def get_languages():
    return CodeExecutionLogic.get_supported_languages()

@router.get("/languages/version/{lang}")
async def get_language_versions(lang: str):
    return CodeExecutionLogic.get_language_versions(lang)

@router.post("/testcases")
async def upload_testcases(testcases: str, lang: str, version: str):
    result = await CodeExecutionLogic.execute_testcases(testcases, lang, version)
    return result