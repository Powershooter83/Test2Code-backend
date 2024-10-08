from fastapi import APIRouter, Request
import services.container_service 
import services.llm_service

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
async def upload_testcases(request: Request):
    body = await request.json()
    return {
    "id": "chatcmpl-AFohtniAprarbO6GWW57oPoQSZMQ9",
    "object": "chat.completion",
    "created": 1728333201,
    "model": "gpt-4o-mini-2024-07-18",
    "choices": [
        {
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "This is a test! How can I assist you further?",
            "refusal": "null"
        },
        "logprobs": "null",
        "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 13,
        "completion_tokens": 12,
        "total_tokens": 25,
        "prompt_tokens_details": {
        "cached_tokens": 0
        },
        "completion_tokens_details": {
        "reasoning_tokens": 0
        }
    },
    "system_fingerprint": "fp_f85bea6784"
}
