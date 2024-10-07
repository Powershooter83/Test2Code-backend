from fastapi import APIRouter
import services.container_service # import build_and_run_container
import services.llm_service # import generate_code

router = APIRouter()

# Route to get languages
@router.get("/languages")
async def get_languages():
    return ["Python"]

# Route to get language versions
@router.get("/languages/version/{lang}")
async def get_language_versions(lang: str):
    if lang == "Python":
        return {"language": lang, "versions": ["3.11"]}
    return {"error": "Language not found"}, 404

# Route to post test cases
@router.post("/testcases")
async def upload_testcases(testcases: str, lang: str, version: str):
    return {"status": "Test cases uploaded successfully"}

